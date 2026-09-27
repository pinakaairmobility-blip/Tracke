// Produces the claude.ai Artifact flavour of index.html: the host wraps pages in
// its own <!doctype>/<html>/<head>/<body> skeleton, so those tags are stripped.
import { readFileSync, writeFileSync } from 'node:fs';

const [src = new URL('../index.html', import.meta.url), out = new URL('../dist/meghquasar-showreel.artifact.html', import.meta.url)] = process.argv.slice(2);
const html = readFileSync(src, 'utf8');
const strip = [/^<!doctype html>\s*$/im, /^<html[^>]*>\s*$/im, /^<head>\s*$/im, /^<\/head>\s*$/im, /^<body>\s*$/im, /^<\/body>\s*$/im, /^<\/html>\s*$/im, /^<meta charset="utf-8">\s*$/im, /^<meta name="viewport"[^>]*>\s*$/im];
let body = html;
for (const re of strip) {
  if (!re.test(body)) throw new Error(`expected to strip ${re}`);
  body = body.replace(re, '');
}
writeFileSync(out, body.replace(/^\s*\n/, ''));
console.log('wrote', out.pathname ?? out, `${(body.length / 1024).toFixed(0)} KB`);
