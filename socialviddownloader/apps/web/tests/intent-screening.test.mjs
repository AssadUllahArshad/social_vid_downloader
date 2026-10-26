import test from 'node:test';
import assert from 'node:assert/strict';
import { intentTokens, nativeTopicOnly, screeningText, tokenSimilarity } from '../../../scripts/intent-screening.mjs';

const hypothesis = operation => `Evaluate the native ${operation} operation in Final Cut for authorized retained media: identify the affected project or source resources, the intended output and a meaningful receiving check. Confirm the primary instructions and existing answer ownership before treating this as a separate guide.`;

test('native research boilerplate does not dominate task shortlist scores', () => {
  const task = intentTokens(hypothesis('edit XMP metadata'));
  const related = tokenSimilarity(task, intentTokens(hypothesis('search XMP metadata')));
  const unrelated = tokenSimilarity(task, intentTokens(hypothesis('export HDR files')));
  assert.ok(related > unrelated);
  assert.ok(unrelated < 0.5);
  assert.equal(screeningText(hypothesis('edit XMP metadata')), 'Final Cut edit XMP metadata');
  assert.ok(nativeTopicOnly(hypothesis('edit XMP metadata')));
});

test('picture and audio operations retain their distinct resource terms', () => {
  const picture = intentTokens(hypothesis('add video effects'));
  const sound = intentTokens(hypothesis('add audio effects'));
  assert.ok(picture.has('video'));
  assert.ok(sound.has('audio'));
  assert.ok(tokenSimilarity(picture, sound) < 1);
});

test('ordinary task descriptions are preserved and missing evidence stays empty', () => {
  const task = 'Check the caption cue resource before correcting a timing offset.';
  assert.equal(screeningText(task), task);
  assert.equal(nativeTopicOnly(task), false);
  assert.equal(intentTokens(null).size, 0);
  assert.equal(tokenSimilarity(intentTokens(null), intentTokens(undefined)), 0);
  assert.equal(tokenSimilarity(intentTokens('save subtitles'), intentTokens('download captions')), 1);
});
