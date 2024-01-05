#!/bin/bash

ADDON_NAME=insert_symbols

ROOT_FOLDER="$(cd "$(dirname "$0")/.." && pwd -P)"
SRC_FOLDER="$ROOT_FOLDER/src"
BUILD_FOLDER="$ROOT_FOLDER/build"

EXCLUDES=".|..|*.ui|__pycache__"

if [ -d $BUILD_FOLDER ]; then
  rm -rf $BUILD_FOLDER/*
else
  mkdir $BUILD_FOLDER
fi

mkdir -p "$BUILD_FOLDER/Anki20/$ADDON_NAME"
mkdir "$BUILD_FOLDER/Anki21"

shopt -s nullglob
shopt -s extglob

cd "$SRC_FOLDER"

for i in !($EXCLUDES); do
  cp $i "$BUILD_FOLDER/Anki20/$ADDON_NAME/$i"
  cp $i "$BUILD_FOLDER/Anki21/$i"
done

#cp Ui_SymbolWindow_4.py "$BUILD_FOLDER/Anki20/$ADDON_NAME/Ui_SymbolWindow.py"
#cp Ui_SymbolWindow.py "$BUILD_FOLDER/Anki21/Ui_SymbolWindow.py"
cp "$ROOT_FOLDER/manifest.json" "$BUILD_FOLDER/Anki21/manifest.json"

py_fname=$(echo $ADDON_NAME | tr '_' ' ' | sed 's/\b[a-z]/\u&/g')

echo "import $ADDON_NAME.$ADDON_NAME" > "$BUILD_FOLDER/Anki20/$py_fname.py"
echo "from . import $ADDON_NAME" > "$BUILD_FOLDER/Anki21/__init__.py"
