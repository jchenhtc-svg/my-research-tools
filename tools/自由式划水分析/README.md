# 自由式划水分析

用電腦視覺（MediaPipe姿態估計）分析自由式選手側拍影片，輸出划水角度、划頻等指標，以及教練用的文字回饋報告。

四種使用方式：CLI（自己分析用）、網頁版（雲端部署給選手/助理教練用）、現地Docker版（單機起服務，同WiFi多裝置連線）、**現地單機.exe版**（單一電腦用，不需要Docker/Python，雙擊就跑）。

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

## 部署到網路上給選手用（雲端）
repo裡已附 `Dockerfile`／`Procfile`／`render.yaml`／`railway.json`／`nixpacks.toml`，是原作者為 Render/Railway/HuggingFace Spaces 準備的部署設定。**安全性考量下建議選Render**（HF Spaces免費版預設公開可搜尋，不適合放選手影像）。部署時需要另外設定環境變數 `FLASK_ENV=production`、`FRONTEND_URL`（後端CORS允許的前端網域）。⚠️ 目前程式本身沒有任何登入驗證，正式對外部署前務必先加一層密碼保護。

---

# 現地Docker版（單機起服務，同WiFi多裝置連線，資料不上雲）

適合**訓練現場有多人要一起連**（教練+助理教練+選手各自手機/平板）的情境。把 `backend`＋`frontend` 包成**單一Docker容器**（同一個port同時提供API跟網頁），只要在一台電腦上啟動，同一個WiFi下的手機/平板都能連。

## 使用方式（現場教練/助理，不需要懂程式）
1. 該電腦第一次使用需先安裝 [Docker Desktop](https://www.docker.com/products/docker-desktop/)（一次性，免費）
2. 雙擊 `啟動.command`（Mac）或 `啟動.bat`（Windows）
3. 等它印出「啟動完成」，瀏覽器會自動打開 http://localhost:8080
4. 同一個WiFi下的其他裝置，把 `localhost` 換成該電腦的區網IP（例如 `http://192.168.1.23:8080`）即可連線
5. 用完雙擊 `關閉.command` / `關閉.bat` 即可關閉服務

## 技術細節（給會碰程式的人）
```bash
cd tools/自由式划水分析
docker compose up --build   # 或直接用上面的啟動腳本
```
`Dockerfile` 是多階段build：先用Node把 `frontend/` 編譯成靜態檔案，再放進Python的Flask後端一起提供服務，`backend/app.py` 會在 `/` 直接serve編譯好的前端，`/api/*` 才是API路由——所以整個工具只佔一個port（預設對外映射 `8080`），現地使用非常單純。容器內也裝了ffmpeg，分析影片可以在瀏覽器正常播放（不像本機dev測試時遇到的黑屏問題）。

⚠️ **注意**：這個Docker打包過程本身無法在目前的Claude Code sandbox環境完整驗證（此環境的網路政策擋掉了Docker Hub的映像檔下載），但底層邏輯（Flask單一origin同時serve API+前端靜態檔）已經用本機Node build+Flask實測過，行為與Docker容器內完全一致；`Dockerfile`／`docker-compose.yml`／啟動腳本請在正常網路環境（您自己的電腦）跑一次 `docker compose up --build` 驗證。

## 已知小問題
本機測試環境（Claude Code sandbox）因為套件庫連線問題裝不了ffmpeg，`npm start`/`python backend/app.py`直接跑（非Docker）時分析影片會是mp4v編碼、瀏覽器播放器顯示黑屏（下載後用VLC等播放器可正常看）。這是**環境限制，不是程式問題**：Docker容器內已經裝好ffmpeg會自動解決；雲端部署（Render等）平台上apt-get也能正常裝ffmpeg。

---

# 現地單機.exe版（只有一台電腦要用，不需要Docker/Python/Node）

適合**只有一台電腦要看、不用給其他裝置連**的情境。不需要安裝Docker Desktop（省掉500MB下載+重開機），使用者只要拿到一個資料夾，雙擊裡面的`.exe`，背景會自動啟動、自動跳出瀏覽器，關掉視窗就結束。

## 給教練/助理教練（拿到打包好的資料夾之後）
1. 解壓縮 `SwimStrokeAnalyzer` 資料夾（放桌面或任何位置都可以，**不要把裡面的.exe單獨移出來**，它需要跟旁邊的檔案放在一起）
2. 雙擊 `SwimStrokeAnalyzer.exe`
3. 出現黑色視窗印出啟動訊息後，瀏覽器會自動打開 http://127.0.0.1:8080
4. 用完直接關掉那個黑色視窗即可（等於關閉服務）

## 給會碰程式的人（第一次要自己build出.exe）
這個.exe必須在**Windows電腦**上build（無法從Mac/Linux或這個開發環境跨平台編譯），只要build這一次，之後產出的資料夾誰都能直接用，不需要再裝任何東西：

1. 該Windows電腦先裝好 [Python 3.10+](https://www.python.org/downloads/) 和 [Node.js](https://nodejs.org/)（只有build這台電腦需要，其他使用者的電腦不用裝）
2. 雙擊 `build_exe.bat`，或在終端機執行：
   ```
   cd tools\自由式划水分析
   build_exe.bat
   ```
3. 跑完後產出 `dist\SwimStrokeAnalyzer\` 資料夾，裡面的 `SwimStrokeAnalyzer.exe` 就是給使用者雙擊的檔案。把整個資料夾壓縮成zip分享出去即可

### 技術細節
- `desktop_app.py` 是給PyInstaller打包用的進入點：用 [waitress](https://github.com/Pylons/waitress)（純Python、跨平台的WSGI伺服器，Windows不支援gunicorn所以雲端版跟桌面版分開處理）取代gunicorn，並且**用`importlib`直接從硬碟讀取`backend/app.py`**（而不是讓PyInstaller把它編譯進打包檔內部），這樣`backend/app.py`原本用`__file__`算路徑的邏輯（找`frontend/build`、`uploads`/`results`資料夾）在打包後才能繼續正確運作
- `build_exe.bat`用 `--add-data` 把 `backend`／`src`／`frontend/build` 三個資料夾原封不動塞進輸出資料夾，用 `--collect-data mediapipe` 額外處理mediapipe自己內建的模型檔案（這是PyInstaller打包mediapipe時常見的雷，模型檔案不會被自動偵測到）
- 已在本機（Linux，非frozen狀態）用實際跑`desktop_app.py`＋Playwright驗證整條「啟動→上傳→分析→出報告」流程正確、跟原本的Docker版/dev版結果一致（4/10分、無console錯誤）
- ⚠️ **PyInstaller打包出真正的.exe這一步本身還沒驗證過**（此開發環境是Linux，無法跨平台編譯Windows執行檔）。第一次在Windows上跑`build_exe.bat`如果PyInstaller報錯找不到某個模組，通常是加一個 `--hidden-import <模組名>` 就能解決，`build_exe.bat`裡也有留這個提示
