---
name: obsidian-to-portable-markdown
description: Convert Obsidian-flavored Markdown into maximally portable Markdown that renders correctly in any previewer — VS Code, Typora, Pandoc, MkDocs, Jekyll, Hugo, Docusaurus, GitLab, plain CommonMark. Rewrites wikilinks, embeds, callouts, highlights, tags, block IDs and YAML frontmatter, and also repairs non-Obsidian hazards like bare angle brackets, stray $VARIABLES and ragged tables. Use this whenever someone uploads or points at a note or vault containing [[wikilinks]], ![[embeds]], [!note] callouts, ==highlights==, %%comments%% or ^block-ids, or asks to "clean up", "normalize", "de-Obsidian" or make Markdown "work everywhere" or "render in any previewer". For output aimed specifically at GitHub, prefer a GitHub-targeted skill if one is installed, since GitHub alerts render better there.
---

# Obsidian → portable Markdown

Obsidian's dialect breaks outside Obsidian, and the usual fix — converting to
GitHub-flavored Markdown — just trades one dialect for another. GitHub alerts
(`> [!NOTE]`) show a literal `[!NOTE]` line in Typora, Pandoc and MkDocs. This skill
targets the common denominator instead: constructs that render the same way in
essentially every Markdown tool.

**Target dialect:** portable Markdown. Callouts become bold-titled blockquotes,
frontmatter becomes a visible metadata list, and wikilinks become relative links only
when the target file actually exists. Minimal inline HTML is permitted where Markdown
has no equivalent (image sizing); `--no-html` removes even that.

## Workflow

### 1. Find the vault root before converting

Link resolution is the whole game. `[[Meeting Notes]]` carries no path — the converter
has to search the vault to find that it lives at `Work/Meetings/Meeting Notes.md`. A
wrong root means every link silently degrades to plain text.

- Uploaded folder or zip: unpack it, use the top-level directory.
- Loose `.md` files with no attachments: the uploads directory is the root.
- A single note referencing other notes you don't have: say so before converting. Those
  links will come out as plain text, and it's better said up front than discovered in
  the output.

### 2. Run the converter

```bash
python scripts/obsidian_to_portable_md.py <input-file-or-dir> --vault <vault-root> --out <output-dir>
```

| Flag | Effect |
|---|---|
| `--frontmatter keep\|strip` | Keep the YAML block verbatim, or delete it (default: bullet list) |
| `--no-html` | Emit zero HTML; image sizes are dropped instead of using `<img>` |
| `--embed-mode inline` | Splice embedded notes' content in rather than linking |
| `--heading-anchors` | Keep `#heading` fragments on cross-file links |
| `--highlight mark\|keep` | `==x==` as `<mark>` or untouched, instead of bold |
| `--keep-angle`, `--keep-dollar`, `--keep-tags` | Disable individual escaping rules |
| `--no-table-normalize`, `--no-block-spacing` | Disable layout repairs |
| `--json` | Machine-readable report |

The report lists what changed, which links failed to resolve, and what lost information.

### 3. Report honestly on what changed

The conversion is genuinely lossy in places. Say so rather than presenting it as a clean
round-trip. Always surface:

- **Unresolved links** — named in the report. They became plain text, usually because
  the vault root was wrong or the target note wasn't uploaded.
- **Collapsible callouts** (`> [!note]-`) — now always visible, which changes how a long
  folded section reads.
- **Dropped heading anchors** — cross-file `[[Note#Section]]` links point at the file,
  not the section, because every renderer slugifies headings differently. `--heading-anchors`
  restores them if the user knows their target renderer.
- **Dataview, Tasks and Templater blocks** — left as inert code blocks. They were dynamic
  queries and can't be reproduced statically; the user may want them deleted.

### 4. Present the output

Copy the converted files to the outputs directory and present them. For more than a
handful of files, zip the directory and present that.

## What gets converted

| Obsidian | Portable Markdown |
|---|---|
| `[[Note]]` | `[Note](path/Note.md)`, or plain text if the file doesn't exist |
| `[[Note\|Alias]]` | `[Alias](path/Note.md)` |
| `[[Note#Heading]]` | `[Note > Heading](path/Note.md)` — anchor dropped by default |
| `[[#Heading]]` | `[Heading](#heading)` |
| `![[image.png]]` | `![image](path/image.png)` |
| `![[image.png\|300]]` | `<img src="..." width="300">`, or plain image with `--no-html` |
| `![[Note]]` | `*Embedded note:* [Note](path/Note.md)` |
| `> [!warning] Title` | `> **Warning: Title**` |
| `==highlight==` | `**highlight**` |
| YAML frontmatter | `- **key:** value` bullet list |
| `%%comment%%`, `^block-id` | removed |
| `#tag` at line start | `` `#tag` `` |
| `- [/]`, `- [>]` | `- [ ]` |

## Repairs that aren't Obsidian syntax

Notes written in Obsidian routinely contain plain Markdown that Obsidian tolerates and
other renderers do not. These are fixed too, because the user's real goal is a file that
previews correctly, not a narrow syntax translation:

- **Bare `<placeholder>`** → `\<placeholder\>`. Every renderer parses `<filename>` as an
  HTML tag and deletes it. Real HTML tags (`<img>`, `<br>`, `<details>`) and autolinks
  are left alone.
- **`$SHELL_VARS`** → `\$SHELL_VARS`. Two `$` signs on one line get parsed as inline math
  by renderers with math support, swallowing the text between them.
- **Ragged tables** — padded to equal column counts and widths. Obsidian accepts rows with
  missing trailing cells; stricter parsers drop the table entirely.
- **Missing blank lines** before headings, lists, blockquotes and fenced blocks.
  python-markdown and kramdown need them; Obsidian doesn't.

Full rules and reasoning: `references/conversion-rules.md`. Read it when a conversion
looks wrong, when the user asks why something changed, or when converting by hand.

## Things that must not be touched

The commonest failure mode is rewriting syntax that was never meant to be rewritten.
Inside fenced code blocks, inline code, `$math$`, `$$math$$` and autolinks, Obsidian
syntax is content — a note *about* Obsidian is full of `[[examples]]` that must survive
verbatim. The script protects these regions before doing anything else; preserve that
behavior in any edit, and apply the same discipline when editing by hand.

Also left alone: footnotes, Mermaid blocks, math, strikethrough, and task lists already
in `[ ]`/`[x]` form.

## If code execution isn't available

Convert by hand using the tables above, top to bottom, skipping every fenced block,
inline code span and math span. Say which assumption you made for each `[[link]]` — hand
conversion can't verify whether a target file exists, and a silent guess is worse than a
stated one.
