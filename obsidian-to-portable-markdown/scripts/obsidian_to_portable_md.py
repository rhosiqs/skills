#!/usr/bin/env python3
"""Convert Obsidian-flavored Markdown into maximally portable Markdown.

Targets the common denominator across CommonMark, python-markdown, kramdown,
Pandoc, marked, VS Code, Typora and static-site generators — not any single
renderer's extensions. Code blocks, inline code and math are never rewritten.

Usage:
    python obsidian_to_portable_md.py INPUT [INPUT ...] --out OUTDIR [--vault ROOT]
"""

import argparse
import json
import os
import re
import shutil
import sys
import unicodedata
from pathlib import Path
from urllib.parse import quote

# Obsidian callout type -> human label used in the bold title line.
CALLOUT_LABELS = {
    "note": "Note", "info": "Info", "todo": "To do", "abstract": "Abstract",
    "summary": "Summary", "tldr": "TL;DR", "tip": "Tip", "hint": "Hint",
    "important": "Important", "success": "Success", "check": "Check",
    "done": "Done", "question": "Question", "help": "Help", "faq": "FAQ",
    "warning": "Warning", "caution": "Caution", "attention": "Attention",
    "failure": "Failure", "fail": "Failure", "missing": "Missing",
    "danger": "Danger", "error": "Error", "bug": "Bug", "example": "Example",
    "quote": "", "cite": "",
}

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".avif"}
EMBEDDABLE_MEDIA = {".pdf", ".mp4", ".webm", ".mp3", ".wav", ".ogg", ".m4a", ".mov"}

# Tags in angle brackets that are real HTML and must survive escaping.
HTML_TAGS = {
    "a", "abbr", "b", "blockquote", "br", "center", "code", "del", "details",
    "div", "em", "font", "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i", "img",
    "ins", "kbd", "li", "mark", "ol", "p", "picture", "pre", "q", "s", "samp",
    "small", "span", "strong", "sub", "summary", "sup", "table", "tbody", "td",
    "tfoot", "th", "thead", "tr", "u", "ul", "var", "video", "audio", "source",
}

PLACEHOLDER = "\x00PH{}\x00"

WIKILINK_RE = re.compile(r"(!?)\[\[([^\[\]]+?)\]\]")
COMMENT_RE = re.compile(r"%%.*?%%", re.DOTALL)
HIGHLIGHT_RE = re.compile(r"==([^=\n]+)==")
BLOCK_ID_TRAILING_RE = re.compile(r"[ \t]+\^[A-Za-z0-9][A-Za-z0-9-]*[ \t]*$")
BLOCK_ID_LINE_RE = re.compile(r"^\s*\^[A-Za-z0-9][A-Za-z0-9-]*\s*$")
LEADING_TAG_RE = re.compile(r"^(\s*)(#[^\s#`]+)")
CALLOUT_RE = re.compile(
    r"^(?P<indent>[ \t]*)(?P<marks>(?:>[ \t]?)+)\[!(?P<type>[^\]\s]+)\](?P<fold>[+-]?)[ \t]*(?P<title>.*)$"
)
TASK_RE = re.compile(r"^(\s*[-*+]\s+\[)([^\]xX ])(\]\s)")
ANGLE_RE = re.compile(r"<([A-Za-z_][A-Za-z0-9_.()|/ -]*)>")
SHELL_VAR_RE = re.compile(r"(?<![\\\w$])\$([A-Z][A-Z0-9_]+)\b")
TABLE_SEP_RE = re.compile(r"^\s*\|?[\s:|-]*-[\s:|-]*\|?\s*$")
BLOCK_START_RE = re.compile(r"^\s{0,3}(#{1,6}\s|>|([-*+]|\d+[.)])\s|\|)")
PARAGRAPH_RE = re.compile(r"^\s{0,3}(#{1,6}\s|>|([-*+]|\d+[.)])\s|\||---|===|\s*$)")


class Report:
    def __init__(self):
        self.unresolved = []
        self.counts = {}
        self.notes = []

    def bump(self, key, n=1):
        self.counts[key] = self.counts.get(key, 0) + n


