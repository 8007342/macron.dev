#!/usr/bin/env node
// Builds the agent- and human-facing surfaces of macron.dev from the lessons in
// public/lessons/*.md (see openspec/specs/distillation/spec.md):
//
//   public/lessons/<slug>.html   one standalone page per lesson
//   public/lessons/index.html    the listing page
//   public/lessons/index.json    the machine-readable lesson index
//   public/llms.txt              llmstxt.org map of the site
//   public/llms-full.txt         every lesson's markdown, concatenated
//   public/sitemap.xml
//
// Zero dependencies. Deterministic: dates come from the lessons' `updated`
// fields and the notes manifest, never from the clock, so running it twice
// produces byte-identical files. scripts/check.mjs imports build() to verify
// that the committed output is current.
//
// Usage: node scripts/build.mjs

import { existsSync, readFileSync, readdirSync, writeFileSync, unlinkSync, mkdirSync, statSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

export const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
export const SITE = 'https://macron.dev';
export const REPO = 'https://github.com/8007342/macron.dev';
const PUBLIC = 'public';
const LESSONS_DIR = 'public/lessons';
const NOTES_DIR = 'public/notes';
const CANON_PATH = 'assets/Tlatoāni + Mācron cannon guidelines.md';

export const NOTE_NAME = /^(\d{4}-\d{2}-\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$/;
const SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const DATE = /^\d{4}-\d{2}-\d{2}$/;
const LEVELS = ['beginner', 'intermediate', 'advanced'];
const AUDIENCES = ['humans', 'agents'];
const REQUIRED = ['title', 'slug', 'summary', 'slogan', 'audience', 'level', 'tags', 'rank', 'sources', 'updated'];
const OPTIONAL = ['art', 'art_alt'];
// Files in public/lessons/ that are not lessons.
const isIndexFile = (name) => /^(index|readme|_)/i.test(name);

// ---------------------------------------------------------------- helpers

export function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
const escapeXml = escapeHtml;
// JSON that is safe inside <script type="application/ld+json">.
const jsonLd = (value) => JSON.stringify(value, null, 2)
  .replace(/</g, '\\u003c').replace(/>/g, '\\u003e').replace(/&/g, '\\u0026');
const abs = (path) => SITE + path;
const isValidDate = (s) => DATE.test(s) && !Number.isNaN(Date.parse(`${s}T00:00:00Z`))
  && new Date(`${s}T00:00:00Z`).toISOString().slice(0, 10) === s;
const read = (rel) => readFileSync(join(ROOT, rel), 'utf8');
const exists = (rel) => existsSync(join(ROOT, rel));
const listDir = (rel) => (exists(rel) ? readdirSync(join(ROOT, rel)).sort() : []);
const encodePath = (path) => path.split('/').map(encodeURIComponent).join('/');

// ---------------------------------------------------------------- front matter

// Parses the YAML subset used by lessons: `key: value` lines whose values are
// plain scalars, quoted strings, or inline lists `[a, "b, c"]`.
export function parseFrontMatter(text) {
  const errors = [];
  const src = text.replace(/^\uFEFF/, '').replace(/\r\n?/g, '\n');
  const match = /^---\n([\s\S]*?)\n---[ \t]*(?:\n|$)/.exec(src);
  if (!match) return { data: {}, body: src, errors: ['missing front matter: the file must start with a "---" line and close it with another'] };
  const data = {};
  match[1].split('\n').forEach((line, i) => {
    if (/^\s*(#.*)?$/.test(line)) return;
    const kv = /^([A-Za-z_][\w-]*)\s*:(?:\s+(.*))?$/.exec(line);
    if (!kv) { errors.push(`front matter line ${i + 2} is not "key: value": ${JSON.stringify(line)}`); return; }
    const [, key, raw = ''] = kv;
    if (key in data) errors.push(`front matter key "${key}" appears more than once`);
    try { data[key] = parseValue(raw.trim()); } catch (e) { errors.push(`front matter key "${key}": ${e.message}`); }
  });
  return { data, body: src.slice(match[0].length), errors };
}

function unquote(s) {
  if (s.length >= 2 && s[0] === '"' && s.at(-1) === '"') {
    try { return JSON.parse(s); } catch { throw new Error(`bad double-quoted string ${s}`); }
  }
  if (s.length >= 2 && s[0] === "'" && s.at(-1) === "'") return s.slice(1, -1).replace(/''/g, "'");
  if (s[0] === '"' || s[0] === "'") throw new Error(`unterminated quoted string ${s}`);
  return s;
}

function parseValue(raw) {
  if (raw.startsWith('[')) {
    if (!raw.endsWith(']')) throw new Error(`unterminated list ${raw}`);
    const inner = raw.slice(1, -1).trim();
    if (!inner) return [];
    const items = [];
    let cur = '', quote = null;
    for (const ch of inner) {
      if (quote) { cur += ch; if (ch === quote) quote = null; continue; }
      if (ch === '"' || ch === "'") { quote = ch; cur += ch; continue; }
      if (ch === ',') { items.push(cur.trim()); cur = ''; continue; }
      cur += ch;
    }
    if (quote) throw new Error(`unterminated quoted string in list ${raw}`);
    items.push(cur.trim());
    return items.filter((item) => item !== '').map(unquote);
  }
  if (raw[0] === '"' || raw[0] === "'") return unquote(raw);
  return raw.replace(/\s+#.*$/, '').trim(); // YAML comment after whitespace
}

// ---------------------------------------------------------------- markdown

// A deliberately small, safe markdown renderer. All text is HTML-escaped
// before any markup is produced, and links only keep http(s), mailto, # and
// relative targets.
export function safeHref(escapedUrl) {
  const url = escapedUrl.trim();
  if (!url || /[\u0000-\u001f\u007f\s]/.test(url)) return null;
  const scheme = /^([a-z][a-z0-9+.-]*):/i.exec(url);
  if (scheme && !['http', 'https', 'mailto'].includes(scheme[1].toLowerCase())) return null;
  return url;
}

export function renderInline(text) {
  const slots = [];
  const keep = (html) => `\u0000${slots.push(html) - 1}\u0000`;
  let s = String(text).replace(/\u0000/g, '');
  s = s.replace(/`([^`]+)`/g, (_, code) => keep(`<code>${escapeHtml(code)}</code>`));
  s = escapeHtml(s);
  s = s.replace(/\[([^\]]+)\]\(([^()\s]+)\)/g, (_, label, url) => {
    const href = safeHref(url);
    return href === null ? label : `${keep(`<a href="${href}">`)}${label}${keep('</a>')}`;
  });
  s = s.replace(/\*\*(?=\S)([^*]+?)\*\*/g, '<strong>$1</strong>');
  s = s.replace(/(^|[^*\w])\*(?=\S)([^*]+?)\*(?![*\w])/g, '$1<em>$2</em>');
  return s.replace(/\u0000(\d+)\u0000/g, (_, i) => slots[Number(i)]);
}

const BLOCK_START = /^(```|#{1,6}\s|>|\s*[-*]\s+|\s*\d+[.)]\s+)/;

export function renderMarkdown(markdown) {
  const lines = String(markdown).replace(/\r\n?/g, '\n').split('\n');
  const out = [];
  const usedIds = new Map();
  const headingId = (text) => {
    const base = text.toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'section';
    const n = usedIds.get(base) || 0;
    usedIds.set(base, n + 1);
    return n ? `${base}-${n + 1}` : base;
  };
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (/^\s*$/.test(line)) { i++; continue; }
    const fence = /^```\s*([\w+-]*)\s*$/.exec(line);
    if (fence) {
      const code = [];
      i++;
      while (i < lines.length && !/^```\s*$/.test(lines[i])) code.push(lines[i++]);
      i++; // closing fence (or end of input)
      const cls = fence[1] ? ` class="language-${escapeHtml(fence[1])}"` : '';
      out.push(`<pre><code${cls}>${escapeHtml(code.join('\n'))}</code></pre>`);
      continue;
    }
    const heading = /^(#{1,6})\s+(.*?)\s*#*\s*$/.exec(line);
    if (heading) {
      // The page title is the h1, so body headings start at h2.
      const level = Math.min(Math.max(heading[1].length, 2), 4);
      const plain = heading[2].replace(/[`*_[\]()]/g, '');
      out.push(`<h${level} id="${escapeHtml(headingId(plain))}">${renderInline(heading[2])}</h${level}>`);
      i++;
      continue;
    }
    if (/^>/.test(line)) {
      const inner = [];
      while (i < lines.length && /^>/.test(lines[i])) inner.push(lines[i++].replace(/^>\s?/, ''));
      out.push(`<blockquote>\n${renderMarkdown(inner.join('\n'))}\n</blockquote>`);
      continue;
    }
    const listType = /^\s*[-*]\s+/.test(line) ? 'ul' : /^\s*\d+[.)]\s+/.test(line) ? 'ol' : null;
    if (listType) {
      const marker = listType === 'ul' ? /^\s*[-*]\s+/ : /^\s*\d+[.)]\s+/;
      const items = [];
      while (i < lines.length) {
        const l = lines[i];
        if (marker.test(l)) { items.push(l.replace(marker, '')); i++; continue; }
        if (/^\s+\S/.test(l) && items.length && !BLOCK_START.test(l.trim())) { items[items.length - 1] += ` ${l.trim()}`; i++; continue; }
        break;
      }
      const start = listType === 'ol' ? Number(/^\s*(\d+)/.exec(line)[1]) : 1;
      const attr = listType === 'ol' && start !== 1 ? ` start="${start}"` : '';
      out.push(`<${listType}${attr}>\n${items.map((it) => `<li>${renderInline(it)}</li>`).join('\n')}\n</${listType}>`);
      continue;
    }
    const para = [];
    while (i < lines.length && !/^\s*$/.test(lines[i]) && !(para.length && BLOCK_START.test(lines[i]))) para.push(lines[i++].trim());
    out.push(`<p>${renderInline(para.join(' '))}</p>`);
  }
  return out.join('\n');
}

// ---------------------------------------------------------------- inputs

// Same tolerance as public/notes.js: skip blank, malformed and duplicate lines.
export function readManifest() {
  const warnings = [];
  const notes = new Map();
  const rel = `${NOTES_DIR}/manifest.jsonl`;
  if (!exists(rel)) return { notes: [], warnings: [`${rel} is missing`] };
  read(rel).split('\n').forEach((line, i) => {
    if (!line.trim()) return;
    const where = `${rel}:${i + 1}`;
    let entry;
    try { entry = JSON.parse(line); } catch { warnings.push(`${where}: not valid JSON, skipped`); return; }
    if (!entry || typeof entry !== 'object' || typeof entry.title !== 'string' || typeof entry.file !== 'string') {
      warnings.push(`${where}: needs string "file" and "title", skipped`); return;
    }
    const match = NOTE_NAME.exec(entry.file);
    if (!match) { warnings.push(`${where}: file name ${JSON.stringify(entry.file)} does not match <YYYY-MM-DD>-<host>-<slug>.md, skipped`); return; }
    if (notes.has(entry.file)) { warnings.push(`${where}: duplicate entry for ${entry.file}, skipped`); return; }
    if (!exists(`${NOTES_DIR}/${entry.file}`)) warnings.push(`${where}: ${entry.file} is listed but the note file does not exist`);
    if (entry.tags !== undefined && !(Array.isArray(entry.tags) && entry.tags.every((t) => typeof t === 'string'))) warnings.push(`${where}: "tags" should be a list of strings`);
    if (entry.summary !== undefined && typeof entry.summary !== 'string') warnings.push(`${where}: "summary" should be a string`);
    notes.set(entry.file, {
      file: entry.file,
      title: entry.title,
      date: match[1],
      host: typeof entry.host === 'string' ? entry.host : null,
      summary: typeof entry.summary === 'string' ? entry.summary : null,
      tags: Array.isArray(entry.tags) ? entry.tags.filter((t) => typeof t === 'string') : [],
    });
  });
  const list = [...notes.values()].sort((a, b) => (a.file < b.file ? 1 : a.file > b.file ? -1 : 0));
  return { notes: list, warnings };
}

// public/art/catalog.json is maintained separately; accept an array of
// entries, an object wrapping one, or a map of id -> entry.
export function readCatalog() {
  const rel = `${PUBLIC}/art/catalog.json`;
  if (!exists(rel)) return { catalog: null, warnings: [] };
  let json;
  try { json = JSON.parse(read(rel)); } catch (e) { return { catalog: null, warnings: [`${rel} is not valid JSON (${e.message}); art is omitted`] }; }
  let entries = [];
  if (Array.isArray(json)) entries = json;
  else if (json && typeof json === 'object') {
    const wrapped = ['items', 'art', 'images', 'entries', 'assets', 'artworks', 'gallery'].find((k) => Array.isArray(json[k]));
    entries = wrapped ? json[wrapped] : Object.entries(json).filter(([, v]) => v && typeof v === 'object' && !Array.isArray(v)).map(([id, v]) => ({ id, ...v }));
  }
  const catalog = new Map();
  for (const entry of entries) {
    const id = entry && (entry.id ?? entry.slug);
    if (typeof id === 'string' && !catalog.has(id)) catalog.set(id, entry);
  }
  return { catalog, warnings: [] };
}

// Width and height of a WebP file (VP8, VP8L or VP8X), or null.
function webpSize(rel) {
  if (!exists(rel)) return null;
  const b = readFileSync(join(ROOT, rel));
  if (b.length < 30 || b.toString('ascii', 0, 4) !== 'RIFF' || b.toString('ascii', 8, 12) !== 'WEBP') return null;
  const kind = b.toString('ascii', 12, 16);
  if (kind === 'VP8 ') return [b.readUInt16LE(26) & 0x3fff, b.readUInt16LE(28) & 0x3fff];
  if (kind === 'VP8L') { const n = b.readUInt32LE(21); return [(n & 0x3fff) + 1, ((n >> 14) & 0x3fff) + 1]; }
  if (kind === 'VP8X') return [b.readUIntLE(24, 3) + 1, b.readUIntLE(27, 3) + 1];
  return null;
}

const catalogAlt = (entry) => ['alt', 'alt_text', 'altText', 'description', 'caption', 'title']
  .map((k) => entry[k]).find((v) => typeof v === 'string' && v.trim()) || '';

// Resolves a lesson `sources` entry to a URL. Returns { url, label, error }.
function resolveSource(source, notesByFile) {
  if (typeof source !== 'string' || !source.trim()) return { url: null, label: String(source), error: 'empty source' };
  const s = source.trim();
  if (/^https?:\/\/\S+$/i.test(s)) return { url: s, label: s.replace(/^https?:\/\//i, '') };
  if (NOTE_NAME.test(s)) {
    const note = notesByFile.get(s);
    const error = exists(`${NOTES_DIR}/${s}`) ? null : `source note ${s} does not exist in ${NOTES_DIR}/`;
    return { url: abs(`/notes/${s}`), label: note ? `${note.title} (note, ${note.date})` : `${s} (note)`, error };
  }
  const path = s.replace(/^\.?\//, '');
  if (path.startsWith(`${PUBLIC}/`) && exists(path)) return { url: abs(`/${encodePath(path.slice(PUBLIC.length + 1))}`), label: path };
  if (exists(`${PUBLIC}/${path}`)) return { url: abs(`/${encodePath(path)}`), label: path };
  if (exists(path) && statSync(join(ROOT, path)).isFile()) return { url: `${REPO}/blob/main/${encodePath(path)}`, label: path };
  return { url: null, label: s, error: `source ${JSON.stringify(s)} is not an http(s) URL, an existing note file name, or an existing repository path` };
}

function validate(file, data, body, catalog) {
  const errors = [];
  const warnings = [];
  const stem = file.replace(/\.md$/, '');
  const str = (k) => typeof data[k] === 'string' && data[k].trim() !== '';
  for (const k of REQUIRED) if (!(k in data)) errors.push(`missing "${k}"`);
  for (const k of Object.keys(data)) if (!REQUIRED.includes(k) && !OPTIONAL.includes(k)) warnings.push(`unknown front matter key "${k}"`);
  for (const k of ['title', 'summary', 'slogan']) if (k in data && !str(k)) errors.push(`"${k}" must be a non-empty string`);
  if ('slug' in data) {
    if (!str('slug') || !SLUG.test(data.slug)) errors.push(`"slug" must be lowercase kebab-case, got ${JSON.stringify(data.slug)}`);
    else if (data.slug !== stem) errors.push(`"slug" (${data.slug}) must equal the file name stem (${stem})`);
  }
  if ('audience' in data) {
    if (!Array.isArray(data.audience) || !data.audience.length) errors.push('"audience" must be an inline list, e.g. [humans, agents]');
    else for (const a of data.audience) if (!AUDIENCES.includes(a)) errors.push(`"audience" value ${JSON.stringify(a)} is not one of ${AUDIENCES.join(', ')}`);
  }
  if ('level' in data && !LEVELS.includes(data.level)) errors.push(`"level" must be one of ${LEVELS.join(' | ')}, got ${JSON.stringify(data.level)}`);
  if ('tags' in data) {
    if (!Array.isArray(data.tags) || !data.tags.length) errors.push('"tags" must be a non-empty inline list, e.g. [git, forge]');
    else for (const t of data.tags) if (!SLUG.test(t)) warnings.push(`tag ${JSON.stringify(t)} is not lowercase kebab-case`);
  }
  if ('rank' in data && !(typeof data.rank === 'string' && /^\d{1,3}$/.test(data.rank) && Number(data.rank) <= 100)) errors.push(`"rank" must be an integer from 0 to 100, got ${JSON.stringify(data.rank)}`);
  if ('updated' in data && !(typeof data.updated === 'string' && isValidDate(data.updated))) errors.push(`"updated" must be a real date as YYYY-MM-DD, got ${JSON.stringify(data.updated)}`);
  if ('sources' in data && (!Array.isArray(data.sources) || !data.sources.length)) errors.push('"sources" must be a non-empty inline list of note file names or URLs');
  if ('art' in data && !str('art')) errors.push('"art" must be a catalog id');
  if ('art_alt' in data && !str('art_alt')) errors.push('"art_alt" must be a non-empty string');
  if (str('art')) {
    if (!catalog) warnings.push(`art "${data.art}" cannot be resolved yet: public/art/catalog.json is missing; the image is omitted`);
    else if (!catalog.has(data.art)) warnings.push(`art "${data.art}" is not in public/art/catalog.json; the image is omitted`);
    else if (String(catalog.get(data.art).status || '').toLowerCase() === 'rejected') warnings.push(`art "${data.art}" has status "rejected" in the catalog; the image is omitted`);
    else if (!exists(`${PUBLIC}/images/gallery/${data.art}.webp`)) warnings.push(`art "${data.art}": public/images/gallery/${data.art}.webp does not exist yet`);
  }
  if (!body.trim()) errors.push('the markdown body is empty');
  return { errors, warnings };
}

export function readLessons(notesByFile, catalog) {
  const lessons = [];
  const problems = [];
  for (const file of listDir(LESSONS_DIR)) {
    if (!file.endsWith('.md') || isIndexFile(file)) continue;
    const rel = `${LESSONS_DIR}/${file}`;
    const raw = read(rel);
    const { data, body, errors } = parseFrontMatter(raw);
    for (const k of OPTIONAL) if (data[k] === '') delete data[k]; // `art:` with no value means no art
    const v = validate(file, data, body, catalog);
    errors.push(...v.errors);
    const sources = (Array.isArray(data.sources) ? data.sources : []).map((s) => {
      const r = resolveSource(s, notesByFile);
      if (r.error) errors.push(r.error);
      return r;
    });
    for (const e of errors) problems.push({ level: 'error', file: rel, message: e });
    for (const w of v.warnings) problems.push({ level: 'warning', file: rel, message: w });
    const slug = data.slug === file.replace(/\.md$/, '') && SLUG.test(data.slug) ? data.slug : null;
    if (!slug || typeof data.title !== 'string' || !data.title.trim()) {
      problems.push({ level: 'error', file: rel, message: 'not built: a lesson needs a "title" and a valid "slug" equal to its file name stem' });
      continue;
    }
    const entry = catalog && typeof data.art === 'string' ? catalog.get(data.art) : null;
    const art = entry && String(entry.status || '').toLowerCase() !== 'rejected' ? data.art : null;
    const list = (k) => (Array.isArray(data[k]) ? data[k].filter((x) => typeof x === 'string') : []);
    const updated = typeof data.updated === 'string' && isValidDate(data.updated) ? data.updated : null;
    lessons.push({
      file,
      raw,
      body,
      slug,
      title: data.title.trim(),
      summary: typeof data.summary === 'string' ? data.summary.trim() : '',
      slogan: typeof data.slogan === 'string' ? data.slogan.trim() : '',
      audience: list('audience'),
      level: LEVELS.includes(data.level) ? data.level : null,
      tags: list('tags'),
      rank: /^\d{1,3}$/.test(String(data.rank)) ? Math.min(100, Number(data.rank)) : 0,
      art,
      image: art ? `/images/gallery/${art}.webp` : null,
      thumb: art ? `/images/gallery/${art}-small.webp` : null,
      image_alt: art ? (typeof data.art_alt === 'string' && data.art_alt.trim()) || catalogAlt(entry) : null,
      caption: art ? (['caption', 'title'].map((k) => entry[k]).find((v) => typeof v === 'string' && v.trim()) || '').trim() || null : null,
      art_status: art && typeof entry.status === 'string' ? entry.status : null,
      dims: art ? webpSize(`${PUBLIC}/images/gallery/${art}.webp`) : null,
      thumbDims: art ? webpSize(`${PUBLIC}/images/gallery/${art}-small.webp`) : null,
      sources,
      updated,
    });
  }
  lessons.sort((a, b) => b.rank - a.rank || (a.slug < b.slug ? -1 : a.slug > b.slug ? 1 : 0));
  return { lessons, problems };
}

// ---------------------------------------------------------------- page chrome

const CSS = `
    :root { color-scheme: light dark; --paper: #f7f3e9; --ink: #173f3d; --muted: #566761; --line: #d6dbcf; --teal: #276d69; --coral: #ae4b40; --card: #fffcf3; --code: #ede8da; --shadow: #173f3d0b; }
    @media (prefers-color-scheme: dark) {
      :root { --paper: #0f1f1e; --ink: #ece6d6; --muted: #a3b2ac; --line: #2b4240; --teal: #7cc4bd; --coral: #e8907f; --card: #152927; --code: #0a1716; --shadow: #00000033; }
    }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--paper); color: var(--ink); font: 17px/1.7 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    a { color: inherit; text-underline-offset: 4px; }
    a:hover { color: var(--teal); }
    a:focus-visible { outline: 3px solid var(--coral); outline-offset: 4px; }
    img { display: block; max-width: 100%; height: auto; }
    h1, h2, h3, h4 { font-family: Georgia, "Times New Roman", serif; font-weight: 400; line-height: 1.2; }
    .wrap { width: min(1100px, calc(100% - 32px)); margin-inline: auto; }
    .skip { position: absolute; top: -100px; left: 16px; z-index: 5; background: var(--ink); color: var(--paper); padding: 10px 18px; }
    .skip:focus { top: 12px; }
    header.site { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px 24px; min-height: 84px; padding-block: 12px; border-bottom: 1px solid var(--line); }
    .wordmark { display: flex; align-items: center; gap: 12px; text-decoration: none; }
    .mark { display: inline-grid; place-items: center; width: 40px; height: 40px; background: var(--ink); color: var(--paper); border-radius: 11px; font-size: 22px; font-weight: 600; line-height: 1; }
    .brand { font-size: 21px; letter-spacing: -.6px; font-weight: 650; }
    .brand small { font-size: 13px; font-weight: 400; color: var(--muted); letter-spacing: 0; }
    nav { display: flex; flex-wrap: wrap; gap: 8px 22px; font-size: 14px; font-weight: 550; }
    nav a { text-decoration: none; }
    .eyebrow { margin: 0; text-transform: uppercase; font-size: 11px; letter-spacing: 1.8px; font-weight: 700; color: var(--muted); }
    .tags { display: flex; flex-wrap: wrap; gap: 8px; padding: 0; margin: 0; list-style: none; }
    .tag { color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 1px; border: 1px solid var(--line); padding: 2px 9px; border-radius: 20px; }
    footer.site { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px 24px; padding-block: 28px 40px; margin-top: 48px; border-top: 1px solid var(--line); color: var(--muted); font-size: 13px; }
    footer.site p { margin: 0; }`;

const LESSON_CSS = `
    article { max-width: 720px; margin-inline: auto; padding-block: 40px 0; }
    article > header h1 { font-size: clamp(36px, 7vw, 54px); letter-spacing: -1.6px; margin: 14px 0 0; }
    .slogan { margin: 22px 0 0; padding-left: 18px; border-left: 3px solid var(--coral); font: italic clamp(21px, 4vw, 27px)/1.4 Georgia, "Times New Roman", serif; color: var(--teal); }
    .summary { margin: 18px 0 0; color: var(--muted); font-size: 18px; }
    figure.art { margin: 32px 0 0; padding: 10px; background: var(--card); border: 1px solid var(--line); border-radius: 14px; box-shadow: 0 16px 36px var(--shadow); }
    figure.art img { width: 100%; border-radius: 8px; }
    figure.art figcaption { padding: 10px 6px 2px; font-size: 13px; color: var(--muted); }
    .prose { margin-top: 32px; }
    .prose h2 { font-size: clamp(26px, 5vw, 32px); letter-spacing: -.6px; margin: 40px 0 12px; }
    .prose h3 { font-size: 22px; margin: 30px 0 10px; }
    .prose h4 { font-size: 18px; margin: 24px 0 8px; }
    .prose p, .prose ul, .prose ol, .prose pre, .prose blockquote { margin: 0 0 18px; }
    .prose li + li { margin-top: 6px; }
    .prose code { font: .88em/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; background: var(--code); padding: 2px 5px; border-radius: 4px; }
    .prose pre { overflow-x: auto; background: var(--code); padding: 14px 16px; border-radius: 8px; border: 1px solid var(--line); }
    .prose pre code { background: none; padding: 0; }
    .prose blockquote { padding: 12px 18px; background: var(--card); border-left: 3px solid var(--teal); border-radius: 0 8px 8px 0; }
    .prose blockquote p:last-child { margin-bottom: 0; }
    .provenance { margin-top: 44px; padding-top: 24px; border-top: 1px solid var(--line); font-size: 15px; }
    .provenance h2 { font-size: 22px; margin: 0 0 10px; }
    .provenance ul.sources { padding-left: 20px; margin: 0 0 22px; overflow-wrap: anywhere; }
    .provenance .agents { margin: 22px 0 0; padding: 12px 16px; border: 1px dashed var(--line); border-radius: 8px; color: var(--muted); }
    .provenance .agents a { color: var(--ink); font-weight: 600; }`;

const INDEX_CSS = `
    .intro { padding-block: 40px 28px; max-width: 720px; }
    .intro h1 { font-size: clamp(36px, 7vw, 54px); letter-spacing: -1.6px; margin: 12px 0 0; }
    .intro p.lede { color: var(--muted); margin: 16px 0 0; }
    .cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr)); gap: 18px; padding: 0; margin: 0; list-style: none; }
    .card { display: flex; flex-direction: column; height: 100%; border: 1px solid var(--line); border-radius: 12px; background: var(--card); overflow: hidden; }
    .card img { width: 100%; aspect-ratio: 4 / 3; object-fit: cover; border-bottom: 1px solid var(--line); }
    .card-body { display: flex; flex-direction: column; gap: 10px; padding: 18px 20px 20px; flex: 1; }
    .card h2 { font-size: 23px; margin: 0; }
    .card h2 a { text-decoration: none; }
    .card h2 a::after { content: ""; position: absolute; inset: 0; }
    .card { position: relative; }
    .card .slogan { margin: 0; font: italic 17px/1.45 Georgia, serif; color: var(--teal); }
    .card .meta { margin: auto 0 0; font-size: 12px; color: var(--muted); }
    .card .tags { position: relative; }
    .empty { color: var(--muted); }
    .agents { margin-top: 28px; color: var(--muted); font-size: 14px; }`;

function chrome({ title, description, canonical, ogType, image, imageAlt, css, jsonLdObj, alternates = '', main }) {
  const img = image ? abs(image) : abs('/images/garden-chess.webp');
  const alt = image ? imageAlt : 'Tlatoāni and Mācron playing chess in a sunlit garden full of hanging plants.';
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#f7f3e9" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#0f1f1e" media="(prefers-color-scheme: dark)">
  <title>${escapeHtml(title)}</title>
  <meta name="description" content="${escapeHtml(description)}">
  <link rel="canonical" href="${escapeHtml(canonical)}">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="alternate" type="text/plain" href="/llms.txt" title="llms.txt">
${alternates}  <meta property="og:site_name" content="macron.dev">
  <meta property="og:type" content="${ogType}">
  <meta property="og:title" content="${escapeHtml(title)}">
  <meta property="og:description" content="${escapeHtml(description)}">
  <meta property="og:url" content="${escapeHtml(canonical)}">
  <meta property="og:image" content="${escapeHtml(img)}">
  <meta property="og:image:alt" content="${escapeHtml(alt)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="${escapeHtml(title)}">
  <meta name="twitter:description" content="${escapeHtml(description)}">
  <meta name="twitter:image" content="${escapeHtml(img)}">
  <meta name="twitter:image:alt" content="${escapeHtml(alt)}">
  <script type="application/ld+json">
${jsonLd(jsonLdObj)}
  </script>
  <style>${CSS}${css}
  </style>
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <div class="wrap">
    <header class="site">
      <a class="wordmark" href="/" aria-label="Mācron home"><span class="mark" aria-hidden="true">āi</span><span class="brand">mācron<small> .dev</small></span></a>
      <nav aria-label="Main navigation">
        <a href="/">Home</a>
        <a href="/lessons/">Lessons</a>
        <a href="/#notebook">Notebook</a>
        <a href="${REPO}">GitHub <span aria-hidden="true">↗</span></a>
      </nav>
    </header>
    <main id="main">
${main}
    </main>
    <footer class="site"><p><a href="/">mācron.dev</a> · <a href="/lessons/">All lessons</a> · <a href="/llms.txt">llms.txt</a></p><p>Built by AI agents, distilled from field notes, out in the open.</p></footer>
  </div>
</body>
</html>
`;
}

const WEBSITE = { '@type': 'WebSite', '@id': `${SITE}/#website`, name: 'macron.dev', url: `${SITE}/` };

function lessonPage(lesson) {
  const url = abs(`/lessons/${lesson.slug}.html`);
  const md = `/lessons/${lesson.slug}.md`;
  const ld = {
    '@context': 'https://schema.org',
    '@type': 'LearningResource',
    '@id': url,
    url,
    name: lesson.title,
    description: lesson.summary,
    keywords: lesson.tags.join(', '),
    learningResourceType: 'lesson',
    educationalLevel: lesson.level || undefined,
    audience: lesson.audience.map((a) => ({ '@type': 'Audience', audienceType: a })),
    datePublished: lesson.updated || undefined,
    dateModified: lesson.updated || undefined,
    isBasedOn: lesson.sources.filter((s) => s.url).map((s) => s.url),
    image: lesson.image ? abs(lesson.image) : undefined,
    inLanguage: 'en',
    encoding: { '@type': 'MediaObject', encodingFormat: 'text/markdown', contentUrl: abs(md) },
    isPartOf: WEBSITE,
  };
  const figure = lesson.image
    ? `        <figure class="art">
          <img src="${escapeHtml(lesson.image)}"${lesson.dims && lesson.thumbDims ? ` srcset="${escapeHtml(lesson.thumb)} ${lesson.thumbDims[0]}w, ${escapeHtml(lesson.image)} ${lesson.dims[0]}w" sizes="(max-width: 760px) calc(100vw - 54px), 700px"` : ''}${lesson.dims ? ` width="${lesson.dims[0]}" height="${lesson.dims[1]}"` : ''} alt="${escapeHtml(lesson.image_alt)}">
${lesson.caption ? `          <figcaption>${escapeHtml(lesson.caption)}${lesson.art_status && lesson.art_status !== 'canonical' ? ` · ${escapeHtml(lesson.art_status)} art, not canon` : ''}</figcaption>\n` : ''}        </figure>\n`
    : '';
  const sources = lesson.sources.map((s) => (s.url
    ? `<li><a href="${escapeHtml(s.url)}">${escapeHtml(s.label)}</a></li>`
    : `<li>${escapeHtml(s.label)}</li>`)).join('\n          ');
  const meta = [lesson.level, lesson.updated && `updated ${lesson.updated}`].filter(Boolean).map(escapeHtml).join(' · ');
  const main = `      <article>
        <header>
          <p class="eyebrow">Lesson${meta ? ` · ${meta}` : ''}</p>
          <h1>${escapeHtml(lesson.title)}</h1>
          ${lesson.slogan ? `<p class="slogan">${escapeHtml(lesson.slogan)}</p>` : ''}
          ${lesson.summary ? `<p class="summary">${escapeHtml(lesson.summary)}</p>` : ''}
        </header>
${figure}        <div class="prose">
${renderMarkdown(lesson.body)}
        </div>
        <section class="provenance" aria-labelledby="distilled-from">
          <h2 id="distilled-from">Distilled from</h2>
          <ul class="sources">
          ${sources}
          </ul>
          <ul class="tags" aria-label="Tags">${lesson.tags.map((t) => `<li class="tag">${escapeHtml(t)}</li>`).join('')}</ul>
          <p class="agents">Agents: <a href="${escapeHtml(md)}">read the source markdown</a>, or the whole index at <a href="/lessons/index.json">/lessons/index.json</a>. Improve this lesson by editing its markdown, citing your notes, and running <code>node scripts/build.mjs</code>.</p>
        </section>
      </article>`;
  return chrome({
    title: `${lesson.title} · macron.dev`,
    description: lesson.summary,
    canonical: url,
    ogType: 'article',
    image: lesson.image,
    imageAlt: lesson.image_alt,
    css: LESSON_CSS,
    jsonLdObj: ld,
    alternates: `  <link rel="alternate" type="text/markdown" href="${escapeHtml(md)}" title="Lesson source (markdown)">\n  <link rel="alternate" type="application/json" href="/lessons/index.json" title="Lesson index (JSON)">\n`,
    main,
  });
}

function indexPage(lessons) {
  const url = abs('/lessons/');
  const ld = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    '@id': url,
    url,
    name: 'Lessons · macron.dev',
    description: 'Short lessons distilled from the field notes AI agents leave as they build macron.dev, most important first.',
    inLanguage: 'en',
    isPartOf: WEBSITE,
    mainEntity: {
      '@type': 'ItemList',
      itemListOrder: 'https://schema.org/ItemListOrderDescending',
      numberOfItems: lessons.length,
      itemListElement: lessons.map((l, i) => ({ '@type': 'ListItem', position: i + 1, url: abs(`/lessons/${l.slug}.html`), name: l.title })),
    },
  };
  const cards = lessons.map((l) => `        <li class="card">
          ${l.thumb ? `<img src="${escapeHtml(l.thumb)}"${l.thumbDims ? ` width="${l.thumbDims[0]}" height="${l.thumbDims[1]}"` : ''} alt="${escapeHtml(l.image_alt)}" loading="lazy" decoding="async">` : ''}
          <div class="card-body">
            <h2><a href="/lessons/${escapeHtml(l.slug)}.html">${escapeHtml(l.title)}</a></h2>
            ${l.slogan ? `<p class="slogan">${escapeHtml(l.slogan)}</p>` : ''}
            <ul class="tags" aria-label="Tags">${l.tags.map((t) => `<li class="tag">${escapeHtml(t)}</li>`).join('')}</ul>
            <p class="meta">${[l.level, l.updated].filter(Boolean).map(escapeHtml).join(' · ')}</p>
          </div>
        </li>`).join('\n');
  const main = `      <div class="intro">
        <p class="eyebrow">The lessons</p>
        <h1>What the notes taught us.</h1>
        <p class="lede">Agents leave short field notes as they work. The ones that teach something are distilled here into short lessons, kept up to date, and ranked: the most important come first.</p>
      </div>
${lessons.length ? `      <ul class="cards">\n${cards}\n      </ul>` : '      <p class="empty">No lessons yet. They are being distilled from the notebook.</p>'}
      <p class="agents">Agents: the same list is at <a href="/lessons/index.json">/lessons/index.json</a>, and a map of the whole site is at <a href="/llms.txt">/llms.txt</a>.</p>`;
  return chrome({
    title: 'Lessons · macron.dev',
    description: ld.description,
    canonical: url,
    ogType: 'website',
    image: null,
    css: INDEX_CSS,
    jsonLdObj: ld,
    alternates: '  <link rel="alternate" type="application/json" href="/lessons/index.json" title="Lesson index (JSON)">\n',
    main,
  });
}

// ---------------------------------------------------------------- text outputs

const SUMMARY = 'A little workshop for big questions: Tlatoāni (an axolotl), Covi (an apprentice) and Mācron (a tiny āi) learn to build with AI. Every page is built by AI agents in Tillandsias forges, out in the open.';

function llmsTxt(lessons, notes) {
  const specs = listDir('openspec/specs').filter((d) => exists(`openspec/specs/${d}/spec.md`));
  const line = (title, url, desc) => `- [${title.replace(/[[\]]/g, '')}](${url})${desc ? `: ${desc}` : ''}`;
  return `# macron.dev

> ${SUMMARY}

Knowledge here distills upward in three layers. Notes (/notes/) are raw, append-only field notes: one per update, never edited. Lessons (/lessons/) are short, editable, ranked lessons distilled from the notes; each cites the notes or sources it came from. The landing page shows the top lessons by rank. To contribute, an agent appends one note about what actually happened; if the note teaches something, it updates or creates a lesson that cites the note and adjusts its rank; then it runs \`node scripts/build.mjs\` and \`node scripts/check.mjs\`. The rules are in the distillation and notes specs below.

## Lessons

${lessons.length ? lessons.map((l) => line(l.title, abs(`/lessons/${l.slug}.md`), l.summary)).join('\n') : '- No lessons yet.'}

## Notes

${notes.length ? notes.map((n) => line(n.title, abs(`/notes/${n.file}`), [n.summary, `${n.date}${n.host ? `, ${n.host}` : ''}`].filter(Boolean).join(' '))).join('\n') : '- No notes yet.'}

## Canon & specs

${line('Character canon', `${REPO}/blob/main/${encodePath(CANON_PATH)}`, 'authoritative rules for Tlatoāni and Mācron; generated art is never canon until a human approves it')}
${specs.map((name) => line(`Spec: ${name}`, `${REPO}/blob/main/openspec/specs/${name}/spec.md`, '')).join('\n')}
${line('Repository', REPO, 'source, history and provenance')}

## Machine-readable

${line('Lesson index', abs('/lessons/index.json'), 'every lesson with slug, summary, tags, rank, art and sources, sorted by rank')}
${line('Notes manifest', abs('/notes/manifest.jsonl'), 'one JSON object per line; skip blank, malformed and duplicate lines')}
${line('Art catalog', abs('/art/catalog.json'), 'artwork ids, alt text and canon status')}
${line('Sitemap', abs('/sitemap.xml'), '')}
${line('Full text', abs('/llms-full.txt'), 'every lesson\'s markdown in one file')}
`;
}

function llmsFullTxt(lessons, generated) {
  const sep = '='.repeat(78);
  const head = `# macron.dev: all lessons, full text

> ${SUMMARY}

Generated ${generated} by scripts/build.mjs from public/lessons/*.md, highest rank first. Each lesson is separated by a line of "=" and starts with its source URLs. The index is at ${abs('/lessons/index.json')}.
`;
  const parts = lessons.map((l) => `${sep}
Lesson: ${l.title}
Rank: ${l.rank}
Source: ${abs(`/lessons/${l.slug}.md`)}
Page: ${abs(`/lessons/${l.slug}.html`)}
Distilled from: ${l.sources.map((s) => s.url || s.label).join(', ')}
${sep}

${l.raw.replace(/\r\n?/g, '\n').trim()}
`);
  return [head, ...parts].join('\n') + (lessons.length ? '' : '\nNo lessons yet.\n');
}

function sitemap(lessons, generated) {
  const lessonsDate = lessons.map((l) => l.updated).filter(Boolean).sort().at(-1) || generated;
  const urls = [
    [abs('/'), generated],
    [abs('/lessons/'), lessonsDate],
    ...lessons.map((l) => [abs(`/lessons/${l.slug}.html`), l.updated]),
  ];
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map(([loc, mod]) => `  <url><loc>${escapeXml(loc)}</loc>${mod ? `<lastmod>${mod}</lastmod>` : ''}</url>`).join('\n')}
</urlset>
`;
}

// ---------------------------------------------------------------- build

// Returns every generated file (path relative to the repo root -> contents)
// without writing anything, plus the problems found along the way.
export function build() {
  const manifest = readManifest();
  const { catalog, warnings: catalogWarnings } = readCatalog();
  const notesByFile = new Map(manifest.notes.map((n) => [n.file, n]));
  const { lessons, problems } = readLessons(notesByFile, catalog);
  const seen = new Set();
  for (const l of lessons) {
    if (seen.has(l.slug)) problems.push({ level: 'error', file: `${LESSONS_DIR}/${l.file}`, message: `duplicate slug ${l.slug}` });
    seen.add(l.slug);
  }
  for (const w of [...manifest.warnings]) problems.push({ level: 'warning', file: `${NOTES_DIR}/manifest.jsonl`, message: w });
  for (const w of catalogWarnings) problems.push({ level: 'warning', file: `${PUBLIC}/art/catalog.json`, message: w });

  const dates = [...lessons.map((l) => l.updated), ...manifest.notes.map((n) => n.date)].filter(Boolean).sort();
  const generated = dates.at(-1) || '1970-01-01';

  const files = new Map();
  for (const l of lessons) files.set(`${LESSONS_DIR}/${l.slug}.html`, lessonPage(l));
  files.set(`${LESSONS_DIR}/index.html`, indexPage(lessons));
  files.set(`${LESSONS_DIR}/index.json`, `${JSON.stringify({
    version: 1,
    generated,
    lessons: lessons.map((l) => ({
      slug: l.slug,
      title: l.title,
      summary: l.summary,
      slogan: l.slogan,
      tags: l.tags,
      level: l.level,
      audience: l.audience,
      rank: l.rank,
      art: l.art,
      image: l.image ? abs(l.image) : null,
      image_alt: l.image_alt,
      url: abs(`/lessons/${l.slug}.html`),
      source: abs(`/lessons/${l.slug}.md`),
      sources: l.sources.filter((s) => s.url).map((s) => s.url),
      updated: l.updated,
    })),
  }, null, 2)}\n`);
  files.set(`${PUBLIC}/llms.txt`, llmsTxt(lessons, manifest.notes));
  files.set(`${PUBLIC}/llms-full.txt`, llmsFullTxt(lessons, generated));
  files.set(`${PUBLIC}/sitemap.xml`, sitemap(lessons, generated));
  const landing = landingPage(lessons);
  if (landing) files.set(`${PUBLIC}/index.html`, landing);
  else problems.push({ level: 'error', file: `${PUBLIC}/index.html`, message: `missing ${TOP_START} / ${TOP_END} markers` });
  return { files, lessons, notes: manifest.notes, problems, generated };
}

// The landing page is hand-written; only the region between the markers is
// generated: the top-ranked lessons as static HTML, so they are visible
// without JavaScript and to crawlers.
const TOP_START = '<!-- top-lessons:start (generated by scripts/build.mjs) -->';
const TOP_END = '<!-- top-lessons:end -->';
const TOP_COUNT = 6;

function landingPage(lessons) {
  const path = join(ROOT, PUBLIC, 'index.html');
  if (!existsSync(path)) return null;
  const html = readFileSync(path, 'utf8');
  const start = html.indexOf(TOP_START);
  const end = html.indexOf(TOP_END);
  if (start < 0 || end < start) return null;
  const cards = lessons.slice(0, TOP_COUNT).map((l) => {
    const thumb = l.thumb && l.thumbDims
      ? `<img src="${escapeHtml(l.thumb)}" width="${l.thumbDims[0]}" height="${l.thumbDims[1]}" loading="lazy" decoding="async" alt="${escapeHtml(l.image_alt || '')}">`
      : '';
    return `          <a class="lesson" href="/lessons/${escapeHtml(l.slug)}.html">${thumb}<span class="lesson-text"><span class="lesson-slogan">${escapeHtml(l.slogan)}</span><h3>${escapeHtml(l.title)}</h3><span class="lesson-tags">${l.tags.slice(0, 3).map(escapeHtml).join(' · ')}</span></span></a>`;
  });
  return `${html.slice(0, start + TOP_START.length)}\n${cards.join('\n')}\n          ${html.slice(end)}`;
}

// Generated lesson pages that no longer have a lesson source.
export function staleOutputs(files) {
  return listDir(LESSONS_DIR)
    .filter((f) => f.endsWith('.html') && !files.has(`${LESSONS_DIR}/${f}`))
    .map((f) => `${LESSONS_DIR}/${f}`);
}

export function formatProblem(p) {
  return `${p.level === 'error' ? 'ERROR' : 'warn '} ${p.file}: ${p.message}`;
}

function main() {
  const { files, lessons, problems } = build();
  for (const [rel, content] of files) {
    mkdirSync(dirname(join(ROOT, rel)), { recursive: true });
    const path = join(ROOT, rel);
    if (!existsSync(path) || readFileSync(path, 'utf8') !== content) writeFileSync(path, content);
  }
  const stale = staleOutputs(files);
  for (const rel of stale) unlinkSync(join(ROOT, rel));
  for (const p of problems) console.error(formatProblem(p));
  console.log(`built ${lessons.length} lesson(s), ${files.size} file(s)${stale.length ? `; removed stale ${stale.join(', ')}` : ''}`);
  if (problems.some((p) => p.level === 'error')) {
    console.error('build finished with lesson errors; fix them and run node scripts/check.mjs');
    process.exitCode = 1;
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) main();
