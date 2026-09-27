// Frame-accurate renderer: drives index.html?render in headless Chromium,
// captures every frame, encodes H.264 with ffmpeg, and muxes the Web Audio score.
//
//   node tools/render.mjs                         full film → dist/meghquasar-showreel.mp4
//   node tools/render.mjs --fps 60 --workers 4    smoother, in parallel
//   node tools/render.mjs --stills 1,9.5,15.3     PNG stills → dist/stills/
//   node tools/render.mjs --from 38 --to 52       render a range (no audio)
//
// ffmpeg: set FFMPEG=/path/to/ffmpeg, or have one with libx264 on PATH.
import { chromium } from 'playwright';
import http from 'node:http';
import { spawn, execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync, existsSync, statSync, rmSync } from 'node:fs';
import { extname, join, dirname, resolve } from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const DIST = join(ROOT, 'dist');
const args = Object.fromEntries(process.argv.slice(2).reduce((acc, a, i, all) => {
  if (a.startsWith('--')) acc.push([a.slice(2), all[i + 1] && !all[i + 1].startsWith('--') ? all[i + 1] : true]);
  return acc;
}, []));
const FPS = Number(args.fps || 30);
const WORKERS = Number(args.workers || 3);
const OUT = resolve(args.out || join(DIST, 'meghquasar-showreel.mp4'));
const CRF = String(args.crf || 19);
const FFMPEG = process.env.FFMPEG || findFfmpeg();

function findFfmpeg() {
  try { if (execFileSync('ffmpeg', ['-hide_banner', '-encoders'], { stdio: 'pipe' }).toString().includes('libx264')) return 'ffmpeg'; } catch { /* not on PATH */ }
  try { return execFileSync('python3', ['-c', 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())']).toString().trim(); } catch { /* none */ }
  return null;
}

// --- static server; three.js is served from node_modules in place of the CDN ---
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.json': 'application/json', '.css': 'text/css' };
function serve() {
  return new Promise((ok) => {
    const srv = http.createServer((req, res) => {
      const p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
      const f = join(ROOT, p === '/' ? 'index.html' : p);
      if (!f.startsWith(ROOT) || !existsSync(f) || statSync(f).isDirectory()) { res.writeHead(404); res.end(); return; }
      res.writeHead(200, { 'content-type': MIME[extname(f)] || 'application/octet-stream' });
      res.end(readFileSync(f));
    }).listen(0, '127.0.0.1', () => ok(srv));
  });
}
const THREE_CDN = /^https:\/\/cdn\.jsdelivr\.net\/npm\/three@[^/]+\/(.*)$/;
const FONTS = /^https:\/\/fonts\.(googleapis|gstatic)\.com\//;
const CACHE = join(ROOT, '.cache');

// Google Fonts are fetched with curl (which honours the system proxy and CA
// settings) and cached, so rendering never depends on the browser's network.
function cachedFont(url, ua) {
  mkdirSync(CACHE, { recursive: true });
  const f = join(CACHE, createHash('sha1').update(url).digest('hex'));
  if (!existsSync(f)) execFileSync('curl', ['-sSfL', '-A', ua, '-o', f, url]);
  return readFileSync(f);
}

async function openPage(port) {
  const browser = await chromium.launch({
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-gpu-vsync', '--font-render-hinting=none'],
  });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => console.error('[page error]', e.message));
  page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') console.error(`[console.${m.type()}]`, m.text()); });
  await page.route(THREE_CDN, (route) => {
    const rel = route.request().url().match(THREE_CDN)[1];
    const file = join(ROOT, 'node_modules/three', rel);
    route.fulfill({ status: 200, body: readFileSync(file), headers: { 'content-type': 'text/javascript', 'access-control-allow-origin': '*' } });
  });
  await page.route(FONTS, async (route) => {
    const req = route.request();
    try {
      const body = cachedFont(req.url(), await req.headerValue('user-agent'));
      const type = req.url().includes('googleapis') ? 'text/css' : 'font/woff2';
      route.fulfill({ status: 200, body, headers: { 'content-type': type, 'access-control-allow-origin': '*' } });
    } catch (e) { console.error('font fetch failed', req.url()); route.abort(); }
  });
  await page.goto(`http://127.0.0.1:${port}/index.html?render`);
  await page.waitForFunction(() => window.MQ, null, { timeout: 60000 });
  await page.evaluate(() => window.MQ.ready);
  const cdp = await page.context().newCDPSession(page);
  return { browser, page, cdp };
}

async function renderFrameTo(page, t) {
  await page.evaluate(async (tt) => {
    window.MQ.renderFrame(tt);
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  }, t);
}

async function stills(port, times) {
  const dir = join(DIST, 'stills');
  mkdirSync(dir, { recursive: true });
  const { browser, page } = await openPage(port);
  for (const t of times) {
    await renderFrameTo(page, t);
    const f = join(dir, `still-${t.toFixed(2).padStart(6, '0')}.png`);
    await page.screenshot({ path: f });
    console.log('wrote', f);
  }
  await browser.close();
}

function encoder(file) {
  const ff = spawn(FFMPEG, ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', CRF, '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-tune', 'film', '-g', String(FPS * 2), file], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((ok, bad) => ff.on('close', (c) => (c === 0 ? ok() : bad(new Error('ffmpeg exited ' + c)))));
  return { ff, done };
}

async function worker(port, id, frames, file) {
  const { browser, page, cdp } = await openPage(port);
  const { ff, done } = encoder(file);
  const t0 = Date.now();
  for (let i = 0; i < frames.length; i++) {
    await renderFrameTo(page, frames[i] / FPS);
    const { data } = await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: 95, optimizeForSpeed: false });
    const buf = Buffer.from(data, 'base64');
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    if (i % 60 === 0) {
      const el = (Date.now() - t0) / 1000, rate = (i + 1) / el;
      console.log(`[w${id}] frame ${frames[i]} (${i + 1}/${frames.length}) ${rate.toFixed(2)} fps, eta ${Math.round((frames.length - i) / rate)} s`);
    }
  }
  ff.stdin.end();
  await done;
  await browser.close();
}

