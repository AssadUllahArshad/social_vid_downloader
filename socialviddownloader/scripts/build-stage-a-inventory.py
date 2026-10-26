"""Bulk intent discovery into the existing registry; never authors or publishes.

Seed tasks are hypotheses, not approved search demand or researched answers.
Exact duplicates and explicitly reviewed scope overlaps are consolidated.
Other candidates retain DRAFT/NOINDEX until primary evidence and full-answer
review justify writing. Re-running preserves stable IDs and all decisions.
"""
import json,re
from collections import Counter
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo


from pathlib import Path as _GenerationPath
import json as _generation_json
_control = _GenerationPath(__file__).resolve().parents[1] / "content/editorial/generation-control.json"
if _control.exists() and _generation_json.loads(_control.read_text()).get("status") == "PAUSED_FOR_LAUNCH":
    raise SystemExit("Content generation is PAUSED_FOR_LAUNCH. Resume only after an explicit user instruction.")

REGISTRY=Path('content/editorial/first-500-inventory.json')
SEEDS=Path('content/editorial/stage-a-intent-seeds.tsv')
DATE=datetime.now(ZoneInfo('Asia/Karachi')).date().isoformat()
BATCH='expansion-stage-a-2026-10-08'
rows=json.loads(REGISTRY.read_text())
articles=json.loads(Path('content/editorial/articles.json').read_text())
core=json.loads(Path('content/pages/publication.json').read_text())
by_path={r['path']:r for r in rows}
# Explicit answer ownership, not an automatic lexical-match publication decision.
merges={
 'audio-edit-zero-crossing-stereo-limits':('audio-click-at-edit-boundary','Existing complete seam-click answer explicitly owns zero-crossing adjustment and different stereo crossing positions.'),
 'audio-metadata-language-tag-handoff':('missing-source-language','Existing stream-language identification owns labels versus actual listening and keeping uncertainty explicit.'),
 'subtitle-language-vs-region-tags':('subtitle-language-vs-audio-language','Keep regional caption identity as a secondary clarification of the existing language-choice task rather than another language-label landing.'),
 'blur-mask-vs-audio-identification':('tracked-video-blur-handoff-review','Existing complete blur answer already distinguishes coverage from anonymity and other identifying context.'),
 'embedded-location-vs-visible-location':('inspect-video-metadata-before-sharing','Existing metadata privacy answer owns embedded fields versus identifying visible content; enrich that answer if new source evidence supports it.'),
 'video-export-naming-version-identity':('archive-source-vs-edit','Existing version-lineage answer owns identifiable parents and derivatives; another final-filename label does not create a separate task.'),
 'video-archive-integrity-vs-playability':('archive-checksums','Existing checksum answer explicitly separates byte identity from playable or trustworthy media.'),
 'video-archive-external-sidecar-inventory':('archive-manifest','Existing source manifest owns associated artifacts and missing context; consolidate sidecar inventory into that record.'),
 'archive-permission-source-evidence':('archive-manifest','Existing manifest owns source version and permission evidence association; avoid a second manifest page.'),
 'watermark-attribution-vs-license':('public-url-vs-permission','Existing public-access/permission answer owns credit versus rights; a visible attribution variant should strengthen it.'),
 'participant-consent-vs-upload-ownership':('video-permission-request','Existing permission-request answer owns actual authorized uses and unresolved approval scope; do not publish a legal-advice permutation.'),
 'music-license-scope-edited-video':('video-permission-request','Existing permission scope task owns edits and redistribution; consolidate the music-use example without making legal conclusions.'),
 'premiere-transparent-black-preview':('video-alpha-channel-handoff','Existing complete alpha handoff answer owns receiver/background verification; one editor preview variation is not a new intent.'),
 'webm-alpha-receiver-support':('video-alpha-channel-handoff','Container-specific receiver details belong in the existing actual-alpha handoff answer unless future evidence shows a distinct task.'),
 'obs-scene-source-vs-retained-asset':('archive-source-vs-edit','Generic external-resource retention is already owned; do not approve another project-versus-file page solely by renaming the application.'),
}
FAMILIES={'creator':'CRT','audio':'AUD','captions':'CAP','formats':'FMT','codecs':'COD','glossary':'GLS','device':'DEV','browser':'BRW','platform-help':'PLT','copyright':'PRV','troubleshooting':'TRB','faq':'FAQ','comparison':'CMP'}
TOOLS={'general':'/youtube-video-downloader/','youtube':'/youtube-video-downloader/','facebook':'/facebook-video-downloader/','instagram':'/instagram-video-downloader/','tiktok':'/tiktok-video-downloader/','snapchat':'/snapchat-spotlight-downloader/','whatsapp':None}
HUBS={'general':'/guides/','youtube':'/youtube/','facebook':'/facebook/','instagram':'/instagram/','tiktok':'/tiktok/','snapchat':'/snapchat-downloader/','whatsapp':'/guides/'}
def suggested_tool(platform, slug):
 if platform=='youtube' and ('youtube-short-' in slug or 'youtube-shorts-' in slug):return '/youtube-shorts-downloader/'
 if platform=='facebook' and 'reel' in slug:return '/facebook-reels-downloader/'
 if platform=='instagram' and 'reel' in slug:return '/instagram-reels-downloader/'
 return TOOLS[platform]
