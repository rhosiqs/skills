#!/usr/bin/env python3
"""Convert Obsidian-flavored Markdown into standard (GitHub-compatible) Markdown.

Handles wikilinks, embeds, callouts, highlights, tags, block IDs and comments,
while leaving code blocks, inline code and math untouched.

Usage:
    python obsidian_to_md.py INPUT [INPUT ...] --out OUTDIR [--vault VAULT_ROOT]

Run with --help for all options.
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

# --------------------------------------------------------------------------
# Callout type -> GitHub alert type.
# GitHub only supports NOTE, TIP, IMPORTANT, WARNING, CAUTION.
# Anything mapped to None becomes a plain blockquote.
# --------------------------------------------------------------------------
CALLOUT_MAP = {
    "note": "NOTE", "info": "NOTE", "todo": "NOTE", "abstract": "NOTE",
    "summary": "NOTE", "tldr": "NOTE", "example": "NOTE", "question": "NOTE",
    "help": "NOTE", "faq": "NOTE",
    "tip": "TIP", "hint": "TIP", "success": "TIP", "check": "TIP", "done": "TIP",
    "important": "IMPORTANT",
    "warning": "WARNING", "caution": "WARNING", "attention": "WARNING",
    "danger": "CAUTION", "error": "CAUTION", "bug": "CAUTION",
    "failure": "CAUTION", "fail": "CAUTION", "missing": "CAUTION",
    "quote": None, "cite": None,
}

# Default title shown when a callout has no custom title and its type is lost
# in translation (e.g. "example" -> NOTE).
TITLE_WHEN_LOSSY = {
    "todo": "To do", "abstract": "Abstract", "summary": "Summary",
    "tldr": "TL;DR", "example": "Example", "question": "Question",
    "help": "Help", "faq": "FAQ", "success": "Success", "check": "Check",
    "done": "Done", "danger": "Danger", "error": "Error", "bug": "Bug",
    "failure": "Failure", "fail": "Failure", "missing": "Missing",
    "info": "Info", "hint": "Hint", "attention": "Attention",
    "caution": "Caution",
}

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".avif"}
EMBEDDABLE_MEDIA = {".pdf", ".mp4", ".webm", ".mp3", ".wav", ".ogg", ".m4a", ".mov"}

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


class Report:
    def __init__(self):
        self.unresolved = []      # (source_file, link_target)
        self.counts = {}
        self.notes = []           # human-readable warnings

    def bump(self, key, n=1):
        self.counts[key] = self.counts.get(key, 0) + n


# --------------------------------------------------------------------------
# Protecting regions that must never be rewritten
# --------------------------------------------------------------------------

def protect(text):
    """Replace code blocks, inline code and math with placeholders."""
    store = []

    def stash(match):
        store.append(match.group(0))
        return PLACEHOLDER.format(len(store) - 1)

    # Fenced code blocks (``` or ~~~), including unterminated ones.
    text = re.sub(
        r"^(?P<f>```+|~~~+)[^\n]*\n.*?(?:^(?P=f)[ \t]*$|\Z)",
        stash, text, flags=re.DOTALL | re.MULTILINE,
    )
    # Display math, then inline code, then inline math.
    text = re.sub(r"\$\$.*?\$\$", stash, text, flags=re.DOTALL)
    text = re.sub(r"(?<!`)(`+)(?!`).*?(?<!`)\1(?!`)", stash, text, flags=re.DOTALL)
    text = re.sub(r"(?<![\\$])\$(?!\s)[^\n$]*?(?<!\s)\$(?!\d)", stash, text)
    # HTML comments are already invisible in both renderers; leave them intact.
    text = re.sub(r"<!--.*?-->", stash, text, flags=re.DOTALL)
    return text, store


def restore(text, store):
    for i, original in enumerate(store):
        text = text.replace(PLACEHOLDER.format(i), original)
    return text


# --------------------------------------------------------------------------
# Vault index and link resolution
# --------------------------------------------------------------------------

class Vault:
    """Index of every file in the vault, for resolving wikilink targets."""

    def __init__(self, root):
        self.root = Path(root).resolve()
        self.by_stem = {}       # "note name" -> [paths]
        self.by_relpath = {}    # "folder/note name" -> [paths]
        for path in self.root.rglob("*"):
            if not path.is_file() or any(p.startswith(".") for p in path.parts):
                continue
            rel = path.relative_to(self.root)
            self.by_stem.setdefault(path.stem.lower(), []).append(path)
            self.by_stem.setdefault(path.name.lower(), []).append(path)
            self.by_relpath.setdefault(str(rel.with_suffix("")).lower().replace("\\", "/"), []).append(path)
            self.by_relpath.setdefault(str(rel).lower().replace("\\", "/"), []).append(path)

    def resolve(self, target, source=None):
        """Resolve an Obsidian link target to a real file, Obsidian-style.

        Prefers an exact path match, then the shortest path when a bare name is
        ambiguous, then a file sitting next to the source note.
        """
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
    """GitHub's heading-anchor rules: lowercase, drop punctuation, spaces -> '-'."""
    text = unicodedata.normalize("NFKC", heading).strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text)


