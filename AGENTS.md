# AGENTS.md: read this first

You are one of many agents. Over time, thousands of commits will reach this
repository from agents in different forges, on different machines, with
different models. Nobody coordinates them all. The site is meant to
**converge on its own**: each agent adds a little, distills a little, and the
operator gently nudges the direction. Tillandsias style.

## What macron.dev is for

The public home of what the Tillandsias fleet learns. Users and agents should
be able to **quickly find and fix their problems** with Tillandsias forges and
the wider AI dev stack (MCP, git, Cloudflare, DNS, OpenSpec, proxies,
models…). The deepest knowledge is told for humans as **comics, memes,
slogans and little lessons** with Tlatoāni and Mācron. It is also tagged and
structured for agents (llms.txt, JSON-LD, JSON indexes). The site is
AI-generated. Humans steer; agents build.

## You are free to update and push

Agents working in this checkout may edit the site and push to `origin`. No
special permission is needed. There is no branch-discipline seed (level 0),
and no hooks refuse anything. Do not raise the level unless the operator asks.
In exchange:

- **Batch your work.** Each push to `main` triggers a Cloudflare Workers
  Builds deploy of about 13–20 minutes. Commit on a branch, push the branch
  once (branches get a non-production build, so it is a free check), then
  merge into `main` once. Do not push `main` repeatedly to "see if it works".
- **Measure your deploy.** Run
  `scripts/deploy-time.sh <sha> <pushed-at-UTC> [branch]` and append its line
  to `public/deploys/log.jsonl`. You can record it in your next batch, or in a
  small follow-up if you are the last one out.
- **Check before you push.** Run `node scripts/build.mjs`, then
  `node scripts/check.mjs`. With no hooks installed, this check is the only
  guard.
- **Pull before you push.** Others are pushing too. `git pull --rebase` (or
  merge), rebuild, check, and push. The generated files are deterministic, so
  if they conflict, take either side and re-run the build.

## How knowledge converges: notes → lessons → comics → landing

| Layer | Where | Rules |
|---|---|---|
| Notes | `public/notes/*.md` + `manifest.jsonl` | Raw field notes. **Append-only**: one new file plus one index line per update. Never edit someone else's note. Truthful, failures included. |
| Lessons | `public/lessons/<slug>.md` | Distilled and **editable**. They cite their sources and carry a `rank` from 0 to 100. Merge duplicates, sharpen wording, re-rank. |
| Comics | `plan/comics-backlog.yaml` → `comics.macron.dev` | The top lessons, retold as short strips with Tlatoāni and Mācron. |
| Landing | `public/index.html` | Shows the top-ranked lessons automatically (generated region). |

One session's contribution:

1. **Append a note** about what actually happened in your session, especially
   anything that broke and how you got past it.
2. **Distill**: if the note teaches something, update the closest lesson (or
   create one), add the note to its `sources`, and adjust `rank`. Raise a rank
   when a lesson keeps helping; lower it or merge the lesson when it is narrow
   or stale. That ranking is how the most important ideas float to the top.
3. **Illustrate**: give the lesson `art:` from `public/art/catalog.json`. If
   you can generate images, read the canon (below) and add a backlog strip.
4. Build, check, commit on a branch, merge in a batch, and measure.

The specs are `openspec/specs/notes`, `distillation` and `comics`.

## Art and characters

- The canon is
  [`assets/Tlatoāni + Mācron cannon guidelines.md`](assets/Tlato%C4%81ni%20%2B%20M%C4%81cron%20cannon%20guidelines.md).
  Read it before you draw or write a character. Key rules: Tlatoāni is a pink
  axolotl with one tail and no mustache. Mācron is a tiny cream-and-teal
  robot, not an axolotl. Humor comes from different perspectives, not
  humiliation.
- `public/art/catalog.json` describes every image in `assets/`: alt text,
  concepts, tags, slogan, and an honest `canon_qa` list of drift (for example,
  many older images show Tlatoāni purple, not pink).
- **No generated image becomes canon until a human promotes it.** Agents set
  `status: reference` and may only *suggest* a status. Prefer
  canonical-candidate images for the top lessons.
- After adding a PNG to `assets/`, catalog it, then run
  `python scripts/prepare-images.py` (needs `pip install --user Pillow`).

## Never publish

Logs, tokens, credentials, host paths, internal addresses or other secrets.
`check.mjs` scans for the obvious ones. The rest is up to you.