async function audio(port, file) {
  const { browser, page } = await openPage(port);
  const n = await page.evaluate(() => window.MQ.audioPCM());
  const parts = [];
  for (let i = 0; i < n; i++) parts.push(Buffer.from(await page.evaluate((k) => window.MQ.audioChunk(k), i), 'base64'));
  writeFileSync(file, Buffer.concat(parts));
  await browser.close();
}

const srv = await serve();
const port = srv.address().port;
try {
  if (args.stills) {
    await stills(port, String(args.stills).split(',').map(Number));
  } else {
    if (!FFMPEG) throw new Error('No ffmpeg with libx264 found. Set FFMPEG=/path/to/ffmpeg or `pip install imageio-ffmpeg`.');
    mkdirSync(DIST, { recursive: true });
    const tmp = join(DIST, '.parts');
    rmSync(tmp, { recursive: true, force: true });
    mkdirSync(tmp, { recursive: true });
    const from = Math.round(Number(args.from || 0) * FPS), to = Math.round(Number(args.to || 94) * FPS);
    const all = Array.from({ length: to - from }, (_, i) => from + i);
    const per = Math.ceil(all.length / WORKERS);
    const segs = [];
    const jobs = [];
    for (let w = 0; w < WORKERS; w++) {
      const frames = all.slice(w * per, (w + 1) * per);
      if (!frames.length) continue;
      const f = join(tmp, `seg${w}.mp4`);
      segs.push(f);
      jobs.push(worker(port, w, frames, f));
    }
    const withAudio = !args.from && !args.to && !args['no-audio'];
    const pcm = join(tmp, 'score.pcm');
    if (withAudio) jobs.push(audio(port, pcm));
    const t0 = Date.now();
    await Promise.all(jobs);
    console.log(`frames done in ${Math.round((Date.now() - t0) / 1000)} s`);
    const list = join(tmp, 'list.txt');
    writeFileSync(list, segs.map((s) => `file '${s}'`).join('\n'));
    const video = join(tmp, 'video.mp4');
    execFileSync(FFMPEG, ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', video]);
    if (withAudio) {
      execFileSync(FFMPEG, ['-y', '-loglevel', 'error', '-i', video, '-f', 's16le', '-ar', '48000', '-ac', '2', '-i', pcm,
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', OUT]);
    } else {
      execFileSync(FFMPEG, ['-y', '-loglevel', 'error', '-i', video, '-c', 'copy', '-movflags', '+faststart', OUT]);
    }
    rmSync(tmp, { recursive: true, force: true });
    console.log('wrote', OUT, (statSync(OUT).size / 1e6).toFixed(1), 'MB');
  }
} finally {
  srv.close();
}
