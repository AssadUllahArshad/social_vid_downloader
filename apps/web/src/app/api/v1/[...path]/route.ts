export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type Context = { params: Promise<{ path: string[] }> };
function failure(code: string, message: string, status: number) {
  return Response.json(
    { success: false, error: { code, message } },
    { status, headers: { "Cache-Control": "no-store" } },
  );
}
async function proxy(request: Request, context: Context) {
  const { path } = await context.params;
  const operation = path.join("/");
  const allowed =
    request.method === "GET"
      ? /^(capabilities|(?:jobs|files|thumbnail)\/[a-f0-9]{32})$/
      : /^(extract|download)$/;
  if (!allowed.test(operation))
    return failure("not_found", "This API operation is unavailable.", 404);
  let body: string | undefined;
  if (request.method === "POST") {
    const reader = request.body?.getReader();
    const chunks: Uint8Array[] = [];
    let size = 0;
    if (reader) {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        size += value.byteLength;
        if (size > 8192) {
          await reader.cancel();
          return failure(
            "payload_too_large",
            "This request is too large.",
            413,
          );
        }
        chunks.push(value);
      }
    }
    body = Buffer.concat(chunks).toString("utf8");
  }
  try {
    // Set only behind a private ingress that overwrites this header. Never
    // forward arbitrary X-Forwarded-For supplied by a public client.
    const identityHeader = process.env.TRUSTED_CLIENT_IP_HEADER;
    const identity = identityHeader ? request.headers.get(identityHeader) : null;
    const { isIP } = await import("node:net");
    const base = process.env.API_INTERNAL_URL || "http://127.0.0.1:8000";
    const response = await fetch(
      new URL(
        `/api/v1/${operation}${new URL(request.url).searchParams.get("inline") === "1" && operation.startsWith("files/") ? "?inline=1" : ""}`,
        base,
      ),
      {
        method: request.method,
        headers: {
          "Content-Type": "application/json",
          ...(identity && isIP(identity) ? { "X-Forwarded-For": identity } : {}),
          ...(request.headers.get("range") &&
          /^bytes=(\d+-\d*|-\d+)$/.test(request.headers.get("range")!)
            ? { Range: request.headers.get("range")! }
            : {}),
        },
        body,
        cache: "no-store",
        redirect: "error",
        signal: AbortSignal.any([
          request.signal,
          AbortSignal.timeout(operation.startsWith("files/") ? 600000 : 100000),
        ]),
      },
    );
    const headers = new Headers({
      "Content-Type":
        response.headers.get("Content-Type") || "application/json",
      "Cache-Control": "no-store",
    });
    for (const name of [
      "Content-Disposition",
      "Content-Length",
      "Content-Range",
      "Accept-Ranges",
    ]) {
      const value = response.headers.get(name);
      if (value) headers.set(name, value);
    }
    const retry = response.headers.get("Retry-After");
    if (retry) headers.set("Retry-After", retry);
    return new Response(response.body, { status: response.status, headers });
  } catch {
    return failure(
      "service_unavailable",
      "The video service is currently unavailable. Please try again later.",
      503,
    );
  }
}
export const POST = proxy;
export const GET = proxy;