def words(text):
 text=re.sub(r'\b(subtitles?|captions?)\b','texttrack',text.lower())
 return set(re.findall(r'[a-z0-9]{3,}',text))-{'the','and','for','with','video','your','from','into','versus','actual','retained','check','verify'}
def similarity(a,b):
 x,y=words(a),words(b)
 return len(x&y)/len(x|y) if x|y else 0
published=[r for r in articles if r.get('status')=='PUBLISHED' and r.get('indexable')]
counts=Counter((r['platform'],r['family']) for r in rows if r.get('batch')==BATCH)
added=[];skipped=0
for line in SEEDS.read_text().splitlines():
 if not line.strip() or line.startswith('#'):continue
 platform,family,slug,title,task=[x.strip() for x in line.split('|')]
 assert platform in TOOLS and family in FAMILIES
 assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug)
 path=f'/guides/{platform}/{slug}/'
 if path in by_path:skipped+=1;continue
 assert not re.search(r'snapchat.*stor(y|ies)|private.*bypass|whatsapp.*downloader',path)
 counts[platform,family]+=1
 identifier=f'SVD-A-{platform.upper()[:3]}-{FAMILIES[family]}-{counts[platform,family]:04d}'
 assert not any(r.get('id')==identifier for r in rows)
 # Primary answer text is compared for shortlist discovery, not full peer review.
 pool=[]
 for a in published:
  answer=' '.join([a.get('intro','')]+[s['heading'] for s in a.get('sections',[])])
  score=similarity(title+' '+task,a['title']+' '+answer)
  pool.append((score,a['path']))
 closest=[p for _,p in sorted(pool,reverse=True)[:3]]
 gap=('Inventory-stage hypothesis: '+task+' Current answer-map shortlist: '+', '.join(closest)+'. Full peer bodies, other drafts and primary evidence must confirm this narrower task before writing; no distinct-intent approval or observed SERP equivalence is claimed.')
 merged=merges.get(slug)
 if merged:
  destination='/guides/general/'+merged[0]+'/'
  assert any(a['path']==destination for a in published)
 else:destination=path
 reason=merged[1] if merged else gap
 r={'id':identifier,'batch':BATCH,'path':path,'canonical':path,'platform':platform,'family':family,'cluster':family,'title':title,'h1':title,'description':task.rstrip('.')+'.','primaryKeyword':title,'primaryTopic':task,'secondaryKeywords':[slug.replace('-',' ')],'intent':'task:'+slug,'targetUser':'A viewer or authorized creator completing this specific media task.','userProblem':title,'userBenefit':task,'whyExistingContentDoesNotSatisfy':gap,'closestExistingPages':closest,'semanticReview':{'state':'MERGED_EXISTING_TASK' if merged else 'GAP_IDENTIFIED_RESEARCH_PENDING','comparisons':closest,'rationale':reason,'reviewer':'Inventory-stage scope consolidation' if merged else None,'reviewedAt':DATE,'expectedSERP':'Unmeasured; no search volume, difficulty or SERP-equivalence claim.','screeningMethod':'Answer-map and task shortlist; neither writing approval nor a substitute for complete peer/source review.'},'priority':2,'targetDownloader':suggested_tool(platform,slug),'hub':HUBS[platform],'internalLinkParent':f'/topics/{family}/','related':closest,'suggestedInternalLinks':closest,'status':'ARCHIVED' if merged else 'DRAFT','indexable':False,'inventoryApproval':None,'qualityResult':'NOT_RUN_NONPUBLIC_INVENTORY','disposition':{'classification':'MERGE_WITH_EXISTING' if merged else 'NEEDS_RESEARCH','destination':destination,'internalLinkDestination':destination if merged else closest[0],'reason':reason,'reviewedAt':DATE,'targetUser':'An authorized creator or viewer handling the specified media task.','primaryQuestion':title,'outcome':'CONSOLIDATED' if merged else 'RESEARCH_REQUIRED'}}
 if platform=='whatsapp':r['contentRole']='education'
 rows.append(r);by_path[path]=r;added.append(identifier)
REGISTRY.write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps({'created':len(added),'alreadyRegistered':skipped,'registryRecords':len(rows),'stageARecords':sum(r.get('batch')==BATCH for r in rows),'newIDs':added},indent=2))
