# Conversion rules in detail

Contents:
1. Callout mapping
2. Link resolution
3. Embeds
4. Why each cleanup rule exists
5. Known lossy conversions

---

## 1. Callout mapping

GitHub supports exactly five alert types: `NOTE`, `TIP`, `IMPORTANT`, `WARNING`,
`CAUTION`. Obsidian ships more than twenty callout types, so several collapse onto the
same alert. When a type collapses, its original name is preserved as a bold title line
so no meaning is lost.

| Obsidian type | GitHub alert | Title added |
|---|---|---|
| `note` | `NOTE` | — |
| `info`, `todo`, `abstract`, `summary`, `tldr`, `example`, `question`, `help`, `faq` | `NOTE` | yes |
| `tip`, `hint` | `TIP` | `hint` only |
| `success`, `check`, `done` | `TIP` | yes |
| `important` | `IMPORTANT` | — |
| `warning` | `WARNING` | — |
| `caution`, `attention` | `WARNING` | yes |
| `danger`, `error`, `bug`, `failure`, `fail`, `missing` | `CAUTION` | yes |
| `quote`, `cite` | plain blockquote | title only if custom |

A custom title always wins over the generated one.

### Cases that degrade to a plain bold-titled blockquote

GitHub's alert parser is strict, so these can't stay alerts:

- **Nested callouts** (`> > [!tip]`) — alerts don't nest.
- **Indented callouts** — a callout inside a list item isn't at block level.
- **`quote`/`cite`** — no alert equivalent; a blockquote is already the right rendering.

### Collapsible callouts

`> [!note]-` (starts folded) and `> [!note]+` (starts expanded) both flatten to a normal
alert. The fold marker is dropped and the flattening is reported, because a folded
callout hiding a long block will now be fully visible — a real change in how the page
reads.

### Blank line before an alert

An alert directly after a paragraph line is absorbed as a lazy continuation of that
paragraph and never renders. The converter inserts a blank line when the preceding line
is non-blank text.

---

## 2. Link resolution

Obsidian resolves `[[Note]]` by searching the whole vault, so conversion needs the same
index. The rule used, matching Obsidian's own behavior:

1. Exact vault-relative path match (`[[Folder/Note]]`).
2. Filename match; if several notes share the name, prefer one in the same folder as the
   source note, then the shortest path.
3. No match → emit the alias, or the raw target text, as plain text.

Paths in the output are relative to the converted file's location and URL-encoded, so
`Other Note.md` becomes `Other%20Note.md`. Without encoding, spaces break the link on
GitHub.

Heading fragments use GitHub's anchor rules: lowercase, punctuation stripped, spaces
replaced with hyphens. Block references (`#^abc123`) have no equivalent anchor, so the
link points at the file and drops the fragment.

### Why unresolved links become plain text, not links

A link to a file that doesn't exist renders as a live link that 404s. Plain text is
honest about what happened, and every unresolved target is listed in the report so the
user can decide what to do.

---

## 3. Embeds

| Embed | Output | Reason |
|---|---|---|
| Image | `![alt](path)` | Direct equivalent |
| Image with size (`\|300`) | `<img width="300">` | Markdown has no size syntax; GitHub allows this HTML |
| Note | Link, or inlined content with `--embed-mode inline` | Transclusion doesn't exist in standard Markdown |
| PDF, video, audio | Link | GitHub won't inline these from a Markdown link |

Inlining a note (`--embed-mode inline`) goes one level deep only. Deeper recursion risks
loops, and duplicating a note into many files makes the output hard to maintain — the
link is usually the better default.

When `![[Note#Section]]` is inlined, only that section's content is spliced in, up to the
next heading of the same or higher level.

---

## 4. Why each cleanup rule exists

**`#tag` at line start → backticks.** This is the most damaging Obsidian-ism in a normal
previewer: a line of tags silently becomes a giant heading. Backticks keep the tag
visible and readable while stopping the heading parse. Tags mid-sentence are already
harmless and are left alone. When a line-leading tag is escaped, other tags on that same
line are escaped too, so the line looks consistent.

**`==highlight==` → bold.** GitHub strips `<mark>` in most contexts, so bold is the
reliable default. `--highlight mark` is available for renderers that do support it.

**`%%comments%%` removed.** They're author-private in Obsidian and would become visible
body text anywhere else. Removal also tidies the doubled spaces and blank lines left
behind, since those change how surrounding blocks parse.

**Block IDs removed.** `^abc123` is an invisible anchor in Obsidian and visible junk
everywhere else.

**Non-standard task states → `[ ]`.** GitHub renders only `[ ]` and `[x]`; anything else
prints the raw brackets. This loses the distinction between "in progress" and "not
started" — worth mentioning to the user if their notes use these heavily.

**Frontmatter kept.** GitHub renders YAML frontmatter as a small table, which is usually
what the user wants. `--strip-frontmatter` removes it.

---

## 5. Known lossy conversions

Be upfront about these rather than letting the user discover them:

- Collapsible callouts become always-visible.
- Block-reference links lose their precise anchor and point at the file.
- Custom task states collapse to unchecked.
- Note embeds become links unless inlining is requested.
- Dataview, Tasks and Templater blocks are left as inert code blocks — they were dynamic
  queries and cannot be reproduced as static Markdown.
- Canvas files (`.canvas`) aren't Markdown at all and are not converted.
