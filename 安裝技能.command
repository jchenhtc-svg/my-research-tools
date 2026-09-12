#!/bin/bash
# 把本 repo 的技能安裝成全域（Mac/Linux）
# 雙擊這個檔案即可安裝
# 安裝後在「任何專案」都能用，不再只限本 repo
#
# 會安裝這些技能：
#   wrap-up              說「收工」自動三方同步
#   baseline-ui          /baseline-ui <檔案> 檢查介面品質
#   fixing-accessibility /fixing-accessibility <檔案> 檢查無障礙

cd "$(dirname "$0")"

SKILLS=(wrap-up baseline-ui fixing-accessibility)

echo "======================================"
echo " 安裝技能（全域）"
echo "======================================"
echo ""

SRC_DIR="$(pwd)/.claude/skills"
DEST_DIR="$HOME/.claude/skills"

# 先全部檢查一遍，有缺就不要裝到一半
missing=0
for skill in "${SKILLS[@]}"; do
    if [ ! -f "$SRC_DIR/$skill/SKILL.md" ]; then
        echo "❌ 找不到技能來源：$SRC_DIR/$skill/SKILL.md"
        missing=1
    fi
done

if [ "$missing" -ne 0 ]; then
    echo ""
    echo "請先執行 git pull 再試一次。"
    read -p "按 Enter 鍵結束..."
    exit 1
fi

echo "來源：$SRC_DIR"
echo "目標：$DEST_DIR"
echo ""

mkdir -p "$DEST_DIR"

for skill in "${SKILLS[@]}"; do
    if [ -f "$DEST_DIR/$skill/SKILL.md" ]; then
        echo "→ $skill（已安裝過舊版，直接覆蓋）"
    else
        echo "→ $skill"
    fi

    if ! cp -r "$SRC_DIR/$skill" "$DEST_DIR/"; then
        echo "❌ $skill 複製失敗。"
        read -p "按 Enter 鍵結束..."
        exit 1
    fi
done

echo ""
echo "✅ 安裝完成（${#SKILLS[@]} 個技能）"
echo ""
echo "重新啟動 Claude Code，之後在任何專案都能用："
echo "  ・說「收工」自動三方同步"
echo "  ・/baseline-ui <檔案>          檢查介面品質"
echo "  ・/fixing-accessibility <檔案> 檢查無障礙"
echo ""
read -p "按 Enter 鍵結束..."
