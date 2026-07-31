#!/bin/bash
# 自由式划水分析 - 現地啟動腳本（Mac/Linux）
# 雙擊這個檔案即可啟動（Mac第一次雙擊可能需要在「系統設定→隱私權與安全性」允許執行）

cd "$(dirname "$0")"

echo "======================================"
echo " 自由式划水分析 - 正在啟動..."
echo "======================================"
echo ""

if ! command -v docker &> /dev/null; then
    echo "❌ 找不到 Docker，請先安裝 Docker Desktop："
    echo "   https://www.docker.com/products/docker-desktop/"
    read -p "按 Enter 鍵結束..."
    exit 1
fi

echo "檢查 Docker Desktop 是否已啟動..."
if ! docker info &> /dev/null; then
    echo ""
    echo "❌ Docker 指令找得到，但 Docker Desktop 應用程式還沒開啟或還在初始化。"
    echo "   請先手動打開 Docker Desktop，等到選單列的鯨魚圖示不再跳動（通常要等10-30秒），"
    echo "   再重新雙擊這個檔案一次。"
    echo ""
    read -p "按 Enter 鍵結束..."
    exit 1
fi

echo "Docker 已就緒，開始建置（第一次會花幾分鐘，請耐心等待）..."
echo ""

if ! docker compose up --build -d; then
    echo ""
    echo "❌ 啟動失敗，請把上面的錯誤訊息截圖回報。"
    echo ""
    read -p "按 Enter 鍵結束..."
    exit 1
fi

echo ""
echo "✅ 啟動完成！"
echo ""
echo "請打開瀏覽器輸入以下網址開始使用："
echo "   http://localhost:8080"
echo ""
echo "（第一次啟動需要幾分鐘下載/建置，之後會快很多）"
echo ""

sleep 2
if command -v open &> /dev/null; then
    open "http://localhost:8080"
elif command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:8080"
fi

echo "要關閉服務，請執行同目錄下的「關閉.command」"
read -p "按 Enter 鍵關閉這個視窗（服務會繼續在背景執行）..."
