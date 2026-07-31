#!/bin/bash
# 自由式划水分析 - 關閉服務（Mac/Linux）
cd "$(dirname "$0")"
docker compose down
echo "已關閉。"
read -p "按 Enter 鍵結束..."
