#!/bin/bash
# render_all.sh — одной командой: модель + рендер + 4 ракурса
# Запускать на машине с GPU

set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
BLENDER=/snap/bin/blender

echo "=== Создание модели и рендер ==="
$BLENDER --background --python "$DIR/flare_install.py" -o "$DIR/" -f 1

echo "=== 4 ракурса ==="
$BLENDER --background "$DIR/flare_install.blend" --python "$DIR/render_views.py"

echo "=== Копирование в report/ ==="
cp "$DIR/0001.png" "$DIR/../report/images/preview.png"
cp "$DIR/renders/"*.png "$DIR/../report/images/" 2>/dev/null

echo "=== ✅ Готово ==="
ls -lh "$DIR/renders/"
