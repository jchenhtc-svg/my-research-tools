# my-research-tools — 我的研究工具總專案

## 對話開始時請先讀
進度與最近更動都在 Obsidian：`secondbrain/my-research-tools/工作筆記.md`

## 工作模式
- **加新工具**：對我說「我想做一個 XXX 工具」→ 建 `tools/<工具名>/` 子資料夾、引導跟著影片做
- **結束工作**：對我說「**收工**」→ 自動 commit + push + 更新 Obsidian 工作筆記（流程寫在 `.claude/skills/wrap-up/`）
- **接續工作**：對我說「讀工作筆記、告訴我上次做到哪」

## 工作桌 + 三個家
- 📋 GDrive 工作桌：`H:\我的雲端硬碟\my-research-tools\`（自動跨電腦同步）
- 🐙 GitHub repo：`jchenhtc-svg/my-research-tools`（公開，網頁的家）
- 📘 Obsidian 駕駛艙：`secondbrain/my-research-tools/工作筆記.md`（想法的家）

## 工具清單
（之後加新工具時會自動更新）
- `tools/自由式划水分析/`：用MediaPipe姿態估計分析自由式選手側拍影片，輸出划水角度/划頻等指標與教練回饋報告（改編自開源專案 veluthoor/swim-stroke-analyzer, MIT License）。有五種使用型態：CLI（本機分析，會順便產生單一HTML報告，雙擊即用不需伺服器）、網頁版（Flask+React，可部署雲端）、現地Docker版（雙擊`啟動.command`/`啟動.bat`，多裝置同WiFi連線）、現地單機.exe版（`build_exe.bat`打包，單一電腦用、不需Docker/Python）
- `tools/週會宣導/`：把角色對話腳本（JSON）轉成雙擊即播的單一 HTML「Podcast 對談」網頁，給早會/週會宣導用。多角色各自音調語速（瀏覽器內建 TTS）、字幕同步變色、簡易插畫隨劇情換表情、語速可調、播完停在金句+互動問題。每週新增一集只要加一個 `腳本/*.json` 再跑 `python3 產生網頁.py`，不用改網頁。播放引擎是技能 `.claude/skills/ai-dialogue-podcast-builder/`（可重複用在其他對話腳本專案）。目前已有《工程師的價值》系列第四週。

## 工作注意事項
- 學生資料一律去識別化（只用座號 + 班級代號）
- commit 訊息要寫清楚做了什麼 + 為什麼
- 收工前說「收工」讓自動同步三方
