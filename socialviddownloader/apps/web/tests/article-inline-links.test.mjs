import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { runInNewContext } from "node:vm";
import ts from "typescript";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

// Exercise the actual private renderer without importing Next's route runtime
// or adding a test-only export to the page module.
const path = new URL("../src/app/(english)/guides/[platform]/[slug]/page.tsx", import.meta.url);
const ast = ts.createSourceFile("page.tsx", readFileSync(path, "utf8"), ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
const renderer = ast.statements.find(node => ts.isFunctionDeclaration(node) && node.name?.text === "renderParagraphLinks");
assert.ok(renderer, "The article renderer must exist");
const compiled = ts.transpileModule(renderer.getText(ast), {
  compilerOptions: { jsx: ts.JsxEmit.ReactJSX, module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
}).outputText;
const first = "/guides/general/approved-guide/";
const second = "/guides/youtube/another-guide/";
function render(text, published = new Set([first, second])) {
  const context = {
    exports: {},
    require: createRequire(import.meta.url),
    getArticle: path => published.has(path) ? { path } : undefined,
    Link: props => createElement("a", props),
  };
  runInNewContext(compiled, context);
  return renderToStaticMarkup(createElement("p", null, context.renderParagraphLinks(text)));
}

describe("safe contextual article links", () => {
  it("preserves ordinary paragraph text and escaping", () => {
    const text = 'Existing words & <code> remain exactly "as written".';
    assert.equal(render(text), renderToStaticMarkup(createElement("p", null, text)));
  });
  it("renders multiple approved internal links with surrounding text intact", () => {
    assert.equal(render(`Before [first guide](${first}). Between [second guide](${second}). After.`),
      `<p>Before <a href="${first}">first guide</a>. Between <a href="${second}">second guide</a>. After.</p>`);
  });
  it("keeps unsafe, external, noncanonical and unpublished destinations as text", () => {
    for (const target of ["https://example.com/", "//example.com/", "javascript:alert(1)", "/admin/", "/guides/general/missing/", "/guides/general/../approved-guide/", "/guides/general/%61pproved-guide/", first + "?x=1", first + "#section", first.slice(0, -1)]) {
      const text = `Read [guide](${target}).`;
      assert.equal(render(text), renderToStaticMarkup(createElement("p", null, text)), target);
    }
  });
  it("fails closed when a destination loses publication approval", () => {
    const text = `Read [guide](${first}).`;
    assert.equal(render(text, new Set()), renderToStaticMarkup(createElement("p", null, text)));
  });
  it("escapes HTML in labels and surrounding content", () => {
    const html = render(`<script>alert(1)</script> [<img src=x onerror=alert(1)>](${first})`);
    assert.ok(!html.includes("<script>") && !html.includes("<img"));
    assert.ok(html.includes("&lt;script&gt;") && html.includes("&lt;img"));
    assert.equal((html.match(/<a /g) || []).length, 1);
  });
  it("does not consume ordinary bracketed text around a valid link", () => {
    assert.equal(render(`Keep [notes] and [safe](${first}) and [unfinished.`),
      `<p>Keep [notes] and <a href="${first}">safe</a> and [unfinished.</p>`);
  });
});
