#!/bin/bash
# render_all.sh — полный пайплайн рендера факельной установки
# Запуск: bash render_all.sh

set -e
BLENDER=/snap/bin/blender
DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== 1. Создание модели и основной рендер ==="
$BLENDER --background --python "$DIR/flare_install.py" -o "$DIR/" -f 1

echo "=== 2. 4 ракурса ==="
$BLENDER --background "$DIR/flare_install.blend" --python "$DIR/render_views.py"

echo "=== 3. Копирование в report/images/ ==="
cp "$DIR/0001.png" "$DIR/../report/images/preview.png"
cp "$DIR/renders/"*.png "$DIR/../report/images/" 2>/dev/null

echo "=== ✅ Готово! ==="
echo "Рендеры:"
ls -lh "$DIR/renders/"
