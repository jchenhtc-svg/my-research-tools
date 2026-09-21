# 週會宣導回應收集 — Cloudflare Workers + D1

把播放器結尾「送出回應」的資料，改成透過 Cloudflare Workers 寫進 D1（一個免費的
雲端 SQLite 資料庫），這樣不管誰用手機或電腦填、彼此都連得到同一份資料，
文字雲工具也能直接抓雲端資料，不需要再手動收集本機檔案。

## 部署前你要準備的

1. 一個免費 Cloudflare 帳號（dash.cloudflare.com，email 註冊即可，不需信用卡）
2. 一組 API Token：登入後點右上角頭像 →「My Profile」→「API Tokens」→
   「Create Token」→ 選範本 **「Edit Cloudflare Workers」** → 建立、複製 token
3. Dashboard 右側欄的 **Account ID**

## 部署步驟

拿到 token 跟 Account ID 之後，在這個資料夾（`tools/週會宣導/cloudflare/`）依序執行：

```bash
export CLOUDFLARE_API_TOKEN="貼上你的 token"
export CLOUDFLARE_ACCOUNT_ID="貼上你的 Account ID"

# 1. 建立 D1 資料庫（只需要做一次）
npx wrangler d1 create weekly-briefing-responses
# 這一步會印出一個 database_id，把它貼進 wrangler.toml 裡取代
# REPLACE_AFTER_CREATING_DATABASE

# 2. 建立資料表
npx wrangler d1 execute weekly-briefing-responses --remote --file=schema.sql

# 3. 設定防呆用的 SITE_KEY（隨便打一串你自己記得住的亂碼即可，不是密碼等級的安全機制）
npx wrangler secret put SITE_KEY

# 4. 部署 Worker
npx wrangler deploy
```

部署完成後，指令會印出一個網址，長得像：

```
https://weekly-briefing-responses.<你的帳號>.workers.dev
```

把這個網址、還有你在步驟 3 設定的 SITE_KEY，回報給 Claude，接下來會把它們
填進播放器跟文字雲頁面裡，讓兩邊都能連到這個 Worker。

## 之後要更新 Worker 程式碼時

改完 `worker.js` 之後，重新執行 `npx wrangler deploy` 就會更新雲端上的版本。

## 誠實說明

- Worker 網址是**公開的**——任何人只要知道網址都連得到。`SITE_KEY` 只是一個
  簡單的門檻，擋掉「剛好路過亂掃描的機器人」，不是真正的身分驗證，不要拿來
  存放機密資料。
- 這個免費方案（Workers + D1 Free tier）額度：Workers 每天 10 萬次請求、
  D1 每天 500 萬次讀取、10 萬次寫入——對幾十人規模的內部回應收集來說綽綽有餘。
- 這條路**需要連網、需要呼叫外部 API**（Cloudflare 的伺服器）。如果公司資安
  政策明確禁止使用外部 API 服務，這個做法不符合規定，請先跟 IT／資安部門
  確認過可以用 Cloudflare 再實際啟用。
