# Knowledge base — sources, provenance, and kept knowledge

From Hermes's built-in `llm-wiki` skill (MIT), re-expressed into this
skill's project-wiki framing. `structure.md` decides WHERE notes live,
`moc.md` builds the index over them, `vault-health.md` repairs links/headers
and reports stats. This file adds the one lifecycle those don't cover:
taking in an external SOURCE (a paper, a spec, a transcript, a pasted
write-up the vault will reason over later) and keeping what it taught the
vault dated, traceable, and honest as the vault ages.

## When this applies

- The vault absorbs outside material, not only impulse-project-management's
  own artifacts — research papers, vendor docs, interview transcripts, a
  teammate's long write-up.
- A claim somewhere in the vault needs to trace back to the source it came
  from, without re-reading the whole source.
- The same source may be re-ingested later, and the vault should notice it
  changed instead of silently trusting a stale copy.

A vault that only ever holds impulse-pm outputs has no use for this — its
content is already born in the vault. Skip this file. The layer is optional
and additive: turning it on adds a `/raw/` folder and a `SCHEMA.md`; nothing
else about the vault changes.

## Layer 1 — the immutable raw source

Ingested sources are kept verbatim under `/raw/` — an add-on to
`structure.md`'s taxonomy — and never edited after landing. Corrections and
synthesis go into wiki notes that link back, never into the raw file.

```
/raw/             — immutable ingested sources; the agent reads, never writes
├── articles/     — web articles, clippings
├── papers/       — PDFs, arxiv papers
├── transcripts/  — meeting notes, interviews
└── assets/       — images/diagrams a source references
```

Every raw file gets a small frontmatter block so a re-ingest can detect drift:

```yaml
---
source_url: https://example.com/article    # original URL, if any
ingested: YYYY-MM-DD
sha256: <hex digest of the body below the frontmatter>
---
```

The `sha256:` is computed over the body only (everything after the closing
`---`), not the frontmatter itself. On re-ingest of the same URL: recompute,
compare, skip if identical, flag drift and update if different. It is cheap
enough to run on every re-ingest and catches a source that silently changed
under the vault. Capture with `web_extract` for URLs and PDFs (`web_extract`
handles both); pasted text goes to the matching subfolder. Name the file
descriptively, e.g. `raw/articles/karpathy-llm-wiki-2026.md`.

## Layer 2 — SCHEMA.md, the vault's own rules

A single `SCHEMA.md` at vault root records the conventions this vault runs
on, so a later session (or a different agent) doesn't re-invent them: the
domain the vault covers, the file-naming rule, the required frontmatter, the
tag taxonomy, the page-creation thresholds, and the contradiction policy
below. Add a tag to the taxonomy HERE before using it anywhere — freeform
tags decay into noise. A full template is at the end of this file.

On file naming: Obsidian resolves `[[wikilinks]]` by basename, so the case
and separator are the vault's own choice, not this skill's. The built-in's
rule was lowercase-hyphen-no-spaces (`transformer-architecture.md`); a vault
already using Title Case (`Getting-Started.md`) keeps it. Whatever the rule
is, it goes in `SCHEMA.md` and everyone follows it — the point is one rule,
not which one.

## Backbone: index and log

- **Index** — `moc.md`'s MOC *is* this vault's index; no separate `index.md`
  is needed. A sectioned, one-line-per-page catalog is exactly the shape the
  MOC workflow produces.
- **Log** — a vault may keep an append-only `log.md`: one line per action,
  `## [YYYY-MM-DD] action | subject`, with action ∈ ingest, update, query,
  lint, create, archive, delete. Rotate at 500 entries — rename to
  `log-YYYY.md` and start fresh. `vault-health.md`'s stats script reports the
  entry count as the rotation trigger.

## Provenance, confidence, and honesty signals

- **Provenance markers** — on a page synthesizing 3+ sources, append
  `^[raw/articles/source-file.md]` at the end of a paragraph whose claim
  comes from one specific source. This lets a reader trace a claim without
  re-reading the whole raw file. Optional on single-source pages, where the
  `sources:` frontmatter already says enough.
- **Quality signals** in frontmatter — `confidence: high | medium | low`
  (how well-supported the claims are), `contested: true` (unresolved
  contradictions), `contradictions: [other-page-slug]` (pages this one
  conflicts with). Set `confidence` below `high` for opinion-heavy,
  fast-moving, or single-source claims — a weak claim must not silently
  harden into accepted vault fact.

## Update policy — contradictions are marked, never overwritten

When new information conflicts with an existing page:

1. Check dates — a newer source generally supersedes an older one.
2. If genuinely contradictory, note BOTH positions with their dates and
   sources; do not silently replace one with the other.
3. Mark it in frontmatter: `contradictions: [page-name]` on the page, plus
   `contested: true`.
4. Surface it for user review in the next health pass.

## Page thresholds — what earns its own note

- **Create** a page when an entity/concept appears in 2+ sources OR is
  central to one source.
- **Add to** an existing page when a source touches something already
  covered — the default, and what stops a growing vault becoming a pile of
  duplicates.
- **Don't create** a page for a passing mention, a footnote, or anything
  outside the vault's domain.
- **Split** a page past ~200 lines into sub-topics with cross-links.
  `capture-and-atomize.md`'s atomizer does the physical split losslessly.
