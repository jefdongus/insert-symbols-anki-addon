#!/bin/bash

BUILD_FOLDER=build
ADDON_NAME=insert_symbols

EXCLUDES=".|..|build|*.sh|.git|.gitignore|*.ui|README.md|Ui_SymbolWindow*.py"

if [ -d $BUILD_FOLDER ]; then
  rm -rf $BUILD_FOLDER/*
else
  mkdir $BUILD_FOLDER
fi

mkdir -p "$BUILD_FOLDER/Anki20/$ADDON_NAME"
mkdir "$BUILD_FOLDER/Anki21"

shopt -s nullglob
shopt -s extglob

for i in !($EXCLUDES); do
  cp $i "$BUILD_FOLDER/Anki20/$ADDON_NAME/$i"
  cp $i "$BUILD_FOLDER/Anki21/$i"
done

cp Ui_SymbolWindow_4.py "$BUILD_FOLDER/Anki20/$ADDON_NAME/Ui_SymbolWindow.py"
cp Ui_SymbolWindow_5.py "$BUILD_FOLDER/Anki21/Ui_SymbolWindow.py"

py_fname=$(echo $ADDON_NAME | tr '_' ' ' | sed 's/\b[a-z]/\u&/g')

echo "import $ADDON_NAME.$ADDON_NAME" > "$BUILD_FOLDER/Anki20/$py_fname.py"
echo "from . import $ADDON_NAME" > "$BUILD_FOLDER/Anki21/__init__.py"