# --------------------------------------------------------------------------
# Protecting regions that must never be rewritten
# --------------------------------------------------------------------------

def protect(text):
    store = []

    def stash(match):
        store.append(match.group(0))
        return PLACEHOLDER.format(len(store) - 1)

    text = re.sub(
        r"^(?P<f>```+|~~~+)[^\n]*\n.*?(?:^(?P=f)[ \t]*$|\Z)",
        stash, text, flags=re.DOTALL | re.MULTILINE,
    )
    text = re.sub(r"\$\$.*?\$\$", stash, text, flags=re.DOTALL)
    text = re.sub(r"(?<!`)(`+)(?!`).*?(?<!`)\1(?!`)", stash, text, flags=re.DOTALL)
    text = re.sub(r"(?<![\\$])\$(?!\s)[^\n$]*?(?<!\s)\$(?!\d)", stash, text)
    text = re.sub(r"<(https?://|mailto:)[^>\s]*>", stash, text)
    text = re.sub(r"<!--.*?-->", stash, text, flags=re.DOTALL)
    return text, store


def restore(text, store):
    for i, original in enumerate(store):
        text = text.replace(PLACEHOLDER.format(i), original)
    return text


def is_block_placeholder(line, store):
    """True when a whole line is a placeholder standing in for a fenced block."""
    match = re.fullmatch(r"\x00PH(\d+)\x00", line.strip())
    if not match:
        return False
    content = store[int(match.group(1))]
    return content.startswith("```") or content.startswith("~~~")


# --------------------------------------------------------------------------
# Vault index and link resolution
# --------------------------------------------------------------------------

class Vault:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.by_stem = {}
        self.by_relpath = {}
        for path in self.root.rglob("*"):
            if not path.is_file() or any(p.startswith(".") for p in path.parts):
                continue
            rel = path.relative_to(self.root)
            self.by_stem.setdefault(path.stem.lower(), []).append(path)
            self.by_stem.setdefault(path.name.lower(), []).append(path)
            self.by_relpath.setdefault(str(rel.with_suffix("")).lower().replace("\\", "/"), []).append(path)
            self.by_relpath.setdefault(str(rel).lower().replace("\\", "/"), []).append(path)

    def resolve(self, target, source=None):
        key = target.strip().lower().replace("\\", "/").lstrip("./")
        candidates = self.by_relpath.get(key) or self.by_stem.get(key) or []
        if not candidates:
            return None
        if len(candidates) > 1 and source:
            same_dir = [c for c in candidates if c.parent == Path(source).parent]
            if same_dir:
                return same_dir[0]
        return sorted(candidates, key=lambda p: (len(p.parts), str(p)))[0]


def slugify(heading):
    text = unicodedata.normalize("NFKC", heading).strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text)


def rel_url(target, from_file):
    rel = os.path.relpath(str(target), str(Path(from_file).parent))
    return quote(rel.replace(os.sep, "/"), safe="/._-()")


# --------------------------------------------------------------------------
# Wikilinks and embeds
# --------------------------------------------------------------------------

def split_target(raw):
    body, _, alias = raw.partition("|")
    path, sep, frag = body.partition("#")
    return path.strip(), (frag.strip() if sep else ""), (alias.strip() or None)


def convert_links(text, ctx):
    def replace(match):
        is_embed = match.group(1) == "!"
        path, frag, alias = split_target(match.group(2))
        return (render_embed if is_embed else render_link)(path, frag, alias, ctx)

    return WIKILINK_RE.sub(replace, text)


