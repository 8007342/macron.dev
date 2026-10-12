# macron.dev

The apex site, `macron.dev`, indexes a family of sub-projects, each served at
`<name>.macron.dev`: `comics.`, `doc.`, `art.`, and others as they appear.

Everything here is built by AI agents working inside
[Tillandsias](https://github.com/8007342/tillandsias) forges, and each
sub-project keeps its source, build and provenance in the open.

Stack: the default is a plain static site (`wrangler.jsonc` serving `./public`,
no build step). Flutter + Flame is used for the comics only and is opt-in
anywhere else.

Status: under construction. See `openspec/specs/` for what each sub-project
will be, and `plan/` for its backlog.
