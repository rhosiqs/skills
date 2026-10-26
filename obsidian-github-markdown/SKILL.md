---
name: obsidian-github-markdown
description: Convert Obsidian-flavored Markdown into standard, GitHub-compatible Markdown by rewriting wikilinks, embeds, callouts, highlights, tags and block IDs so the file renders correctly outside Obsidian. Use this whenever someone uploads or points at a note, vault, or .md file that contains [[wikilinks]], ![[embeds]], [!note] callouts, ==highlights==, %%comments%% or ^block-ids — and also when they ask to "clean up", "fix", "normalize", "de-Obsidian" or "make renderable on GitHub" any Markdown that came out of Obsidian, even if they don't name the specific syntax.
---

# Obsidian → standard Markdown

Obsidian's Markdown dialect breaks in ordinary previewers: `[[Wikilinks]]` render as
literal brackets, `> [!note]` callouts show a stray `[!note]` line, `![[image.png]]`
shows nothing at all, and a `#tag` at the start of a line silently becomes an `<h1>`.
This skill rewrites those constructs into plain Markdown that renders correctly on
GitHub, GitLab, VS Code and static-site generators.

**Target dialect:** GitHub-flavored Markdown. Callouts become GitHub alerts; wikilinks
become relative links when the target file actually exists, and plain text when it
doesn't (a dead link is worse than no link).

## Workflow

### 1. Find the vault root before converting

Link resolution is the whole game here. `[[Meeting Notes]]` has no path in it — the
converter has to search the vault to discover it lives at `Work/Meetings/Meeting Notes.md`.
Getting the root wrong means every link silently degrades to plain text.

- If the user uploaded a folder or zip, unpack it and use the top-level directory.
- If they uploaded loose `.md` files with no attachments, the uploads directory is the root.
- If they uploaded a single note that references images or other notes you don't have,
  say so plainly before converting — those links will come out as plain text, and it's
  better for the user to hear that up front than to discover it in the output.

### 2. Run the converter

```bash
python scripts/obsidian_to_md.py <input-file-or-dir> --vault <vault-root> --out <output-dir>
```

Useful flags:

| Flag | Effect |
|---|---|
| `--embed-mode inline` | Splice embedded notes' content in, instead of linking to them |
| `--highlight mark` | `==x==` → `<mark>x</mark>` instead of `**x**` |
| `--strip-frontmatter` | Drop the YAML block (kept by default — GitHub renders it as a table) |
| `--keep-tags` | Leave line-leading `#tags` alone instead of wrapping them in backticks |
| `--no-copy-assets` | Don't copy referenced images/attachments into the output tree |
| `--json` | Machine-readable report |

The script prints a report: what was converted, which links couldn't be resolved, and
which constructs lost information in translation.

### 3. Report honestly on what changed

Some Obsidian features have no standard equivalent, so the conversion is genuinely
lossy. Tell the user about the lossy parts rather than presenting the output as a clean
round-trip. Always surface:

- **Unresolved links** — listed by name in the report. These became plain text. They
  usually mean the vault root was wrong or the note lives outside what was uploaded.
- **Collapsible callouts** (`> [!note]-`) — GitHub alerts can't fold, so they're flattened.
- **Note embeds** — converted to links by default; mention `--embed-mode inline` as the
  alternative if they wanted the content to actually appear.
- **Dataview / Tasks / Templater blocks** — left untouched as fenced code blocks, since
  they're queries, not content. Point them out; the user may want them deleted.

### 4. Present the output

Copy the output directory's files to the outputs directory and present them. If more
than a handful of files were converted, zip the directory and present that instead.

## What gets converted

| Obsidian | Standard Markdown |
|---|---|
| `[[Note]]` | `[Note](path/Note.md)`, or plain text if the file doesn't exist |
| `[[Note\|Alias]]` | `[Alias](path/Note.md)` |
| `[[Note#Heading]]` | `[Note > Heading](path/Note.md#heading)` |
| `[[#Heading]]` | `[Heading](#heading)` |
| `[[Note#^block]]` | Link to the note (block anchors don't exist elsewhere) |
| `![[image.png]]` | `![image](path/image.png)` |
| `![[image.png\|300]]` | `<img src="path/image.png" width="300">` |
| `![[Note]]` | `*Embedded note:* [Note](path/Note.md)` |
| `![[file.pdf]]` | `[file.pdf](path/file.pdf)` |
| `> [!warning] Title` | `> [!WARNING]` + `> **Title**` |
| `==highlight==` | `**highlight**` |
| `%%comment%%` | removed |
| `^block-id` | removed |
| `#tag` at line start | `` `#tag` `` (otherwise it renders as a heading) |
| `- [/]`, `- [>]` | `- [ ]` (GitHub only knows `[ ]` and `[x]`) |

Full callout-type mapping and the reasoning behind each rule: `references/conversion-rules.md`.
Read it when a conversion looks wrong, when the user asks why something changed, or when
you're editing a file by hand instead of running the script.

## Things that must not be touched

The single most common way to get this wrong is rewriting syntax that was never meant
to be rewritten. Inside fenced code blocks, inline code spans, `$math$` and `$$math$$`,
Obsidian syntax is content — a tutorial about Obsidian is full of `[[examples]]` that
must survive verbatim. The script protects these regions before doing anything else;
preserve that behavior in any edit, and apply the same discipline when editing by hand.

Also leave alone: YAML frontmatter (unless asked), footnotes, tables, Mermaid blocks,
task lists in `[ ]`/`[x]` form, and math — all of these already render correctly on GitHub.

## If code execution isn't available

Convert by hand using the tables above, working through the file top to bottom, and
skipping every fenced block, inline code span and math span. Mention that hand
conversion can't verify whether link targets exist, so state the assumption you made
for each `[[link]]` rather than silently guessing.