def render_link(path, frag, alias, ctx):
    display = alias or (f"{path} > {frag.lstrip('^')}" if frag and path else (path or frag.lstrip("^")))

    if not path:
        ctx["report"].bump("wikilinks_converted")
        return f"[{display}](#{slugify(frag)})"

    target = ctx["vault"].resolve(path, ctx["source"]) if ctx["vault"] else None
    if not target:
        ctx["report"].bump("wikilinks_unresolved")
        ctx["report"].unresolved.append((str(ctx["source"]), path))
        return display

    url = rel_url(ctx["out_for"](target), ctx["out_file"])
    if frag and not frag.startswith("^"):
        # Heading anchors are generated differently by every renderer, so only
        # emit one when the user opted in.
        if ctx["opts"].heading_anchors:
            url += f"#{slugify(frag)}"
        else:
            ctx["report"].bump("heading_anchors_dropped")
    ctx["assets"].add(target)
    ctx["report"].bump("wikilinks_converted")
    return f"[{display}]({url})"


def render_embed(path, frag, alias, ctx):
    if not path:
        return render_link(path, frag, alias, ctx)

    target = ctx["vault"].resolve(path, ctx["source"]) if ctx["vault"] else None
    if not target:
        ctx["report"].bump("embeds_unresolved")
        ctx["report"].unresolved.append((str(ctx["source"]), path))
        return f"*(missing embed: {path})*"

    ext = target.suffix.lower()
    ctx["assets"].add(target)

    if ext in IMAGE_EXT:
        url = rel_url(ctx["out_for"](target), ctx["out_file"])
        ctx["report"].bump("images_converted")
        if alias and re.fullmatch(r"\d+(x\d+)?", alias):
            if ctx["opts"].allow_html:
                w, _, h = alias.partition("x")
                dims = f' width="{w}"' + (f' height="{h}"' if h else "")
                ctx["report"].bump("image_sizes_as_html")
                return f'<img src="{url}" alt="{target.stem}"{dims}>'
            ctx["report"].bump("image_sizes_dropped")
            return f"![{target.stem}]({url})"
        return f"![{alias or target.stem}]({url})"

    if ext == ".md":
        return embed_note(target, alias, frag, ctx)

    url = rel_url(ctx["out_for"](target), ctx["out_file"])
    ctx["report"].bump("media_linked")
    if ext in EMBEDDABLE_MEDIA:
        ctx["report"].notes.append(f"{target.name} was an inline media embed; converted to a link.")
    return f"[{alias or target.name}]({url})"


def embed_note(target, alias, frag, ctx):
    if ctx["opts"].embed_mode == "inline" and ctx["depth"] < 1:
        try:
            body = strip_frontmatter(target.read_text(encoding="utf-8"))[1]
        except OSError:
            body = ""
        if frag and not frag.startswith("^"):
            body = extract_section(body, frag)
        inner = dict(ctx, depth=ctx["depth"] + 1, source=target)
        ctx["report"].bump("notes_inlined")
        return convert_body(body.strip(), inner)

    ctx["report"].bump("notes_embedded_as_link")
    return "*Embedded note:* " + render_link(str(target.stem), frag, alias, ctx)


def extract_section(body, heading):
    out, level = [], None
    for line in body.split("\n"):
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match:
            if level is None and slugify(match.group(2)) == slugify(heading):
                level = len(match.group(1))
                continue
            if level is not None and len(match.group(1)) <= level:
                break
        if level is not None:
            out.append(line)
    return "\n".join(out) if level is not None else body


# --------------------------------------------------------------------------
# Callouts -> plain bold-titled blockquotes
# --------------------------------------------------------------------------

def convert_callouts(text, report):
    out = []
    for line in text.split("\n"):
        match = CALLOUT_RE.match(line)
        if not match:
            out.append(line)
            continue

        indent = match.group("indent")
        marks = "> " * match.group("marks").count(">")
        ctype = match.group("type").strip().lower()
        title = match.group("title").strip()
        label = CALLOUT_LABELS.get(ctype, ctype.capitalize())

        if title and label:
            heading = f"{label}: {title}"
        else:
            heading = title or label

        report.bump("callouts_converted")
        if heading:
            out.append(f"{indent}{marks}**{heading}**")
            out.append(f"{indent}{marks.rstrip()}")
        if match.group("fold"):
            report.notes.append(
                f"Collapsible callout [!{ctype}] was flattened — no portable equivalent."
            )
    return "\n".join(out)


