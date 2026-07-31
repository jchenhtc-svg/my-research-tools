# 自由式划水分析

用電腦視覺（MediaPipe姿態估計）分析自由式選手側拍影片，輸出划水角度、划頻等指標，以及教練用的文字回饋報告。

兩種使用方式：CLI（自己分析用）跟網頁版（給選手/助理教練用瀏覽器上傳）。

## 來源
核心程式碼改編自開源專案 [veluthoor/swim-stroke-analyzer](https://github.com/veluthoor/swim-stroke-analyzer)（MIT License），拿掉了選配的Gemini UI設計助手。

---

# CLI版（本機分析）

## 安裝
```bash
cd tools/自由式划水分析
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python test_installation.py   # 確認環境OK
```

## 使用
```bash
python main.py 選手影片.mp4
```
輸出：
- `選手影片_analyzed.mp4`：標註骨架+角度的分析影片
- `選手影片_analyzed_report.txt`：教練回饋報告（總評分、關鍵問題、待加強項目）

其他選項：
```bash
python main.py 選手影片.mp4 --report-only   # 只出文字報告，不輸出影片（較快）
python main.py 選手影片.mp4 -o 指定輸出路徑.mp4
python main.py --help
```

## 拍攝建議
- 側面拍攝，與泳道垂直（90°）
- 光線充足、避免逆光
- 腳架固定，減少晃動
- 至少拍到2-3個完整划水週期（約10秒以上）
- 完整入鏡，不要選手游出畫面

## 待驗證
這是原作者針對一般自由式愛好者設定的判定規則（`src/models/freestyle_rules.py`裡的角度/划頻門檻），還沒針對我們的選手族群或運動科學標準校準過。先用手邊選手影片實測，看報告內容是否合理，再決定要不要調整判定邏輯。

已知限制：**偵測率明顯偏低（例如低於70%）的分析結果不該直接採信**——通常代表影片太短、選手中途出鏡、或動作剛好落在偵測空檔，樣本數不足會讓角度/划頻統計失真（實測時8/10分的一支影片偵測率只有48.3%，只抓到2次划水，可信度低於另外兩支96%+偵測率、判定4/10的影片）。之後可以考慮在報告裡加低偵測率警示。

---

# 網頁版（給選手/助理教練用瀏覽器上傳）

```
backend/    Flask API（上傳影片、跑分析、回傳報告+標註影片）
frontend/   React 前端（拖拉上傳、進度條、報告畫面）
```

## 本機啟動測試

**後端**
```bash
cd tools/自由式划水分析
source .venv/bin/activate        # 沿用CLI版的venv即可（requirements.txt已包含Flask相關套件）
python backend/app.py            # 預設跑在 http://localhost:5001
```

**前端**（另開一個終端機）
```bash
cd tools/自由式划水分析/frontend
npm install
npm start                        # 開瀏覽器到 http://localhost:3000
```

前端預設會打 `http://localhost:5001/api`（見 `frontend/src/config.js`），本機測試不用改設定。

## 部署到網路上給選手用
repo裡已附 `Dockerfile`／`Procfile`／`render.yaml`／`railway.json`／`nixpacks.toml`，是原作者為 Render/Railway/HuggingFace Spaces 準備的部署設定，可以直接拿來部署成一個網址讓選手/助理教練直接上傳影片，不用碰終端機。部署時需要另外設定環境變數 `FLASK_ENV=production`、`FRONTEND_URL`（後端CORS允許的前端網域）。

## 已知小問題
本機測試環境（Claude Code sandbox）因為套件庫連線問題裝不了ffmpeg，導致分析影片是mp4v編碼、瀏覽器播放器顯示黑屏（下載後用VLC等播放器可正常看）。這是**環境限制，不是程式問題**：`Dockerfile`裡已經有`apt-get install ffmpeg`，正式部署（Docker/Render等）會自動裝好ffmpeg，影片就能在瀏覽器正常播放。
