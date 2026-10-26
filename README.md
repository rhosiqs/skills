# Skills Collection

<p align="center">
  <a href="README.md">English</a>
  &nbsp;·&nbsp;
  <a href="README.zh-TW.md">繁體中文</a>
</p>

<p align="center">
  <a href="https://github.com/rhosiqs/skills/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-16a34a" alt="MIT license"></a>
</p>

Skills I built to make AI responses more accurate or to support specific tasks. Feel free to use or modify them.

| Skill | Main purpose | Recommended use cases | Category | Details |
|---|---|---|---|---|
| `be-concise` | Force minimal, no-filler answers. | Quick questions where only the answer matters. Invoke via `/be-concise`. | AI Constraint | [![Look for detail](https://img.shields.io/badge/-Look_for_detail-ffdf80?style=for-the-badge)](./be-concise/) |
| `academic-translator` | Translate academic text with accurate terminology and register. Especially for zh-TW and en-US. | Translating or polishing papers, abstracts, and proposals. | Academic | [![Look for detail](https://img.shields.io/badge/-Look_for_detail-ffdf80?style=for-the-badge)](./academic-translator/) |
| `svg` | Render the result as an SVG vector. | Manual only: invoke via `/svg`. | Tool | [![Look for detail](https://img.shields.io/badge/-Look_for_detail-2ea44f?style=for-the-badge)](./svg/) |
| `svg-pptx` | Convert an SVG into fully editable PowerPoint shapes. | Invoke via `/svg-pptx`, or ask to export a diagram or chart as a presentation. | Tool | [![Look for detail](https://img.shields.io/badge/-Look_for_detail-2ea44f?style=for-the-badge)](./svg-pptx/) |
| `obsidian-github-markdown` | Convert Obsidian Markdown to GitHub-Flavored Markdown. | Publishing Obsidian notes to GitHub. | Tool | [![Look for detail](https://img.shields.io/badge/-Look_for_detail-2ea44f?style=for-the-badge)](./obsidian-github-markdown/) |
| `obsidian-to-portable-markdown` | Convert Obsidian Markdown to Markdown that renders in any previewer. | Exporting Obsidian notes to non-GitHub or mixed renderers. | Tool | [![Look for detail](https://img.shields.io/badge/-Look_for_detail-2ea44f?style=for-the-badge)](./obsidian-to-portable-markdown/) |
| `photo-grading` | Score and critique a photo like a competition judge. | Getting a rating or composition feedback on a photo. | Daily | [![Look for detail](https://img.shields.io/badge/-Look_for_detail-2ea44f?style=for-the-badge)](./photo-grading/) |


### Categories

- **Daily** — General-purpose tasks used in everyday work.
- **Academic** — Recommend for the academic use.
- **Tool** — Format conversion or file-production utilities.
- **AI Constraint** — Rules that change how the AI responds rather than what task it performs.

### Choosing between the two Obsidian skills

- Target is GitHub → `obsidian-github-markdown`
- Target is anything else, or multiple renderers → `obsidian-to-portable-markdown`

## Installation

Download or clone this repository, then choose one of the following:

### Option A: Install selected skills (recommended)

1. Pick the skills you need from the table above.
2. Drag only those skill folders (e.g. `photo-grading/`) into your AI tool (e.g. Claude, Claude Code).
3. Ask the AI to install them:

   ```
   Install these skills.
   ```

### Option B: Install all skills

1. Drag the whole repository folder into your AI tool.
2. Ask the AI to install every skill in it:

   ```
   Install all skills in this folder.
   ```

Only download or copy the specific skill is also recommended. Each skill folder contains a `SKILL.md`. Some also include `references/` and `scripts/`; keep the folder structure intact so these files are found.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
