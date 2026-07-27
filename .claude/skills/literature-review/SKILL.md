---
name: literature-review
description: Guides a two-pass (scan-then-rescan) literature review workflow for academic/research writing - initial title-and-abstract scan, deeper article review with gap-tracking, building an annotated bibliography, immediately logging citations into reference software, repeating scans until saturation, then reviewing the bibliography for themes/gaps/inconsistencies and writing up the review. Use this whenever the user is starting, continuing, or organizing a literature review, systematic review, or SLR - even if they just say things like "幫我看這幾篇論文跟我的研究有沒有關係", "整理一下這些文獻", "annotated bibliography", "文獻回顧要怎麼開始", "我要交文獻探討", "追蹤 research gap", or mentions Zotero/EndNote/Mendeley citation management alongside a batch of papers. Also trigger when the user pastes/uploads multiple paper titles, abstracts, or PDFs and wants to know which are relevant, or asks whether their literature search has reached "saturation" / can stop.
---

# 文獻回顧工作流程 (Literature Review Workflow)

依據 Christine @Scholar Culture 的 8 步驟文獻回顧架構圖改寫。核心精神：**用「兩輪掃描、逐漸加深」取代「一次讀懂每篇論文」** —— 第一遍只看標題/摘要抓範圍，第二遍才決定深讀哪些、寫進附註書目，並且每一篇進來就立刻建檔、立刻加引用，不要堆積「之後再處理」的欠帳。整個過程重複到「飽和」（再掃也掃不出新主題）才停下來寫作。

## 為什麼要照這個順序做

文獻回顧最容易卡住的地方，不是找不到文獻，而是：(1) 想一次把每篇都讀熟讀懂，導致進度停滯；(2) 讀到後面才發現漏了某個子主題，得從頭重找；(3) 引用資訊沒有即時記錄，寫作時要重新翻一輪原文找出處。這個流程用「先略讀分流、再深讀寫檔、立刻建立引用」來解決這三個問題，並用「重複掃描直到飽和」取代「怎樣才算讀夠了」的模糊感覺。

## 開始一個新的文獻回顧專案

在動手掃描前，先確認以下資訊（使用者沒講清楚就主動問，不要用預設值硬猜）：

1. **研究問題與回顧範圍**：這次文獻回顧要回答什麼問題？範圍多廣（例如：只看近 10 年、只看某地區、只看某方法論）？
2. **要用的資料庫/來源**：例如 Google Scholar、ERIC、Web of Science、特定期刊，是否要納入灰色文獻（研討會論文、政府報告、學位論文等未正式出版的資料）？
3. **時間限制**：初步掃描打算花多久？（圖中特別建議設時間上限，避免第一輪就陷入細讀）
4. **文獻管理軟體**：使用者用 Zotero / EndNote / Mendeley 還是純手動？

確認後，在使用者指定的專案資料夾（沒指定就用 `literature-review/<主題簡稱>/`）建立這兩個檔案，之後每一輪掃描都持續更新它們：

- **附註書目** — 複製 `assets/annotated-bibliography-template.md` 到專案資料夾，改名為 `annotated-bibliography.md`。
- **追蹤表** — 複製 `assets/tracking-sheet-template.csv` 到專案資料夾，改名為 `tracking-sheet.csv`。若使用者比較想要正式的 `.xlsx`（對應圖中「Excel chart」），可以用 xlsx 技能把這份 CSV 轉成試算表。

這兩份檔案是整個流程的「記憶」：不管掃描到第幾輪，都靠它們判斷目前涵蓋了什麼主題、還缺什麼、有哪些篇已經處理過。**每次繼續工作前，先讀這兩個檔案，不要憑空重新開始。**

## SCAN 1：第一輪掃描

### 步驟 1 — Initial Scan（初步掃描）

只看**標題與摘要**，目的是抓範圍、不是理解內容。針對每篇候選文獻，用一兩句話記下「這篇看起來在談什麼」，先不判斷是否要深讀。維持在使用者說好的時間限制內；如果使用者沒設限，主動建議一個（例如「這 20 篇摘要，我抓 15 分鐘看完初步分類，可以嗎？」）。

輸出：把候選文獻列進追蹤表，狀態標為「待略讀」。

### 步驟 2 — Review Articles（略讀）

對初步掃描後留下的文獻做更深入、但仍是**略讀**的檢視：看章節標題、瀏覽討論與結論，不逐字精讀全文。這一步常會發現「摘要看起來相關，細看後其實不相關」的文章 —— 這是正常現象，不是掃描失敗，直接在追蹤表把狀態改成「不相關-已排除」即可，不用勉強塞進附註書目。