# --------------------------------------------------------------------------
# Tables
# --------------------------------------------------------------------------

def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    cells, current, escaped = [], "", False
    for ch in line:
        if escaped:
            current += ch
            escaped = False
        elif ch == "\\":
            current += ch
            escaped = True
        elif ch == "|":
            cells.append(current.strip())
            current = ""
        else:
            current += ch
    cells.append(current.strip())
    return cells


def alignment(cell):
    cell = cell.strip()
    left, right = cell.startswith(":"), cell.endswith(":")
    return "center" if left and right else "right" if right else "left" if left else None


def visible_width(cell, store):
    """Display width of a cell, resolving placeholders and wide CJK glyphs."""
    text = re.sub(r"\x00PH(\d+)\x00", lambda m: store[int(m.group(1))], cell)
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text)


def normalize_tables(text, store, report):
    """Pad ragged tables so strict parsers accept them."""
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        if (i + 1 < len(lines) and "|" in lines[i]
                and TABLE_SEP_RE.match(lines[i + 1]) and "|" in lines[i + 1]):
            header = split_row(lines[i])
            aligns = [alignment(c) for c in split_row(lines[i + 1])]
            rows, j = [], i + 2
            while j < len(lines) and "|" in lines[j] and lines[j].strip():
                rows.append(split_row(lines[j]))
                j += 1

            width = max([len(header)] + [len(r) for r in rows])
            header += [""] * (width - len(header))
            aligns += [None] * (width - len(aligns))
            rows = [r + [""] * (width - len(r)) for r in rows]

            sizes = [max([visible_width(header[c], store)]
                         + [visible_width(r[c], store) for r in rows] + [3])
                     for c in range(width)]
            sep = []
            for c in range(width):
                bar = "-" * sizes[c]
                sep.append({"center": f":{bar[:-2]}:" if sizes[c] > 2 else ":-:",
                            "right": f"{bar[:-1]}:",
                            "left": f":{bar[1:]}"}.get(aligns[c], bar))

            def emit(cells):
                padded = [cells[c] + " " * (sizes[c] - visible_width(cells[c], store))
                          for c in range(width)]
                return "| " + " | ".join(padded) + " |"

            if out and out[-1].strip():
                out.append("")
            out.append(emit(header))
            out.append("| " + " | ".join(sep) + " |")
            out.extend(emit(r) for r in rows)
            if j < len(lines) and lines[j].strip():
                out.append("")
            report.bump("tables_normalized")
            i = j
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


# --------------------------------------------------------------------------
# Line-level cleanups
# --------------------------------------------------------------------------

def convert_lines(text, opts, report):
    out = []
    for line in text.split("\n"):
        if BLOCK_ID_LINE_RE.match(line):
            report.bump("block_ids_removed")
            continue
        new = BLOCK_ID_TRAILING_RE.sub("", line)
        if new != line:
            report.bump("block_ids_removed")
        line = new

        if opts.escape_tags and LEADING_TAG_RE.match(line):
            tagged = re.sub(r"(?<![\w`])#[^\s#`]+", lambda m: f"`{m.group(0)}`", line)
            if tagged != line:
                report.bump("tags_escaped")
            line = tagged

        if TASK_RE.match(line):
            report.bump("task_states_normalized")
            line = TASK_RE.sub(r"\1 \3", line, count=1)

        out.append(line)
    return "\n".join(out)


def escape_angles(text, report):
    """Bare <placeholder> text is swallowed as an HTML tag by every renderer."""
    def replace(match):
        name = match.group(1).split()[0].split(".")[0].lower()
        if name in HTML_TAGS or name.rstrip("/") in HTML_TAGS:
            return match.group(0)
        report.bump("angle_brackets_escaped")
        return "\\<" + match.group(1) + "\\>"

    return ANGLE_RE.sub(replace, text)


def escape_shell_vars(text, report):
    """$VAR pairs on one line get parsed as math by renderers with math support."""
    def replace(match):
        report.bump("shell_vars_escaped")
        return "\\$" + match.group(1)

    return SHELL_VAR_RE.sub(replace, text)