def rel_url(target, from_file):
    """Relative, URL-encoded path from the output file to the target."""
    rel = os.path.relpath(str(target), str(Path(from_file).parent))
    return quote(rel.replace(os.sep, "/"), safe="/._-()")


# --------------------------------------------------------------------------
# Wikilinks and embeds
# --------------------------------------------------------------------------

def split_target(raw):
    """Split 'Note#Heading|Alias' into (path, fragment, alias)."""
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

    if not path:  # [[#Heading]] — same-file link
        ctx["report"].bump("wikilinks_converted")
        return f"[{display}](#{slugify(frag)})"

    target = ctx["vault"].resolve(path, ctx["source"]) if ctx["vault"] else None
    if not target:
        ctx["report"].bump("wikilinks_unresolved")
        ctx["report"].unresolved.append((str(ctx["source"]), path))
        return display  # plain text, per the "link only if it exists" rule

    url = rel_url(ctx["out_for"](target), ctx["out_file"])
    if frag and not frag.startswith("^"):
        url += f"#{slugify(frag)}"
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
        # Obsidian uses the alias slot for size: |300 or |300x200
        if alias and re.fullmatch(r"\d+(x\d+)?", alias):
            w, _, h = alias.partition("x")
            dims = f' width="{w}"' + (f' height="{h}"' if h else "")
            return f'<img src="{url}" alt="{target.stem}"{dims}>'
        return f"![{alias or target.stem}]({url})"

    if ext == ".md":
        return embed_note(target, alias, frag, ctx)

    url = rel_url(ctx["out_for"](target), ctx["out_file"])
    label = alias or target.name
    ctx["report"].bump("media_linked")
    if ext in EMBEDDABLE_MEDIA:
        ctx["report"].notes.append(f"{target.name} was an inline media embed; converted to a link.")
    return f"[{label}]({url})"


def embed_note(target, alias, frag, ctx):
    """Note embeds have no standard-Markdown equivalent."""
    if ctx["embed_mode"] == "inline" and ctx["depth"] < 1:
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
    """Return the text under a heading, up to the next same-or-higher heading."""
    lines = body.split("\n")
    out, level = [], None
    for line in lines:
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
# Callouts
# --------------------------------------------------------------------------

