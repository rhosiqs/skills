# Skills Collection

<p align="center">
  <a href="README.md">English</a>
  &nbsp;·&nbsp;
  <a href="README.zh-TW.md">繁體中文</a>
</p>

<p align="center">
  <a href="https://github.com/rhosiqs/small-web-tools/blob/develop/LICENSE"><img src="https://img.shields.io/badge/license-MIT-16a34a" alt="MIT license"></a>
</p>

一些自己做的skill，用來約束AI、增進學術簡報製作效率或其它特定用途。歡迎試試看！也可以下載來自己修改

| Skill | 主要目的 | 建議使用場景 | 分類 | 詳細說明 |
|---|---|---|---|---|
| `be-concise` | 強制 AI 只給最精簡、不帶廢話的回答。推論就說推論，降低AI幻覺 | 只需要答案本身的快速提問或想要精準回答，以 `/be-concise` 呼叫 | 約束 AI | [![查看詳細](https://img.shields.io/badge/-查看詳細-ffdf80?style=for-the-badge)](./be-concise/) 
| `academic-translator` | 以精確的術語與學術語域翻譯學術文本。繁體中文、英文特別優化 | 翻譯或潤飾論文、摘要與計畫書 | 學術 | [![查看詳細](https://img.shields.io/badge/-查看詳細-ffdf80?style=for-the-badge)](./academic-translator/) |
| `svg` | 將結果繪製成 SVG 向量圖 | 僅限手動觸發：以 `/svg` 呼叫 | 工具 | [![查看詳細](https://img.shields.io/badge/-查看詳細-2ea44f?style=for-the-badge)](./svg/) |
| `svg-pptx` | 將 SVG 轉換成可完整編輯的 PowerPoint 圖形 | 以 `/svg-pptx` 呼叫，或要求將圖表、示意圖匯出成簡報 | 工具 | [![查看詳細](https://img.shields.io/badge/-查看詳細-2ea44f?style=for-the-badge)](./svg-pptx/) |
| `obsidian-github-markdown` | 將 Obsidian Markdown 轉換成 GitHub-Flavored Markdown | 將 Obsidian 筆記發布到 GitHub | 工具 | [![查看詳細](https://img.shields.io/badge/-查看詳細-2ea44f?style=for-the-badge)](./obsidian-github-markdown/) |
| `obsidian-to-portable-markdown` | 將 Obsidian Markdown 轉換成在任何預覽器都能正確顯示的 Markdown | 將 Obsidian 筆記匯出到 GitHub 以外的平台，或需同時支援多種渲染器時 | 工具 | [![查看詳細](https://img.shields.io/badge/-查看詳細-2ea44f?style=for-the-badge)](./obsidian-to-portable-markdown/) |
| `photo-grading` | 以攝影比賽評審的角度為照片評分與講評 | 想取得照片的評分或構圖回饋時 | 日常 | [![查看詳細](https://img.shields.io/badge/-查看詳細-2ea44f?style=for-the-badge)](./photo-grading/) |


### 分類

- **日常**：日常工作中使用的一般用途任務。
- **學術**：建議用於學術場合。
- **工具**：格式轉換或檔案產出的工具。
- **約束 AI**：改變 AI 回應方式，而非指定 AI 執行哪種任務的規則。

### 兩個 Obsidian skill 的選擇方式

- 目標平台是 GitHub → `obsidian-github-markdown`
- 目標是其他平台，或需同時支援多種渲染器 → `obsidian-to-portable-markdown`

## 安裝方式

下載或 clone 這個 repository 後，擇一進行：

### 方式 A：只安裝需要的 skill（建議）

1. 從上方表格挑選需要的 skill。
2. 只把這些 skill 的資料夾（例如 `photo-grading/`）拖曳到你的 AI 工具中（例如 Claude、Claude Code）。
3. 請 AI 安裝：

   ```
   安裝這些 skill。
   ```

### 方式 B：安裝全部 skill

1. 把整個 repository 資料夾拖曳到你的 AI 工具中。
2. 請 AI 安裝資料夾內的所有 skill：

   ```
   安裝這個資料夾中的所有 skill。
   ```

也建議只下載或複製需要的 skill。每個 skill 資料夾都包含一個 `SKILL.md`，部分還附有 `references/` 與 `scripts/`；請保持資料夾結構完整，AI 才找得到這些檔案。

## 授權

本專案採用 MIT 授權條款，詳見 [LICENSE](LICENSE)。
