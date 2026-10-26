// Discovery scores surface peers for editorial review. They never authorize
// writing, merging or publication, and do not establish SERP equivalence.
const nativeHypothesis = /^Evaluate the native (.+) operation in (Premiere|Final Cut) for authorized retained media: identify the affected project or source resources, the intended output and a meaningful receiving check\. Confirm the primary instructions and existing answer ownership before treating this as a separate guide\.$/;
const stopWords = new Set(['the', 'and', 'for', 'with', 'why', 'how', 'your', 'from', 'into', 'actual', 'retained', 'check', 'verify', 'versus', 'rather', 'without', 'instead']);
const cache = new Map();

export function nativeTopicOnly(text) {
  return nativeHypothesis.test(String(text ?? ''));
}

export function screeningText(text) {
  const value = String(text ?? '');
  const match = nativeHypothesis.exec(value);
  // Keep the operation and application. Common research instructions are not
  // evidence that two user tasks overlap. Word order still needs human review.
  return match ? `${match[2]} ${match[1]}` : value;
}

export function intentTokens(text) {
  const value = screeningText(text);
  if (!cache.has(value)) {
    cache.set(value, new Set(value.toLowerCase()
      .replace(/\b(download(?:ing|ed)?|save|saving)\b/g, 'retain')
      .replace(/\b(subtitles?|captions?)\b/g, 'texttrack')
      .replace(/[^a-z0-9]+/g, ' ').split(' ')
      .filter(word => word.length > 2 && !stopWords.has(word))));
  }
  return cache.get(value);
}

export function tokenSimilarity(a, b) {
  const intersection = [...a].filter(word => b.has(word)).length;
  const union = a.size + b.size - intersection;
  return union ? intersection / union : 0;
}
