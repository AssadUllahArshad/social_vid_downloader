import argparse,json,time,uuid,tempfile,urllib.request,urllib.error,concurrent.futures,subprocess
from pathlib import Path
from datetime import datetime,timezone
parser=argparse.ArgumentParser(description='Verify authorized public URLs; client copies are temporary. Server copies expire by TTL.')
parser.add_argument('--origin',default='http://127.0.0.1:3000')
for name in ['youtube','facebook','instagram','tiktok','snapchat']:
 parser.add_argument('--'+name,action='append',default=[])
args=parser.parse_args()
origin=args.origin.rstrip('/')
if not origin.startswith(('https://','http://')):parser.error('Origin must use HTTP/HTTPS')
samples=[(platform,platform,None,url) for platform in ['youtube','facebook','instagram','tiktok','snapchat'] for url in getattr(args,platform)]
if not samples:parser.error('Provide at least one authorized public URL')
def get(path,payload=None):
 req=urllib.request.Request(origin+path,data=json.dumps(payload).encode() if payload is not None else None,headers={'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=110) as res:return res.status,res.read(),dict(res.headers)
 except urllib.error.HTTPError as e:return e.code,e.read(),dict(e.headers)
def check(sample):
 tool,platform,kind,url=sample;start=time.monotonic();row=dict(tool=tool,platform=platform,contentType=kind,url=url,checkedAt=datetime.now(timezone.utc).isoformat(),status='FAIL')
 try:
  status,body,_=get('/api/v1/extract/',{'url':url,'platform':platform});data=json.loads(body)
  if status!=200 or not data.get('success'):row.update(stage='extraction',httpStatus=status,error=data.get('error'));return row
  row.update(title=data.get('title'),creator=data.get('creator'),duration=data.get('duration'),formatCount=len(data.get('formats',[])),audioTracks=data.get('audio_tracks',[]))
  if data.get('thumbnail'):
   st,thumbnail,headers=get(data['thumbnail']);row['thumbnail']=dict(status=st,bytes=len(thumbnail),contentType=headers.get('Content-Type'));assert st==200 and len(thumbnail)>0
  formats=data['formats'];fmt=min(formats,key=lambda f:(f.get('height') or 100000,f.get('filesize') or 0));row['selectedFormat']=fmt
  status,body,_=get('/api/v1/download/',{'sessionId':data['sessionId'],'formatId':fmt['id']});job=json.loads(body)
  if status!=202:row.update(stage='preparation',httpStatus=status,error=job.get('error'));return row
  deadline=time.monotonic()+210
  while time.monotonic()<deadline:
   status,body,_=get(job['statusUrl']);ready=json.loads(body)
   if ready.get('status') in ['ready','error']:break
   time.sleep(2)
  if ready.get('status')!='ready':row.update(stage='preparation',error=ready.get('error'),jobStatus=ready.get('status'));return row
  status,body,_=get(ready['downloadUrl']);assert status==200
  tmp=Path(tempfile.gettempdir()) / ('svd-smoke-'+uuid.uuid4().hex+'.'+ready['extension']);tmp.write_bytes(body)
  try:
   probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(tmp)],timeout=15));streams=probe['streams'];assert any(s['codec_type']=='video' for s in streams);assert len(body)==ready['filesize'];video=next(s for s in streams if s['codec_type']=='video');assert video['height']==fmt['height'];assert video['width']==fmt['width']
   row.update(status='PASS',stage='verified_file',bytes=len(body),reportedBytes=ready['filesize'],streams=[{k:s.get(k) for k in ['codec_type','codec_name','width','height','tags','disposition']} for s in streams],probedDuration=probe['format'].get('duration'))
  finally:tmp.unlink(missing_ok=True)
 except Exception as exc:row.update(stage='verification_or_transport',errorCategory=type(exc).__name__,reason="Verification or transport failed; inspect private server diagnostics.")
 finally:row['durationSeconds']=round(time.monotonic()-start,2);print(json.dumps({k:row.get(k) for k in ['tool','status','stage','httpStatus','error','bytes','durationSeconds']}),flush=True)
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(check,samples))
print(json.dumps({'sampleCount':len(rows),'results':rows},indent=2))
raise SystemExit(0 if all(row['status']=='PASS' for row in rows) else 1)
