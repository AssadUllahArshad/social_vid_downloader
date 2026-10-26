import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {corePaths,eligibleTranslation,translationDigest} from '../src/lib/translation-policy.mjs';
const load=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'));
const records=load('../../../content/translations/pages.json');
const en=load('../src/locales/en.json');
const processingTools=load('../../../content/processing/tools.json');
const toolPaths=['/video-tools/',...processingTools.map(tool=>`/${tool.slug}/`)];
test('all twelve locales provide every product message and every core route',()=>{
 for(const code of ['hi','ur','ar','bn','id','vi','th','pt-br','es','fr','de','tr']) {
  const messages=load(`../src/locales/${code}.json`);
  assert.deepEqual(Object.keys(messages).sort(),Object.keys(en).sort());
  assert.ok(Object.values(messages).every(value=>typeof value==='string'&&value.trim()));
  assert.deepEqual(records.filter(row=>row.locale===code).map(row=>row.englishPath).sort(),[...corePaths,...toolPaths].sort());
 }
});
test('translation publication requires complete reviewed content and an unchanged digest',()=>{
 const row={status:'PUBLISHED_TRANSLATION',complete:true,reviewApproved:true,approvalDigest:translationDigest(en)};
 assert.equal(eligibleTranslation(row,en),true);
 for(const change of [{complete:false},{reviewApproved:false},{status:'DRAFT_TRANSLATION'},{approvalDigest:'stale'}])assert.equal(eligibleTranslation({...row,...change},en),false);
 assert.equal(eligibleTranslation(row,{...en,download:'changed'}),false);
 const incomplete={...en,download:''};assert.equal(eligibleTranslation({...row,approvalDigest:translationDigest(incomplete)},incomplete),false);
});
test('translation registry never reserves unsupported content or new article topics',()=>{
 assert.equal(records.length,192+12*23);
 assert.ok(records.every(row=>[...corePaths,...toolPaths].includes(row.englishPath)&&!/(snapchat-story|snap-story|story-viewer|download-snapchat-story)/.test(row.englishPath)));
});

test('all processing tools have complete independent locale dictionaries',()=>{const en=load('../src/locales/processing/en.json');for(const code of ['hi','ur','ar','bn','id','vi','th','pt-br','es','fr','de','tr']){const dictionary=load(`../src/locales/processing/${code}.json`);assert.deepEqual(Object.keys(dictionary).sort(),Object.keys(en).sort());assert.ok(Object.values(dictionary).every(value=>value.trim()));}});

test('every indexable processing translation has current approval evidence',()=>{for(const row of records.filter(row=>toolPaths.includes(row.englishPath))){const dictionary={...load(`../src/locales/${row.locale}.json`),...load(`../src/locales/processing/${row.locale}.json`)};assert.equal(eligibleTranslation(row,dictionary),true);}});
