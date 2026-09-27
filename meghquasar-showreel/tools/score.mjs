// Renders only the Web Audio score to dist/score.wav and prints its loudness stats.
import { chromium } from 'playwright';
import http from 'node:http';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const FFMPEG = process.env.FFMPEG || execFileSync('python3', ['-c', 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())']).toString().trim();
const srv = http.createServer((q, r) => {
  const f = join(ROOT, new URL(q.url, 'http://x').pathname);
  if (!f.startsWith(ROOT) || !existsSync(f)) { r.writeHead(404); r.end(); return; }
  r.writeHead(200, { 'content-type': f.endsWith('.html') ? 'text/html' : 'text/javascript' }); r.end(readFileSync(f));
}).listen(0, '127.0.0.1');
await new Promise((r) => srv.on('listening', r));
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on('pageerror', (e) => console.error('[page error]', e.message));
await page.route(/cdn\.jsdelivr\.net\/npm\/three@[^/]+\/(.*)$/, (r) => r.fulfill({ body: readFileSync(join(ROOT, 'node_modules/three', r.request().url().split(/three@[^/]+\//)[1])), headers: { 'content-type': 'text/javascript' } }));
await page.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());
await page.goto(`http://127.0.0.1:${srv.address().port}/index.html?render`);
await page.waitForFunction(() => window.MQ);
await page.evaluate(() => window.MQ.ready);
const t0 = Date.now();
const n = await page.evaluate(() => window.MQ.audioPCM());
const parts = [];
for (let i = 0; i < n; i++) parts.push(Buffer.from(await page.evaluate((k) => window.MQ.audioChunk(k), i), 'base64'));
console.log(`score rendered in ${((Date.now() - t0) / 1000).toFixed(1)} s`);
mkdirSync(join(ROOT, 'dist'), { recursive: true });
const pcm = join(ROOT, 'dist', 'score.pcm');
writeFileSync(pcm, Buffer.concat(parts));
const wav = join(ROOT, 'dist', 'score.wav');
execFileSync(FFMPEG, ['-y', '-loglevel', 'error', '-f', 's16le', '-ar', '48000', '-ac', '2', '-i', pcm, wav]);
const stats = execFileSync(FFMPEG, ['-hide_banner', '-i', wav, '-af', 'volumedetect,ebur128=framelog=quiet', '-f', 'null', '-'], { stdio: ['ignore', 'pipe', 'pipe'] });
await browser.close(); srv.close();
