# my-research-tools — 我的研究工具總專案

## 對話開始時請先讀
進度與最近更動都在 Obsidian：`secondbrain/my-research-tools/工作筆記.md`

## 工作模式
- **加新工具**：對我說「我想做一個 XXX 工具」→ 建 `tools/<工具名>/` 子資料夾、引導跟著影片做
- **結束工作**：對我說「**收工**」→ 自動 commit + push + 更新 Obsidian 工作筆記（流程寫在 `.claude/skills/wrap-up/`）
- **接續工作**：對我說「讀工作筆記、告訴我上次做到哪」
- **介面檢查**：做網頁或 HTML 報告時說「`/baseline-ui <檔案>`」或「`/fixing-accessibility <檔案>`」→ 逐條列出問題與修法（技能在 `.claude/skills/`，來自開源專案 ibelick/ui-skills, MIT License）

## 工作桌 + 三個家
- 📋 GDrive 工作桌：`H:\我的雲端硬碟\my-research-tools\`（自動跨電腦同步）
- 🐙 GitHub repo：`jchenhtc-svg/my-research-tools`（公開，網頁的家）
- 📘 Obsidian 駕駛艙：`secondbrain/my-research-tools/工作筆記.md`（想法的家）

## 工具清單
（之後加新工具時會自動更新）
- `tools/自由式划水分析/`：用MediaPipe姿態估計分析自由式選手側拍影片，輸出划水角度/划頻等指標與教練回饋報告（改編自開源專案 veluthoor/swim-stroke-analyzer, MIT License）。有五種使用型態：CLI（本機分析，會順便產生單一HTML報告，雙擊即用不需伺服器）、網頁版（Flask+React，可部署雲端）、現地Docker版（雙擊`啟動.command`/`啟動.bat`，多裝置同WiFi連線）、現地單機.exe版（`build_exe.bat`打包，單一電腦用、不需Docker/Python）

## 工作注意事項
- 學生資料一律去識別化（只用座號 + 班級代號）
- commit 訊息要寫清楚做了什麼 + 為什麼
- 收工前說「收工」讓自動同步三方
