// Embeds assets/meghquasar-logo.jpg into index.html as a data URI (the single
// `// @logo` line), so the page stays one self-contained file.
import { readFileSync, writeFileSync } from 'node:fs';

const jpg = readFileSync(new URL('../assets/meghquasar-logo.jpg', import.meta.url));
const page = new URL('../index.html', import.meta.url);
const html = readFileSync(page, 'utf8');
if (!/^.*\/\/ @logo$/m.test(html)) throw new Error('index.html has no // @logo line');
const line = `const LOGO_JPG = 'data:image/jpeg;base64,${jpg.toString('base64')}'; // @logo`;
writeFileSync(page, html.replace(/^.*\/\/ @logo$/m, () => line));
console.log(`embedded logo: ${(jpg.length / 1024).toFixed(0)} KB`);
