# Conversion rules in detail

Contents:
1. What "portable" means here
2. Callouts
3. Link resolution
4. Embeds
5. Frontmatter
6. Non-Obsidian repairs
7. Known lossy conversions

---

## 1. What "portable" means here

The target is the set of constructs that render the same way across CommonMark,
python-markdown, kramdown, marked, Pandoc, VS Code, Typora, MkDocs, Jekyll, Hugo,
Docusaurus, GitLab and GitHub.

Three things fall just outside strict CommonMark but are kept anyway, because every
renderer a note is realistically viewed in supports them, and the alternatives are worse:

- **Pipe tables.** Converting a table to a bullet list destroys the structure that made
  it a table. Tables are kept and normalized instead.
- **Task lists.** In a renderer without them, `- [ ] item` degrades to a bullet reading
  "[ ] item" — still perfectly legible.
- **Minimal inline HTML** for image sizing, since Markdown has no size syntax at all.
  `--no-html` drops sizing rather than emitting the tag.

GitHub alerts are *not* kept. `> [!NOTE]` renders as a styled box on GitHub and as a
blockquote containing a literal `[!NOTE]` line everywhere else — exactly the kind of
dialect-specific breakage this skill exists to remove.

---

## 2. Callouts

Every Obsidian callout becomes a blockquote whose first line is a bold title:

```
> [!warning] Watch out          ->   > **Warning: Watch out**
> Body text                          >
                                     > Body text
```

The type name is preserved in the title, so `[!danger]`, `[!bug]` and `[!question]` stay
distinguishable even though they all render as ordinary blockquotes. A custom title is
appended after the type label; with no custom title, the type label stands alone.

`quote` and `cite` produce no label — a blockquote already conveys that, and a title
reading "Quote" adds nothing.

The blank `>` line after the title matters: without it, the title and first body line
merge into one paragraph and the bold heading stops looking like a heading.

Nested callouts (`> > [!tip]`) keep their nesting depth. Collapsible markers (`-`/`+`)
are dropped and reported, since nothing outside Obsidian folds.

---

## 3. Link resolution

`[[Note]]` is resolved by indexing the vault, mirroring Obsidian's own rule:

1. Exact vault-relative path match (`[[Folder/Note]]`).
2. Filename match; when several notes share a name, prefer one in the source note's
   folder, then the shortest path.
3. No match → emit the alias, or the raw target text, as plain text.

Output paths are relative to the converted file and URL-encoded, so `Other Note.md`
becomes `Other%20Note.md`. Percent-encoding is understood universally; unencoded spaces
break links in several parsers.

### Why heading anchors are dropped by default

`[[Note#My Section]]` needs an anchor like `#my-section`, but the slug rules differ:
GitHub strips punctuation one way, kramdown another, Pandoc prepends the section number
in some configurations, and Docusaurus lets authors override IDs entirely. A wrong
anchor lands the reader at the top of the page with no error — silently useless. The
link therefore points at the file, and the section name survives in the link text
(`[Note > My Section]`). `--heading-anchors` re-enables them when the target renderer is
known.

Same-file links (`[[#Heading]]`) keep their anchor, since dropping it would leave nothing
to link to at all.

### Why unresolved links become plain text

A link to a nonexistent file renders as a live link that 404s. Plain text is honest, and
every unresolved target appears in the report.

---

## 4. Embeds

| Embed | Output | Reason |
|---|---|---|
| Image | `![alt](path)` | Direct equivalent |
| Image with size (`\|300`) | `<img width="300">`, or plain image with `--no-html` | No Markdown size syntax exists |
| Note | Link, or inlined content with `--embed-mode inline` | Transclusion isn't a Markdown feature |
| PDF, video, audio | Link | No renderer inlines these from a Markdown link |

Inlining goes one level deep. Deeper recursion risks loops, and duplicating a note into
many files makes the output hard to maintain. `![[Note#Section]]` inlines only that
section, up to the next heading of equal or higher level.

---

## 5. Frontmatter

A YAML block is invisible in Obsidian and in static-site generators that consume it, but
in a plain previewer the closing `---` after text turns the whole block into a setext
heading — the note opens with a giant line reading "date created: ... tags:".

The default converts it to a bullet list, which reads correctly everywhere and keeps the
metadata visible:

```
- **date created:** 2026-07-27
- **tags:** WorldVeg/Omics_cowpea_SNP_calling
```

Use `--frontmatter keep` when the file is destined for a static-site generator that
parses the YAML, and `--frontmatter strip` when the metadata is noise.

The parser handles the common shapes — `key: value`, block lists under a key, and inline
`[a, b]` lists. Deeply nested YAML falls back to whatever it can flatten, so check the
output when frontmatter is complex.

---

## 6. Non-Obsidian repairs

These are ordinary Markdown problems that Obsidian happens to tolerate.

**Bare angle brackets.** `<filename>.sh` in prose is parsed as an unknown HTML tag and
removed, so the sentence renders as ".sh file". Escaping to `\<filename\>` is CommonMark
backslash-escaping and displays literally everywhere. Known HTML tags and autolinks
(`<https://…>`) are exempt, so intentional markup survives.

**`$SHELL_VARS`.** A line mentioning `$PATH` twice looks exactly like inline math to
GitHub, MkDocs-Material and Typora, which will render the text between the two `$` signs
as an equation. Only uppercase multi-character variables are escaped, since those are
almost never real math; single letters like `$x$` are left alone.

**Ragged tables.** Obsidian renders a table whose rows have fewer cells than the header;
several parsers reject the whole block. Rows are padded to the header's column count,
alignment markers are preserved, and columns are padded to a uniform width so the source
is readable too. Width is measured in display columns, so CJK text lines up.

**Missing blank lines.** python-markdown and kramdown require a blank line before a list,
heading or fenced block that follows a paragraph; Obsidian and CommonMark don't. One is
inserted where needed. This never merges or splits list items, so loose/tight list
rendering is unchanged.

**Line-leading `#tag`.** The most damaging Obsidian-ism in a plain previewer: a line of
tags becomes an `<h1>`. Backticks keep the tag visible while stopping the heading parse.
Mid-sentence tags are already harmless and are left alone; when a leading tag is escaped,
the other tags on that line are escaped too so the line looks consistent.

**`==highlight==` → bold.** `<mark>` is stripped by many sanitizers and means nothing in
non-HTML Pandoc output. Bold is the reliable choice. `--highlight mark` is available.

**Non-standard task states.** `- [/]` and `- [>]` print raw brackets outside Obsidian and
collapse to `- [ ]`. This loses "in progress" vs "not started" — worth mentioning if the
notes use them heavily.

---

## 7. Known lossy conversions

State these plainly rather than letting the user find them:

- Collapsible callouts become always-visible.
- Callout styling becomes plain blockquotes; only the type name survives, as text.
- Cross-file heading anchors point at the file, not the section.
- Block-reference links (`#^abc123`) lose their anchor.
- Custom task states collapse to unchecked.
- Note embeds become links unless inlining is requested.
- Dataview, Tasks and Templater blocks remain as inert code blocks.
- Canvas files (`.canvas`) aren't Markdown and aren't converted.
