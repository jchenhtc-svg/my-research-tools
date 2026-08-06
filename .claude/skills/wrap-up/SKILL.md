---
name: wrap-up
description: 收工同步流程——把一段工作的成果同步到三個家：GitHub（程式碼）、Google Drive（工作桌）、Obsidian（工作筆記）。當使用者說「收工」「結束工作」「今天到這」「同步一下」「三方同步」「wrap up」，或在一段開發告一段落時要求記錄進度，一律使用這個技能。也適用於使用者問「上次做到哪」而需要回頭讀/更新工作筆記的情況。不要因為看起來只是「commit 一下」就跳過——收工的重點不只是 push，而是讓三個家的狀態一致，而且誠實反映哪些真的同步了。
---

# 收工（wrap-up）

## 為什麼有這個技能

使用者的專案同時活在三個地方：

| 家 | 位置 | 放什麼 |
|----|------|--------|
| 🐙 GitHub | `github.com/<user>/<repo>` | 程式碼、能跑的東西 |
| 📋 Google Drive 工作桌 | `H:\我的雲端硬碟\<repo>\` | 跨電腦自動同步的工作副本 |
| 📘 Obsidian 駕駛艙 | `secondbrain/<repo>/工作筆記.md` | 進度、決策、想法 |

三個家很容易漂移：程式碼推上去了但筆記沒更新，下次接手時完全不知道上次做到哪。收工的目的就是收斂這個漂移。

**這個技能最重要的一件事不是「把東西同步好」，而是「誠實說明哪些同步了、哪些沒有」。** 環境限制常常讓某一路走不通（下面會講），這時候假裝成功比失敗更糟——使用者會以為筆記更新了，下次接手就撲空。

## 執行順序

### Step 1：先把 GitHub 收乾淨

```bash
git status --short
git log --oneline -5
```

有未提交的變更就 commit。commit 訊息要寫**做了什麼 + 為什麼**（使用者專案規則），例如
`自由式划水分析：啟動.bat改純英文避免cmd.exe編碼崩潰`
而不是 `fix bat file`。

推送到指定分支：

```bash
git push -u origin <branch>
```

網路失敗才重試，退避 2s / 4s / 8s / 16s。

確認是否已併入主線（決定筆記怎麼寫）：

```bash
git fetch origin main   # 或 master，看該 repo
git branch -r --contains HEAD
```

如果輸出裡有 `origin/main`（或 `origin/master`），表示已經 merge 進去了，筆記可以寫「已 merge」。

### Step 2：判斷你在哪種環境——這決定後面全部的做法

```bash
ls -d ~/secondbrain 2>/dev/null || find / -xdev -maxdepth 4 -name "工作筆記.md" 2>/dev/null | head
```

**找得到 vault** → 你在使用者本機，直接用 Edit/Write 改 `工作筆記.md` 就好，收工可以全自動完成。

**找不到** → 你在遠端容器（Claude Code on the web / GitHub Action）。容器裡只有 clone 出來的 repo，本機檔案系統上沒有 vault 也沒有 H: 磁碟。

**但檔案系統找不到 ≠ 碰不到 vault。** 這位使用者的 Obsidian vault 本身就放在 Google Drive 上：

```
我的雲端硬碟/secondbrain/<repo>/工作筆記.md
```

所以就算在遠端容器，也能透過 Google Drive 連接器讀寫 vault。**先查過 Drive 再說「做不到」**——直接宣告失敗會讓使用者白白多做一次手動搬運。查法：

```
search_files: title contains '工作筆記'
→ 拿到 parentId，再 get_file_metadata 往上查，確認是不是 secondbrain/<repo>/
```

### Step 3：取得並更新工作筆記

先找檔案（Google Drive 連接器）：

```
search_files: title contains '工作筆記'
```

多個 repo 可能各有一份工作筆記，用 `contentSnippet` 確認是不是當前 repo 的那份，別更新錯。

讀內容——`download_file_content` 回傳的是 **base64**，要解碼：

```bash
base64 -d b64.txt > 工作筆記_原始.md
```

（`read_file_content` 不支援 `text/markdown`，別浪費一次呼叫。）

更新時遵守這幾條：

- **「上次做到哪」整段換掉**——這是給下次接手的人看的，要寫最後動作、所在 repo、改了哪些檔案，以及**最快的驗證指令**（下次接手的人最想要的就是這個）
- **「最近更動紀錄」表格只准往下加**——這是歷史，舊的列一列都不能動。日期用真的 commit 日期，不要用今天：
  ```bash
  git log --reverse --format='%ad %s' --date=short origin/main
  ```
- 如果這次工作產生了新的階段性狀態（哪些實測過、哪些還沒），加一個現況表格比塞進散文有用得多

### Step 4：讓筆記真的落地

這裡有一個**必須知道的限制**：

> **Google Drive 連接器只能新建檔案，不能就地覆蓋。** 工具只有 `create_file`，沒有 update。

所以如果你直接上傳 `工作筆記.md`，同一個資料夾會出現**兩個同名檔案**，Obsidian 同步會亂掉——這比不更新還糟。

依環境選路線：

**本機環境**：直接用 Edit/Write 改 vault 裡的 `工作筆記.md`。這條最乾淨，改完 Drive 自動同步，什麼都不用手動做。

**遠端容器**：用 `create_file` 上傳到 vault 資料夾（`secondbrain/<repo>/`）。因為不能覆蓋，**用加日期的檔名**（`工作筆記_20260806.md`），別用原檔名去撞——Drive 允許同名檔案並存，但同步下來之後 Obsidian 會出現兩則同名筆記，桌面版客戶端還可能自己把其中一個改名成 `工作筆記 (1).md`，反而更難收拾。

上傳時**一定要設 `disableConversionToGoogleType: true`**。Drive 預設會把上傳的 markdown 轉成 Google Docs 格式，一轉 Obsidian 就讀不到了——這個錯很安靜，檔案看起來有上去，但 vault 裡就是不出現。

上傳完告訴使用者剩下的手動步驟（在 Obsidian 或 Drive 裡把舊的 `工作筆記.md` 刪掉、新的改回原名），並附上 `viewUrl` 方便他直接點開確認。

也可以同時用 `SendUserFile` 給一份，讓他有離線備份。

### Step 5：誠實結算

「最近更動紀錄」表格有 GDrive / Obsidian / GitHub 三個 ✅ 欄位。**只有你真的確認過的才標 ✅。**

- GitHub 推上去也確認過了 → ✅
- 筆記還在使用者的下載資料夾、還沒放進 vault → 不要標 ✅，標 ⏳，並在回覆裡講明「這格要等您放進去才算數」

這條看起來很小，但它決定了這份筆記三個月後還能不能信。一旦開始有「標了✅其實沒做」的列，整張表就失去意義了。

## 工作筆記格式

沿用既有結構，不要重新設計（使用者已經習慣了）：

````markdown
# <repo> 工作筆記

> 進度日誌（變動快）。專案藍圖請看 GDrive 端的 `CLAUDE.md`。
> 進度只在這裡記錄，避免雙寫漂移。

## ⏯️ 上次做到哪

**最後動作**：<一句話講完這次做了什麼，有 PR 就註明狀態>
**所在 repo**：[<repo>](<url>)
**改動範圍**：
- `<檔案>`：<改了什麼>

**下次接手最快驗證方式**：
```bash
<能直接貼上去跑的指令>
```

## 🛠️ 工具清單

| 工具 | 版本 | 用途 |
|------|:----:|------|

## 🗓️ 最近更動紀錄

| 日期 | 變更摘要 | GDrive | Obsidian | GitHub |
|------|----------|--------|----------|--------|
| <只加新列，舊列不動> |
````

## 收工回覆怎麼寫

使用者說「收工」時想知道的是「我可以關電腦了嗎」。所以回覆要能一眼看完：

1. **GitHub 狀態**——commit 了什麼、推到哪、有沒有 merge
2. **筆記狀態**——更新了什麼，以及**還需要使用者做什麼**（如果有）
3. **卡住的事情**——講原因，不要只說做不到

如果有某一路沒走通，把原因講清楚（例如「Drive 連接器不能覆蓋檔案，硬上傳會產生同名重複檔，所以我沒動它」）。使用者能理解限制，不能理解沉默。
