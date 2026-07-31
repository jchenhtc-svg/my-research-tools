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

docker compose up --build -d

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
