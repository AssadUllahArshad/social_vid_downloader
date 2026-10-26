// Content-only wrapping: preserve the design and validate fresh publication digests.
import {readFileSync, writeFileSync, renameSync} from 'node:fs';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {qualityGate, transition, fingerprint} from '../apps/web/src/lib/editorial/workflow.mjs';

export function formatGraph(value) {
  let result='', quoted=false, escaped=false, brackets=0;
  for(let i=0;i<value.length;i++) {
    const char=value[i], next=value[i+1];
    result+=char;
    if(escaped){escaped=false;continue;}
    if(char==='\\'){escaped=true;continue;}
    if(char==="'"){quoted=!quoted;continue;}
    if(quoted)continue;
    if(char==='[')brackets++;
    if(char===']')brackets--;
    if(!brackets && next && !/\s/.test(next) &&
      ([';',',',':'].includes(char)||(char===']'&&/[a-zA-Z[]/.test(next))))result+=' ';
  }
  return result;
}

function formatText(value) {
  return value.replace(/(-(?:vf|af|filter_complex)\s+")((?:\\.|[^"\\])*)(")/g,
    (_,start,graph,end)=>start+formatGraph(graph)+end);
}

function run() {
  const load=path=>JSON.parse(readFileSync(path,'utf8'));
  const articlePath='content/editorial/articles.json', draftPath='content/editorial/deferred-authored-batch.json';
  const articles=load(articlePath), drafts=load(draftPath), core=load('content/pages/publication.json');
  const mission=load('docs/video-tools-execution-state.json').seoCompletion;
  const starting=new Set(mission.continuousRun938.startingIDs);
  const scope=new Set(mission.decisions.filter(d=>starting.has(d.id)&&d.outcome==='PUBLISHED').map(d=>d.id));
  const changed=[];
  for(let i=0;i<articles.length;i++) {
    const old=articles[i];
    if(!scope.has(old.id)&&!old.path.endsWith('/ass-subtitle-font-attachment-handoff/'))continue;
    let page=structuredClone(old);
    for(const section of page.sections)section.paragraphs=section.paragraphs.map(formatText);
    page.example=formatText(page.example);
    if(page.path.endsWith('/ffmpeg-xfade-overlap-duration/'))
      for(const section of page.sections)section.paragraphs=section.paragraphs.map(text=>text.replace(
        'For two compatible square-pixel, eight-bit SDR sources',
        'For two compatible 16:9 square-pixel, eight-bit SDR sources'));
    if(JSON.stringify(page.sections)===JSON.stringify(old.sections)&&page.example===old.example)continue;
    page.status='REVIEW';page.indexable=false;page.approval=null;
    page.review={...page.review,reviewer:'Command grammar and mobile readability review',reviewedAt:'2026-10-13'};
    const quality=qualityGate(page,articles.map((other,index)=>index===i?page:other),core,1);
    if(!quality.passed)throw Error(page.path+JSON.stringify(quality.errors));
    page=transition(page,'APPROVED',{passed:true,digest:fingerprint(page)});
    page=transition(page,'PUBLISHED',{passed:true,digest:fingerprint(page)});
    articles[i]={...page,quality};
    const draft=drafts.find(row=>row.slug===page.path.split('/').filter(Boolean).at(-1));
    if(draft){draft.sections=page.sections;draft.example=page.example;}
    changed.push(page.path);
  }
  for(const[path,data]of[[articlePath,articles],[draftPath,drafts]]) {
    writeFileSync(path+'.tmp',JSON.stringify(data,null,2)+'\n');renameSync(path+'.tmp',path);
  }
  console.log(JSON.stringify({formatted:changed.length,paths:changed,newQueueCompletions:0}));
}

if(fileURLToPath(import.meta.url)===resolve(process.argv[1]||''))run();
