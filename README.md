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

## The workshop

The landing page introduces Tlatoāni, apprentice Covi, and Mācron the āi:
learning together, experimenting, and documenting their adventures. Planned
sub-projects are labeled as planned until they are published.

Preview locally with `python -m http.server 8000 --directory public`.

## Character references

The supplied originals live in `assets/`. Read
[the character canon](assets/Tlatoāni%20+%20Mācron%20cannon%20guidelines.md)
before creating character artwork or writing. Its explicit constraints are
authoritative; committing a reference does not automatically promote every
detail in it to canon. The supplied images remain reference material with no
new individual canonical status assigned by this landing-page update.

The page uses optimized WebP display copies of `Chess Tlatoāni vs Mācron.png`
and `Baby mācrons.png`, preserving the original compositions. To regenerate
them, install Pillow and run `python scripts/prepare-images.py`.
Only `public/` is served; the full reference collection stays in the repository
for future builders.
