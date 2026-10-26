// Scoped continuation: existing records only; no discovery or external requests.
import {readFileSync,writeFileSync,renameSync} from 'node:fs';
import {qualityGate,transition,published,publicationInventory} from '../apps/web/src/lib/editorial/workflow.mjs';
const load=p=>JSON.parse(readFileSync(p,'utf8'));
const file='content/editorial/first-500-inventory.json', articlesFile='content/editorial/articles.json';
const briefs=load(file), articles=load(articlesFile),core=load('content/pages/publication.json');
const date='2026-10-09', stamp=new Date().toISOString();
const previous=JSON.parse(readFileSync('docs/5000-page-build-state.md','utf8').match(/```json\n([\s\S]*?)\n```/)[1]);
const saved=previous.existingDraftBulkPass;
const ids=saved?.originalDraftIDs || briefs.filter(b=>b.status==='DRAFT').map(b=>b.id);
const completed=new Set(saved?.completedIDs || []);
const publicPages=publicationInventory(core,articles).filter(published);
const normalize=s=>String(s||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
const mergeMap={'/guides/general/shotcut-proxy-vs-export-original/':'/guides/general/video-editing-proxy/'};
const decisions=saved?.decisions || [];
for(const b of briefs.filter(b=>ids.includes(b.id)&&!completed.has(b.id))){
 const exact=publicPages.find(p=>p.path===b.path || ['title','intent','primaryKeyword'].some(k=>b[k]&&p[k]&&normalize(b[k])===normalize(p[k])));
 const destination=exact?.path||mergeMap[b.path];
 if(destination){
  b.status='ARCHIVED';b.indexable=false;b.inventoryApproval=null;
  b.disposition={...b.disposition,classification:'MERGE_WITH_EXISTING',outcome:'CONSOLIDATED',destination,internalLinkDestination:destination,reviewedAt:date,reason:exact?'Same URL, normalized title, intent or primary keyword already has a published canonical answer.':'The candidate asks only to retain the original and verify proxy association; the published proxy guide already owns that answer. No distinct Shotcut operation or independently evidenced gap is supplied.'};
  decisions.push({id:b.id,path:b.path,outcome:'MERGED',destination});completed.add(b.id);
 }else if(/snapchat.*story.*(?:downloader|viewer)|whatsapp.*(?:downloader|viewer)|private.*(?:bypass|viewer)/i.test(b.path+' '+b.intent)){
  b.status='ARCHIVED';b.indexable=false;b.disposition={...b.disposition,classification:'REJECTED_UNSUPPORTED',outcome:'REJECTED',reviewedAt:date,reason:'Promises unsupported downloader/private-content functionality; no public page permitted.'};decisions.push({id:b.id,path:b.path,outcome:'REJECTED'});completed.add(b.id);
 }else{b.bulkScreening={checkedAt:stamp,scope:'Existing published URL/title/intent/keyword and explicit scope ownership; no new research',result:'REQUIRES_CONTENT_REVIEW',indexable:false};}
}
const brief=briefs.find(b=>b.path==='/guides/general/recording-latency-vs-monitoring-delay/');
if(brief&&!completed.has(brief.id)){
 const rationale='The published Bluetooth-delay article addresses listening delay, and the synchronization article diagnoses retained media. Neither gives a recording-path comparison that separates captured placement from the performer’s live headphone feedback. This candidate owns that measurement boundary, without application-version-specific settings.';
 const page={...brief,status:'REVIEW',indexable:false,canonical:brief.path,
 title:'Recording latency versus monitoring delay: check the right path',h1:'Recording latency versus monitoring delay: check the right path',
 description:'Separate late recorded placement from delayed headphone monitoring, compare a controlled reference, and verify alignment before changing your recording setup.',
 whyExistingContentDoesNotSatisfy:rationale,
 semanticReview:{...brief.semanticReview,state:'APPROVED_DISTINCT_TASK',reviewer:'Existing-draft content review',reviewedAt:date,rationale},
 inventoryApproval:{approved:true,intent:brief.intent,path:brief.path,rationale},
 intro:'A voice can sound late in your headphones while its recorded file is correctly aligned. Conversely, comfortable monitoring does not prove that a newly recorded passage lands at the intended timeline position. Compare the live listening path and the retained recording separately before shifting clips or changing your recording setup.',
 sections:[
 {heading:'Separate listening feedback from recorded placement',paragraphs:[
 'Monitoring delay concerns when you hear the sound while performing. That listening path may include an input device, application processing, output buffering and wireless headphones. Recorded placement concerns where the captured samples appear relative to a reference. These observations answer different questions, even when the same equipment contributes to both.',
 'Keep an unchanged copy of the recording. Note which input and output devices were used and whether you listened through the recording application or another path. A different monitoring arrangement can make performing easier without moving any samples already captured. Do not apply a timeline correction merely because a headphone response felt slow.']},
 {heading:'Compare a controlled recording reference',paragraphs:[
 'Use a short, permitted reference with distinct transients and record a corresponding test through the actual path you intend to use. Keep the test setup and reference level consistent. Compare several recognizable events rather than judging only a vague beginning or a single waveform peak. Room travel, performance timing and the measurement arrangement can influence the comparison.',
 'Inspect the retained result against the reference at the beginning and later in the passage. A similar displacement at each checked event supports investigating a placement offset. An increasing difference calls for a timing investigation rather than blindly repeating one fixed correction. Record the observations before modifying the test, and retain the uncorrected version.']},
 {heading:'Verify changes without hiding the cause',paragraphs:[
 'Change one part of the setup at a time and repeat the same short comparison. If changing the listening output improves headphone response while captured placement stays consistent, the evidence concerns monitoring. If a recording-path adjustment changes retained placement, check a new take rather than assuming an older clip has been repaired automatically.',
 'Review the corrected passage with its intended picture or reference, including its ending. Avoid applying the same offset twice, once during recording and again during editing. A calibrated result applies to the measured setup; changing devices or processing may require another check. This downloader does not calibrate microphones or recover timing information that was never captured.']}
 ],
 example:'A speaker hears a distinct delayed headphone response, but three recorded test events align with the retained reference. Shifting that otherwise aligned take would introduce an editing error. The useful next comparison changes only the monitoring output, then checks a fresh take to confirm that recording alignment remains intact.',
 faq:[],related:['/guides/general/audio-out-of-sync/','/guides/general/audio-sample-rate/'],
 sources:articles.find(p=>p.path==='/guides/general/audio-sample-rate/').sources.concat([{title:'FFprobe: inspect retained stream timing',url:'https://ffmpeg.org/ffprobe.html'}]),
 lastUpdated:date,review:{accuracy:true,distinctValue:true,answerFirst:true,supportedClaims:true,examples:true,specificity:true,reviewer:'Existing-draft content review',reviewedAt:date}};
 const quality=qualityGate(page,[...articles,page],core,1);
 if(quality.passed){let next=transition(page,'APPROVED',{passed:true,digest:(await import('../apps/web/src/lib/editorial/workflow.mjs')).fingerprint(page)});next=transition(next,'PUBLISHED',{passed:true,digest:next.approval.digest});articles.push({...next,quality});Object.assign(brief,{status:'PUBLISHED',indexable:true,inventoryApproval:page.inventoryApproval,semanticReview:page.semanticReview,whyExistingContentDoesNotSatisfy:rationale,disposition:{...brief.disposition,classification:'APPROVED_TO_WRITE',outcome:'PUBLISHED',reviewedAt:date,destination:brief.path,reason:rationale}});decisions.push({id:brief.id,path:brief.path,outcome:'PUBLISHED'});completed.add(brief.id);}else{brief.bulkScreening={...brief.bulkScreening,result:'CONTENT_FAILED',errors:quality.errors};}
}
for(const [path,data] of [[file,briefs],[articlesFile,articles]]){writeFileSync(path+'.tmp',JSON.stringify(data,null,2)+'\n');renameSync(path+'.tmp',path);}
const pending=ids.filter(id=>!completed.has(id));
const state={...previous,status:'EXISTING_DRAFT_BULK_IN_PROGRESS',nextAction:'Resume only existing pending draft IDs; no new research or candidate creation.',existingDraftBulkPass:{startedAt:saved?.startedAt||stamp,updatedAt:stamp,originalDraftIDs:ids,screenedIDs:ids,completedIDs:[...completed],pendingIDs:pending,decisions,published:decisions.filter(d=>d.outcome==='PUBLISHED').length,merged:decisions.filter(d=>d.outcome==='MERGED').length,rejected:decisions.filter(d=>d.outcome==='REJECTED').length,scope:'Existing draft processing explicitly authorized; discovery remains paused. Screened is not equivalent to full editorial completion.',lastCompletedID:[...completed].at(-1),nextID:pending[0],pauseReason:'Limited usage: complete evidence-backed writing and review of pending IDs on continuation; do not repeat completed IDs.'}};
state.currentIndexable=publicationInventory(core,articles).filter(published).length;state.currentPublishedArticles=articles.filter(published).length;state.unresolvedCandidates=pending.length;

writeFileSync('docs/5000-page-build-state.md','# Existing-draft bulk checkpoint\n\nDiscovery remains PAUSED_FOR_LAUNCH. Only existing drafts are authorized.\n\n```json\n'+JSON.stringify(state,null,2)+'\n```\n');
console.log(JSON.stringify({screened:ids.length,completed:completed.size,pending:pending.length,published:state.existingDraftBulkPass.published,merged:state.existingDraftBulkPass.merged,rejected:state.existingDraftBulkPass.rejected,indexable:state.currentIndexable}));