def convert_callouts(text, report):
    lines = text.split("\n")
    out = []
    for line in lines:
        match = CALLOUT_RE.match(line)
        if not match:
            out.append(line)
            continue

        indent = match.group("indent")
        depth = match.group("marks").count(">")
        ctype = match.group("type").strip().lower()
        title = match.group("title").strip()
        marks = "> " * depth
        alert = CALLOUT_MAP.get(ctype)

        # GitHub alerts only work at the top level of the document and cannot
        # nest, so anything indented or nested degrades to a bold-titled quote.
        if alert is None or depth > 1 or indent:
            label = title or TITLE_WHEN_LOSSY.get(ctype, ctype.capitalize())
            report.bump("callouts_as_blockquote")
            out.append(f"{indent}{marks}**{label}**")
            if title or depth > 1 or indent:
                out.append(f"{indent}{marks}")
            continue

        report.bump("callouts_as_alerts")
        # An alert only renders when it starts its own block, so make sure the
        # previous line isn't text that would swallow it as a lazy continuation.
        if out and out[-1].strip() and not out[-1].lstrip().startswith(">"):
            out.append("")
        out.append(f"{indent}> [!{alert}]")
        label = title or (TITLE_WHEN_LOSSY.get(ctype) if CALLOUT_MAP.get(ctype) != ctype.upper() else None)
        if label:
            out.append(f"{indent}> **{label}**")
        if match.group("fold"):
            report.notes.append(
                f"Collapsible callout [!{ctype}] was flattened — alerts cannot fold."
            )
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

        # A line starting with #tag is parsed as a heading everywhere except
        # Obsidian, so escape it — and its siblings, to keep the line uniform.
        if opts.escape_tags and LEADING_TAG_RE.match(line):
            tagged = re.sub(r"(?<![\w`])#[^\s#`]+", lambda m: f"`{m.group(0)}`", line)
            if tagged != line:
                report.bump("tags_escaped")
            line = tagged

        task = TASK_RE.match(line)
        if task:
            report.bump("task_states_normalized")
            line = TASK_RE.sub(r"\1 \3", line, count=1)

        out.append(line)
    return "\n".join(out)


# --------------------------------------------------------------------------
# Frontmatter
# --------------------------------------------------------------------------

def strip_frontmatter(text):
    match = re.match(r"^---\r?\n(.*?)\r?\n---[ \t]*\r?\n?", text, re.DOTALL)
    if not match:
        return "", text
    return match.group(0), text[match.end():]


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

    text = convert_callouts(text, report)
    text = convert_links(text, ctx)

    if opts.highlight != "keep":
        repl = r"**\1**" if opts.highlight == "bold" else r"<mark>\1</mark>"
        hits = len(HIGHLIGHT_RE.findall(text))
        if hits:
            report.bump("highlights_converted", hits)
        text = HIGHLIGHT_RE.sub(repl, text)

    text = convert_lines(text, opts, report)

    # Removing comments and block IDs leaves gaps that change how the rest of
    # the document is parsed, so tidy them before restoring protected regions.
    if removed:
        text = re.sub(r"(?<=\S)[ \t]{2,}(?=\S)", " ", text)
        text = re.sub(r"^[ \t]+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return restore(text, store)


def convert_file(source, out_file, vault, opts, report, out_for):
    raw = Path(source).read_text(encoding="utf-8")
    frontmatter, body = strip_frontmatter(raw)
    if opts.strip_frontmatter:
        frontmatter = ""
        report.bump("frontmatter_stripped")

    ctx = {
        "vault": vault, "source": Path(source), "out_file": Path(out_file),
        "opts": opts, "report": report, "assets": set(),
        "embed_mode": opts.embed_mode, "depth": 0, "out_for": out_for,
    }
    converted = convert_body(body, ctx)
    result = (frontmatter + converted).rstrip() + "\n"
    Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    Path(out_file).write_text(result, encoding="utf-8")
    return ctx["assets"]


def main():
    ap = argparse.ArgumentParser(description="Convert Obsidian Markdown to standard Markdown.")
    ap.add_argument("inputs", nargs="+", help="Markdown files or directories to convert")
    ap.add_argument("--out", required=True, help="Output directory")
    ap.add_argument("--vault", help="Vault root used to resolve links (default: common parent of inputs)")
    ap.add_argument("--embed-mode", choices=["link", "inline"], default="link",
                    help="Note embeds ![[Note]]: turn into a link (default) or inline the content")
    ap.add_argument("--highlight", choices=["bold", "mark", "keep"], default="bold",
                    help="How to render ==highlights== (default: bold)")
    ap.add_argument("--strip-frontmatter", action="store_true", help="Remove YAML frontmatter")
    ap.add_argument("--keep-tags", dest="escape_tags", action="store_false",
                    help="Leave line-leading #tags alone (they may render as headings)")
    ap.add_argument("--no-copy-assets", dest="copy_assets", action="store_false",
                    help="Do not copy referenced images/attachments into the output directory")
    ap.add_argument("--json", action="store_true", help="Print the report as JSON")
    ap.set_defaults(escape_tags=True, copy_assets=True)
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
        """Where a vault file lands in the output tree."""
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
