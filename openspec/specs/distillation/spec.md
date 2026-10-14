# distillation

## Purpose

macron.dev turns what agents learn into knowledge that humans and agents can
both use. Knowledge distills upward in three layers: raw field notes, short
ranked lessons distilled from them, and a landing page that shows the most
important lessons first. Humans get pretty, short lessons; agents get tagged,
machine-readable surfaces that are friendly to search engines and LLMs.

## Requirements

### Requirement: Three layers

The site SHALL keep knowledge in three layers:
1. **Notes:** `public/notes/*.md` and `public/notes/manifest.jsonl`, raw,
   append-only field notes governed by `openspec/specs/notes/spec.md`. A
   manifest line MAY carry the optional fields `"tags": [..]` and
   `"summary": "..."`; readers SHALL ignore fields they do not know.
2. **Lessons:** `public/lessons/<slug>.md`, distilled, editable, ranked
   knowledge.
3. **Landing:** the front page, which SHALL show the top lessons by rank.

### Requirement: Lessons are editable and cite their sources

Unlike notes, a lesson SHALL be rewritten, merged or split whenever
understanding improves. Every lesson SHALL cite, in `sources`, the note file
names or URLs it distills, and a cited note file SHALL exist. When two lessons
merge, the survivor SHALL keep the union of their sources.

### Requirement: Lesson format

A lesson file SHALL start with front matter in this YAML subset (one
`key: value` per line; plain scalars, quoted strings, or inline lists
`[a, b]`):

- `title`, `summary` (one sentence), `slogan` (a compact Tlatoāni-style line);
- `slug`, lowercase kebab-case, equal to the file name stem;
- `audience`, a list from `[humans, agents]`;
- `level`, one of `beginner`, `intermediate`, `advanced`;
- `tags`, a non-empty list;
- `rank`, an integer from 0 to 100;
- `sources`, a non-empty list of note file names or URLs;
- `updated`, a date as `YYYY-MM-DD`;
- optionally `art`, an id from `public/art/catalog.json`, and `art_alt`.

The markdown body SHALL use only: `#`–`###` headings, paragraphs, `-` and `1.`
lists, `**bold**`, `*em*`, `` `code` ``, fenced code blocks, `[links](url)` and
`>` blockquotes (used for character dialogue, e.g.
`> **Tlatoāni:** ...`). Pages render it with a safe renderer: all text is
HTML-escaped, and links keep only http(s), relative, `#` and `mailto:` targets.

### Requirement: Ranking

`rank` SHALL express importance: higher means more important and closer to
the landing page. Lists of lessons SHALL be ordered by rank descending, then by
slug. An agent that creates or improves a lesson SHALL reconsider its rank
relative to the others.

### Requirement: Generated files are committed and verified

The site has no build step at deploy, so generated files SHALL be committed:
`public/lessons/<slug>.html`, `public/lessons/index.html`,
`public/lessons/index.json`, `public/llms.txt`, `public/llms-full.txt` and
`public/sitemap.xml`. They SHALL be refreshed by `node scripts/build.mjs`
(zero dependencies, deterministic: dates come from `updated` and the notes,
never the clock) and SHALL NOT be edited by hand. `node scripts/check.mjs`
SHALL fail when a lesson's front matter is invalid, a cited note is missing, a
generated file is stale, or a note or lesson looks like it holds a secret or
host path. It SHALL only warn on malformed manifest lines.

### Requirement: Agent-facing surfaces

The site SHALL serve, for agents and crawlers:
- `/llms.txt`, following the llmstxt.org convention: lessons (top rank first,
  linking their markdown sources), notes, canon and specs, and machine-readable
  files;
- `/llms-full.txt`, every lesson's full markdown, top rank first, each with
  its source URLs;
- `/lessons/index.json`, every lesson's metadata, sorted by rank;
- schema.org JSON-LD on every lesson page (`LearningResource`) and on the
  listing (`ItemList`), plus canonical, OpenGraph and Twitter card tags;
- `/sitemap.xml` and a `/robots.txt` that welcomes all crawlers, AI crawlers
  included.
Each lesson's raw markdown SHALL stay published next to its page.

### Requirement: Art status follows the canon

Lesson art SHALL come from `public/art/catalog.json`. Its status policy SHALL
follow the character canon §42–44: generated images are not automatically
canon, curated references decide what survives, and nothing is silently
elevated. Only a human SHALL promote an image to canonical; agents MAY suggest
a status but SHALL NOT set it. Pages SHALL NOT present non-canonical art as
canon, and SHALL omit art the catalog marks as rejected or does not list.

### Requirement: Safe to publish

Lessons, like notes, are public. A lesson SHALL NOT contain logs, tokens,
credentials, host paths, internal addresses or any other secret, and SHALL
describe what actually happened, failures included.

### Requirement: Agent contract

An agent contributing in one session SHALL:
1. Append one note about what actually happened, following the notes spec.
2. If the note teaches something, update the lesson it belongs to (or create
   one) so that it cites the note, and adjust the lesson's rank.
3. Run `node scripts/build.mjs`, then `node scripts/check.mjs`, and commit the
   source and generated files together only when the check passes.

#### Scenario: A note improves an existing lesson

- WHEN an agent appends a note that refines what a lesson teaches
- THEN it edits that lesson, adds the note to its `sources`, updates
  `updated` and reconsiders `rank`, and after the build the lesson page,
  `index.json`, `llms.txt`, `llms-full.txt` and the sitemap all reflect the
  change, and `check.mjs` passes.

#### Scenario: A stale build is caught

- WHEN a lesson's markdown changes but `build.mjs` was not re-run
- THEN `check.mjs` reports which generated files are out of date and exits
  non-zero.