**同步做 gap 追蹤**：一邊略讀一邊記錄「目前這批文獻涵蓋了哪些主題/角度」以及「初步掃描的關鍵字/範圍好像漏掉了什麼」。這份 gap 清單就是下一輪掃描要補的方向，直接寫在追蹤表或附註書目的備註欄。

### 步驟 3 — Add to annotated bib（加入附註書目）

略讀後判斷相關的文章，才進附註書目，依照 `assets/annotated-bibliography-template.md` 的欄位填寫。附註書目不必只是摘要的複述 —— 依使用者這次專案的需求客製化欄位，例如：這篇的主要論點屬於回顧的哪個子主題、這篇在談誰/什麼對象、這篇對使用者自己的研究有什麼建議或啟發。範本裡已經包含常見欄位，用不到的可以刪，需要加的也可以加。

### 步驟 4 — Add to reference software（立刻建立引用）

判定要收錄的文章，**當下**就請使用者加進 Zotero/EndNote 等文獻管理軟體並產生正式引用格式，貼回附註書目的「引用」欄位 —— 不要拖到最後一次補齊，那樣最容易漏掉出處或格式錯誤。同步更新追蹤表對應列的狀態欄。

如果使用者要總覽/篩選用的試算表（圖中「Excel chart」，非必要但建議），就同步更新 `tracking-sheet.csv`：加入引用細節、涵蓋主題、目前輪次等欄位，方便之後做主題分類或排序篩選。

## SCAN 2 及之後：重複掃描直到飽和

### 步驟 5 — Scan 2

带著上一輪整理出的 gap 清單，回頭找文獻（新關鍵字、新資料庫、或原本略過的灰色文獻）。跟 Scan 1 不同的是，這次不是從零開始 —— 先看追蹤表跟附註書目，清楚知道「已經涵蓋什麼」，鎖定「還缺什麼」去找。

### 步驟 6 — 重複步驟 2-4

對新一輪找到的文獻，重複「略讀 → 評估 gap → 加入附註書目 → 加入引用軟體」。**判斷是否需要再開一輪（Scan 3、4、5…）的依據是「飽和」**：如果一整輪掃描下來，附註書目沒有出現新的主題、新的論點、新的引用，只是重複已經記錄過的內容，就代表這個回顧範圍已經飽和，可以停止掃描、進入下一階段。如果還有明顯沒填補的 gap，就再開一輪，不要因為「已經掃了兩輪」就強迫停下。

飽和判斷不是憑感覺，主動幫使用者對照：「上一輪 gap 清單裡列的主題，這一輪有沒有被涵蓋到？」有涵蓋就更新/勾掉，沒有就留著，下一輪繼續針對它找。

## 收尾

### 步驟 7 — Review bib（回顧附註書目）

飽和後，通讀整份 `annotated-bibliography.md`（必要時"列印"或輸出成單一文件方便通讀），標出：

- **主題（themes）**：哪些文獻可以歸成同一群、支持同一個論點
- **落差（gaps）**：目前文獻沒有回答、但跟研究問題相關的問題
- **不一致（inconsistencies）**：不同文獻對同一件事有衝突的發現或立場

這一步的產出通常是一份「文獻回顧大綱」——依主題分節、每節底下列出要引用哪些文獻、以及這節要呈現的論點走向。

### 步驟 8 — Write up（撰寫文獻回顧）

依照步驟 7 整理出的大綱撰寫文獻回顧：總結各主題的關鍵發現、說明其重要性、明確連結回研究問題，並在適當之處加入使用者自己的分析與立場（不是單純堆疊「A 說了什麼、B 說了什麼」）。寫作時直接引用附註書目裡已經準備好的正式引用格式，不用回頭查原文。

## 全程提醒：Meetings

這個流程假設使用者會**定期跟指導教授或團隊開會**，用回饋來檢查自己的盲點（例如：漏掉的重要文獻、對某個主題的偏見解讀）。在合理的時間點（例如剛完成 Scan 1、或判斷「飽和」的時候）主動提醒使用者「這是一個適合跟指導教授對一下範圍/飽和判斷的時間點」，但不要沒完沒了地重複提醒。

## 附屬檔案

- `assets/annotated-bibliography-template.md` — 附註書目範本，每篇文獻一個區塊
- `assets/tracking-sheet-template.csv` — 追蹤表範本，可直接用試算表軟體開啟，或用 xlsx 技能轉成正式 `.xlsx`