def space_blocks(text, store, report):
    """Insert the blank line that stricter parsers require before a block."""
    lines = text.split("\n")
    out = []
    for line in lines:
        # Headings and fenced blocks need separating from anything non-blank.
        # Lists, quotes and tables only need it after a plain paragraph line —
        # a blank line between sibling list items would change the list's
        # rendering, so the rule stays conservative there.
        strict = re.match(r"^#{1,6}\s", line) or is_block_placeholder(line, store)
        loose = BLOCK_START_RE.match(line)
        previous = out[-1] if out else ""
        if (strict or loose) and previous.strip():
            if strict or (not PARAGRAPH_RE.match(previous)
                          and not is_block_placeholder(previous, store)):
                out.append("")
                report.bump("blank_lines_inserted")
        out.append(line)
    return "\n".join(out)


# --------------------------------------------------------------------------
# Frontmatter
# --------------------------------------------------------------------------

def strip_frontmatter(text):
    match = re.match(r"^---\r?\n(.*?)\r?\n---[ \t]*\r?\n?", text, re.DOTALL)
    if not match:
        return "", text
    return match.group(1), text[match.end():]


def frontmatter_to_list(block):
    """Render simple YAML frontmatter as a plain bullet list."""
    entries, key, values = [], None, []

    def flush():
        if key is not None:
            entries.append((key, ", ".join(v for v in values if v)))

    for raw in block.split("\n"):
        if not raw.strip():
            continue
        item = re.match(r"^\s*-\s+(.*)$", raw)
        if item and key is not None:
            values.append(item.group(1).strip().strip("\"'"))
            continue
        pair = re.match(r"^([^:]+):\s*(.*)$", raw)
        if pair:
            flush()
            key = pair.group(1).strip()
            value = pair.group(2).strip()
            if value.startswith("[") and value.endswith("]"):
                value = ", ".join(v.strip().strip("\"'") for v in value[1:-1].split(","))
            values = [value.strip("\"'")] if value else []
    flush()
    if not entries:
        return ""
    return "\n".join(f"- **{k}:** {v}" if v else f"- **{k}**" for k, v in entries) + "\n"


# --------------------------------------------------------------------------
# Main conversion
# --------------------------------------------------------------------------

