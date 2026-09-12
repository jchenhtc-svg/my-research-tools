# fixing-accessibility（外部技能）

- **來源**：[ui-skills](https://github.com/ibelick/ui-skills) by Julien Thibeaut（ibelick），官網 <https://www.ui-skills.com/>
- **授權**：MIT（見同資料夾 `LICENSE`）
- **`SKILL.md` 是原封不動的上游版本**，沒有改過，方便之後直接更新。

## 用法

在 Claude Code 裡：

- `/fixing-accessibility` → 這次對話中所有 UI 工作都套用無障礙規範
- `/fixing-accessibility <檔案>` → 檢查該檔案，逐條列出「違規原文 → 為何重要 → 具體修法」

規則涵蓋 ARIA 標籤、鍵盤操作、focus 管理、色彩對比、表單錯誤提示等 WCAG 項目，
偏好最小幅度的修正，不會大改介面。

## 套用到本專案時要注意

這份技能是框架無關的 HTML/ARIA 規則，直接適用於：

- `tools/自由式划水分析/frontend/`（網頁版 React 介面）
- CLI 產生的單一 HTML 報告

實際情境是學生和教練常在**平板／手機**上看報告，觸控目標大小、對比度、
影片控制項的鍵盤與螢幕閱讀器可及性特別值得檢查。
