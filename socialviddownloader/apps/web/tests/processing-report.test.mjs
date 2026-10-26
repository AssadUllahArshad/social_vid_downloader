import { test } from 'node:test';
import assert from 'node:assert/strict';
import { toolResults } from '../../../scripts/processing-verification-results.mjs';
const tools = [{id:'converter',name:'Converter',slug:'video-converter'}];
const suite = (projectName, status) => ({specs:[{title:'real browser upload and verified output: converter',tests:[{projectName,results:[{status}]}]}]});
test('tool verification joins separate desktop/mobile suites', () => {
  assert.equal(toolResults(tools,{suites:[suite('desktop','passed'),suite('mobile','passed')]})[0].status,'VERIFIED');
});
test('tool verification never credits a missing project', () => {
  const result=toolResults(tools,{suites:[suite('desktop','passed')]})[0];
  assert.equal(result.desktop,'PASS'); assert.equal(result.mobile,'FAIL'); assert.equal(result.status,'ERROR');
});
test('tool verification preserves failed and skipped results', () => {
  for(const status of ['failed','skipped','timedOut']) assert.equal(toolResults(tools,{suites:[suite('desktop','passed'),suite('mobile',status)]})[0].status,'ERROR');
});
