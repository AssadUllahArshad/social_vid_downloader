import { isIP } from 'node:net';
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
type Context = {params:Promise<{path:string[]}>};
function error(status:number,code:string) { return Response.json({error:{code,message:status===413?'This request exceeds the allowed size.':'File processing is unavailable. Please try again.'}},{status,headers:{'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}}); }
async function proxy(request:Request,{params}:Context) {
 const operation=(await params).path.join('/');
 const allowed=request.method==='GET'?/^(capabilities|(?:jobs|files)\/[a-f0-9]{32})$/:/^(uploads|jobs|jobs\/[a-f0-9]{32}\/cancel)$/;
 if(!allowed.test(operation))return error(404,'operation_unavailable');
 const upload=operation==='uploads';const configured=Number(process.env.PROCESSING_MAX_UPLOAD_BYTES||209715200);
 const uploadLimit=Number.isSafeInteger(configured)&&configured>0?Math.min(configured,209715200):209715200;
 const limit=upload?(Number.isSafeInteger(configured)&&configured>0?Math.min(configured,209715200):209715200):8192;
 if(Number(request.headers.get('content-length')||0)>limit)return error(413,'file_too_large');
 const origin=request.headers.get('origin');
 // Browser writes are same-origin only, independent of CORS configuration.
 const allowedOrigins=new Set([process.env.NEXT_PUBLIC_SITE_URL||'https://socialviddownloader.com']);
 const host=request.headers.get('host')||'';if(/^(127\.0\.0\.1|localhost)(:\d+)?$/.test(host))allowedOrigins.add(`http://${host}`);
 if(request.method==='POST'&&origin&&!allowedOrigins.has(origin))return error(403,'invalid_origin');
 let size=0;let exceeded=false;
 const body=request.method==='POST'&&request.body?request.body.pipeThrough(new TransformStream<Uint8Array,Uint8Array>({transform(chunk,controller){size+=chunk.byteLength;if(size>limit){exceeded=true;controller.error(new Error('limit'));return;}controller.enqueue(chunk);}})):undefined;
 const headers=new Headers({'Content-Type':upload?'application/octet-stream':'application/json'});
 const identityHeader=process.env.TRUSTED_CLIENT_IP_HEADER;const identity=identityHeader?request.headers.get(identityHeader):null;
 if(identity&&isIP(identity))headers.set('X-Forwarded-For',identity);
 const range=request.headers.get('range');if(range&&/^bytes=(\d+-\d*|-\d+)$/.test(range))headers.set('Range',range);
 try {
  const response=await fetch(new URL(`/processing/${operation}`,process.env.API_INTERNAL_URL||'http://127.0.0.1:8000'),{method:request.method,headers,body,duplex:'half',redirect:'error',cache:'no-store',signal:AbortSignal.any([request.signal,AbortSignal.timeout(operation.startsWith('files/')?600000:200000)])} as RequestInit&{duplex:'half'});
  const outputHeaders=new Headers({'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});
  for(const key of ['Content-Type','Content-Length','Content-Disposition','Content-Range','Accept-Ranges','Retry-After']){const value=response.headers.get(key);if(value)outputHeaders.set(key,value);}
  // Backend capability URLs are private. Only JSON gets normalized; media stays streamed.
  if(!operation.startsWith('files/') && response.headers.get('content-type')?.includes('application/json')) {
   const data=await response.json();if(operation==='capabilities'&&typeof data.maxInputBytes==='number')data.maxInputBytes=Math.min(data.maxInputBytes,uploadLimit);for(const key of ['statusUrl','downloadUrl'])if(typeof data[key]==='string'&&/^\/processing\/(?:jobs|files)\/[a-f0-9]{32}$/.test(data[key]))data[key]=data[key].replace('/processing/','/api/processing/')+'/';
   outputHeaders.delete("Content-Length");
   return Response.json(data,{status:response.status,headers:outputHeaders});
  }
  return new Response(response.body,{status:response.status,headers:outputHeaders});
 }catch{return error(exceeded?413:503,exceeded?'file_too_large':'service_unavailable');}
}
export const GET=proxy;
export const POST=proxy;
