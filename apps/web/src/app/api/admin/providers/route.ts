export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export async function GET(request: Request) {
  const authorization = request.headers.get("Authorization");
  if (!authorization || authorization.length > 512 || !authorization.startsWith("Bearer "))
    return Response.json({ error: "Administrator access is required." }, { status: 401 });
  try {
    const response = await fetch(new URL("/internal/provider-status", process.env.API_INTERNAL_URL || "http://127.0.0.1:8000"), {
      headers: { Authorization: authorization }, cache: "no-store", redirect: "error", signal: AbortSignal.timeout(10000),
    });
    return new Response(response.body, { status: response.status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
  } catch {
    return Response.json({ error: "Provider administration is unavailable." }, { status: 503 });
  }
}
