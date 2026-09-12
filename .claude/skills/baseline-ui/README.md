# baseline-ui（外部技能）

- **來源**：[ui-skills](https://github.com/ibelick/ui-skills) by Julien Thibeaut（ibelick），官網 <https://www.ui-skills.com/>
- **授權**：MIT（見同資料夾 `LICENSE`）
- **`SKILL.md` 是原封不動的上游版本**，沒有改過，方便之後直接更新。

## 用法

在 Claude Code 裡：

- `/baseline-ui` → 這次對話中所有 UI 工作都套用這些規範
- `/baseline-ui <檔案>` → 檢查該檔案，逐條列出「違規原文 → 為何重要 → 具體修法」

## 套用到本專案時要注意

這份規範預設的技術棧是 **Tailwind CSS + motion/react**，本專案的網頁版前端是
`tools/自由式划水分析/frontend/`（Create React App + React 19，純 CSS，沒有 Tailwind），
CLI 產生的單一 HTML 報告也是手寫 CSS。

所以：

- **Tailwind 專屬的條目**（`text-balance`、`size-*`、`tw-animate-css`、`cn` 工具…）要當成「設計意圖」讀，用等效的 CSS 寫法達成，不要為了照做而引入 Tailwind。
- **跟框架無關的條目照單全收**：動畫只動 `transform`/`opacity`、互動回饋不超過 200ms、`h-dvh` 取代 `h-screen`、空狀態要有明確下一步、不要無故加漸層／發光、資料數字用 `tabular-nums`（`font-variant-numeric: tabular-nums`）。
