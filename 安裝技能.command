#!/bin/bash
# 把「收工」技能安裝成全域（Mac/Linux）
# 雙擊這個檔案即可安裝
# 安裝後在「任何專案」說收工都會觸發，不再只限本 repo

cd "$(dirname "$0")"

echo "======================================"
echo " 安裝「收工」技能（全域）"
echo "======================================"
echo ""

SRC="$(pwd)/.claude/skills/wrap-up"
DEST="$HOME/.claude/skills/wrap-up"

if [ ! -f "$SRC/SKILL.md" ]; then
    echo "❌ 找不到技能來源："
    echo "   $SRC"
    echo ""
    echo "請先執行 git pull 再試一次。"
    read -p "按 Enter 鍵結束..."
    exit 1
fi

echo "來源：$SRC"
echo "目標：$DEST"
echo ""

if [ -f "$DEST/SKILL.md" ]; then
    echo "ℹ️  已安裝過舊版，將直接覆蓋。"
    echo ""
fi

mkdir -p "$HOME/.claude/skills"

if ! cp -r "$SRC" "$HOME/.claude/skills/"; then
    echo "❌ 複製失敗。"
    read -p "按 Enter 鍵結束..."
    exit 1
fi

echo "✅ 安裝完成"
echo ""
echo "重新啟動 Claude Code，之後在任何專案說「收工」都會觸發。"
echo ""
read -p "按 Enter 鍵結束..."
