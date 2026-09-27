// Builds the dotted-globe land mask embedded in index.html.
//
// Points are laid out on a Fibonacci sphere (N points, identical formula to the
// page), each tested against Natural Earth land polygons, and the result is
// packed as a 1-bit-per-point bitmask in base64. The page regenerates the same
// points and keeps the ones whose bit is set.
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { geoContains, geoBounds } from 'd3-geo';
import { feature } from 'topojson-client';

const N = Number(process.argv[2] || 72000);
const topo = JSON.parse(readFileSync(new URL('../node_modules/world-atlas/land-110m.json', import.meta.url)));
const land = feature(topo, topo.objects.land);

// Split the multipolygon so each piece can be bbox-rejected cheaply.
const polys = land.features.flatMap((f) =>
  f.geometry.type === 'MultiPolygon'
    ? f.geometry.coordinates.map((c) => ({ type: 'Feature', geometry: { type: 'Polygon', coordinates: c } }))
    : [f]
).map((f) => ({ f, b: geoBounds(f) }));

const inBox = ([lon, lat], [[x0, y0], [x1, y1]]) =>
  lat >= y0 && lat <= y1 && (x0 <= x1 ? lon >= x0 && lon <= x1 : lon >= x0 || lon <= x1);

const GOLDEN = Math.PI * (3 - Math.sqrt(5));
const bytes = new Uint8Array(Math.ceil(N / 8));
let count = 0;
for (let i = 0; i < N; i++) {
  const y = 1 - ((i + 0.5) * 2) / N;
  const r = Math.sqrt(1 - y * y);
  const phi = i * GOLDEN;
  const x = Math.cos(phi) * r;
  const z = Math.sin(phi) * r;
  const lat = (Math.asin(y) * 180) / Math.PI;
  const lon = (Math.atan2(x, z) * 180) / Math.PI;
  const p = [lon, lat];
  if (polys.some(({ f, b }) => inBox(p, b) && geoContains(f, p))) {
    bytes[i >> 3] |= 1 << (i & 7);
    count++;
  }
}

const b64 = Buffer.from(bytes).toString('base64');

// Rewrite the single `// @landmask` line in index.html so the page stays self-contained.
const page = new URL('../index.html', import.meta.url);
if (existsSync(page)) {
  const html = readFileSync(page, 'utf8');
  const line = `const LANDMASK = { n: ${N}, b64: '${b64}' }; // @landmask`;
  if (!/^.*\/\/ @landmask$/m.test(html)) throw new Error('index.html has no // @landmask line');
  writeFileSync(page, html.replace(/^.*\/\/ @landmask$/m, () => line));
}
console.log(`N=${N} land=${count} (${((count / N) * 100).toFixed(1)}%) base64=${b64.length} chars`);