- **Archive** a fully superseded page: move it to `_archive/` keeping its
  original path, drop it from the index, replace inbound `[[links]]` with
  plain text + "(archived)", and log the action.

## The ingest → query → lint loop

**Ingest** (one source): capture raw → discuss takeaways with the user (skip
in automated/cron runs) → check what already exists (index + a scoped
`search_files`) → write or update pages per the thresholds, cross-linking
each new page to at least 2 others and using only taxonomy tags → update the
index and the log → report every file changed. One source can legitimately
touch 5-15 pages; that is the compounding effect, not a mistake.

**Bulk ingest** (several sources at once): read all sources → identify all
entities/concepts across them → one existence check pass (not N) → create and
update in one pass → update the index once at the end → a single log entry
for the batch.

**Query**: read the index → for a large vault also `search_files` across the
`.md` files, since the index alone misses things → read the relevant pages →
synthesize, citing the pages ("Based on [[page-a]] and [[page-b]]…") → if the
answer is a substantial comparison or novel synthesis, file it as a page under
`/queries/` or `/comparisons/` so it isn't re-derived (skip trivial lookups) →
log the query and whether it was filed.

**Lint** — only the checks `vault-health.md` doesn't already own (it owns
orphan detection and broken-link healing; do not duplicate those):

- **Index completeness** — every wiki page appears in the MOC/index.
- **Frontmatter validation** — required fields present (`title`, `created`,
  `updated`, `type`, `tags`, `sources`); every tag in `SCHEMA.md`'s taxonomy.
- **Stale content** — `updated` more than 90 days older than the newest
  source touching the same entities.
- **Contradictions** — pages sharing tags/entities but stating different
  facts; list every `contested: true` / `contradictions:` page for review.
- **Quality signals** — list `confidence: low` pages and any single-source
  page with no confidence set (candidates for corroboration or a demotion to
  `confidence: medium`).
- **Source drift** — recompute the `sha256:` of every `/raw/` file;
  mismatches mean the raw file was edited (it shouldn't have been) or the URL
  changed.
- **Page size** — flag pages over ~200 lines as split candidates.
- **Tag audit** — every tag in use appears in the taxonomy.
- **Log rotation** — `log.md` past 500 entries.

Report grouped by severity: broken links > orphans > source drift > contested
pages > stale content > style issues.

## Headless sync for servers

On a machine with no display the desktop app isn't an option;
`obsidian-headless` syncs a vault through Obsidian Sync with no GUI, so a
server-side agent can write to the vault while Obsidian desktop reads the same
vault elsewhere. It requires Node.js 22+ and an Obsidian account with a Sync
subscription:

```bash
npm install -g obsidian-headless
ob login --email <email> --password '<password>'
ob sync-create-remote --name "Project Wiki"
cd <vault> && ob sync-setup --vault "<vault-id>"
ob sync --continuous      # foreground; run it under systemd for background
```

A systemd user unit (`ExecStart=… ob sync --continuous`,
`Restart=on-failure`) plus `loginctl enable-linger $USER` keeps it alive across
logout. This is the vault-level counterpart to `cli.md`'s GUI `obsidian` CLI —
use whichever the host actually supports.

## SCHEMA.md template

Adapt to the vault's domain. The schema constrains agent behavior and keeps
sessions consistent:

```markdown
# Wiki Schema

## Domain
[What this vault covers — e.g. "this project's architecture, specs, and decisions"]

## Conventions
- File names: <the vault's rule, e.g. Title Case, or lowercase-hyphen>.
- Every vault page starts with YAML frontmatter (see below).
- Use [[wikilinks]] to link pages — minimum 2 outbound links per page.
- Bump `updated` on every edit.
- Every new page goes into the index (MOC) under the right section.
- Every action is appended to log.md.
- Provenance: on pages synthesizing 3+ sources, append ^[raw/…/source.md] to
  a paragraph whose claim comes from one source.

## Frontmatter
  ---
  title: Page Title
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
  type: entity | concept | comparison | query | summary
  tags: [from the taxonomy below]
  sources: [raw/articles/source-name.md]
  confidence: high | medium | low   # optional quality signals
  contested: true                   # set when contradictions are unresolved
  contradictions: [other-page-slug] # pages this one conflicts with
  ---

## Tag Taxonomy
[Define 10-20 top-level tags. Add a tag here BEFORE using it anywhere.]

## Page Thresholds
- Create a page: entity/concept in 2+ sources, or central to one source.
- Add to an existing page: a source touches something already covered.
- Don't create: passing mentions, minor details, out-of-domain items.
- Split at ~200 lines into sub-topics with cross-links.
- Archive a fully superseded page to _archive/ and drop it from the index.

## Update Policy (contradictions)
1. Check dates — newer generally supersedes older.
2. If truly contradictory, note both positions with dates and sources.
3. Mark it: contradictions: [page-name].
4. Flag for user review in the lint report.
```

## Boundary

This file organizes and keeps SOURCES and their traces — it does not decide
WHAT gets written (`impulse-project-management`), HOW a note is formatted
(`impulse-md-generator`), or where a folder sits (`structure.md`). It does not
replace `moc.md` (indexing), `vault-health.md` (link/header repair and stats),
or `deep-dive.md` (the team-facing page set). Obsidian plugin/theme work stays
out of scope, as in the main SKILL.