def convert_body(text, ctx):
    opts, report = ctx["opts"], ctx["report"]
    text, store = protect(text)

    removed = len(COMMENT_RE.findall(text))
    if removed:
        report.bump("comments_removed", removed)
    text = COMMENT_RE.sub("", text)

    if opts.escape_angle:
        text = escape_angles(text, report)
    if opts.escape_dollar:
        text = escape_shell_vars(text, report)

    text = convert_callouts(text, report)
    text = convert_links(text, ctx)

    if opts.highlight != "keep":
        repl = r"**\1**" if opts.highlight == "bold" else r"<mark>\1</mark>"
        hits = len(HIGHLIGHT_RE.findall(text))
        if hits:
            report.bump("highlights_converted", hits)
        text = HIGHLIGHT_RE.sub(repl, text)

    text = convert_lines(text, opts, report)
    if opts.normalize_tables:
        text = normalize_tables(text, store, report)
    if opts.space_blocks:
        text = space_blocks(text, store, report)

    if removed:
        text = re.sub(r"(?<=\S)[ \t]{2,}(?=\S)", " ", text)
        text = re.sub(r"^[ \t]+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return restore(text, store)


def convert_file(source, out_file, vault, opts, report, out_for):
    raw = Path(source).read_text(encoding="utf-8")
    block, body = strip_frontmatter(raw)

    header = ""
    if block:
        if opts.frontmatter == "list":
            header = frontmatter_to_list(block)
            if header:
                header += "\n"
                report.bump("frontmatter_converted")
        elif opts.frontmatter == "keep":
            header = f"---\n{block}\n---\n\n"
        else:
            report.bump("frontmatter_stripped")

    ctx = {
        "vault": vault, "source": Path(source), "out_file": Path(out_file),
        "opts": opts, "report": report, "assets": set(), "depth": 0,
        "out_for": out_for,
    }
    result = (header + convert_body(body.lstrip("\n"), ctx)).rstrip() + "\n"
    Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    Path(out_file).write_text(result, encoding="utf-8")
    return ctx["assets"]


def main():
    ap = argparse.ArgumentParser(description="Convert Obsidian Markdown to portable Markdown.")
    ap.add_argument("inputs", nargs="+", help="Markdown files or directories to convert")
    ap.add_argument("--out", required=True, help="Output directory")
    ap.add_argument("--vault", help="Vault root used to resolve links (default: common parent of inputs)")
    ap.add_argument("--frontmatter", choices=["list", "keep", "strip"], default="list",
                    help="YAML frontmatter: bullet list (default), keep verbatim, or remove")
    ap.add_argument("--embed-mode", choices=["link", "inline"], default="link")
    ap.add_argument("--highlight", choices=["bold", "mark", "keep"], default="bold")
    ap.add_argument("--no-html", dest="allow_html", action="store_false",
                    help="Never emit HTML; image sizes are dropped instead")
    ap.add_argument("--heading-anchors", action="store_true",
                    help="Keep #heading fragments on links (anchor rules vary by renderer)")
    ap.add_argument("--keep-tags", dest="escape_tags", action="store_false")
    ap.add_argument("--keep-angle", dest="escape_angle", action="store_false",
                    help="Leave bare <placeholder> text unescaped")
    ap.add_argument("--keep-dollar", dest="escape_dollar", action="store_false",
                    help="Leave $SHELL_VARS unescaped")
    ap.add_argument("--no-table-normalize", dest="normalize_tables", action="store_false")
    ap.add_argument("--no-block-spacing", dest="space_blocks", action="store_false")
    ap.add_argument("--no-copy-assets", dest="copy_assets", action="store_false")
    ap.add_argument("--json", action="store_true")
    ap.set_defaults(allow_html=True, escape_tags=True, escape_angle=True,
                    escape_dollar=True, normalize_tables=True, space_blocks=True,
                    copy_assets=True, heading_anchors=False)
    opts = ap.parse_args()

    files = []
    for item in opts.inputs:
        p = Path(item)
        if p.is_dir():
            files.extend(sorted(f for f in p.rglob("*.md")
                                if not any(part.startswith(".") for part in f.parts)))
        elif p.is_file():
            files.append(p)
        else:
            print(f"warning: {item} not found", file=sys.stderr)
    if not files:
        print("No markdown files found.", file=sys.stderr)
        return 1

    vault_root = Path(opts.vault).resolve() if opts.vault else Path(
        os.path.commonpath([str(f.resolve().parent) for f in files]))
    vault = Vault(vault_root)
    out_root = Path(opts.out).resolve()

    def out_for(path):
        path = Path(path).resolve()
        try:
            return out_root / path.relative_to(vault_root)
        except ValueError:
            return out_root / path.name

    report = Report()
    all_assets = set()
    for f in files:
        all_assets |= convert_file(f.resolve(), out_for(f), vault, opts, report, out_for)
        report.bump("files_converted")

    if opts.copy_assets:
        for asset in all_assets:
            if asset.suffix.lower() == ".md":
                continue
            dest = out_for(asset)
            if not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(asset, dest)
                report.bump("assets_copied")

    payload = {
        "output_dir": str(out_root),
        "counts": report.counts,
        "unresolved_links": [{"file": f, "target": t} for f, t in report.unresolved],
        "notes": sorted(set(report.notes)),
    }
    if opts.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Converted {report.counts.get('files_converted', 0)} file(s) -> {out_root}")
        for k, v in sorted(report.counts.items()):
            print(f"  {k}: {v}")
        if report.unresolved:
            print("\nUnresolved links (left as plain text):")
            for f, t in report.unresolved:
                print(f"  [[{t}]] in {Path(f).name}")
        for note in sorted(set(report.notes)):
            print(f"  note: {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
