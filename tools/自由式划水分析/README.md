# 自由式划水分析

用電腦視覺（MediaPipe姿態估計）分析自由式選手側拍影片，輸出划水角度、划頻等指標，以及教練用的文字回饋報告。

## 來源
核心程式碼改編自開源專案 [veluthoor/swim-stroke-analyzer](https://github.com/veluthoor/swim-stroke-analyzer)（MIT License），僅保留本機CLI分析所需的部分（拿掉了網頁前後端、選配的Gemini UI設計助手）。

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
