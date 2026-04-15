#!/usr/bin/env bash
set -e

APPNAME="PRRI-Game"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  PyInstaller Linux Build Script"
echo "========================================"
echo
echo "Project folder:"
echo "$SCRIPT_DIR"
echo

read -rp "Enter output folder for the build: " DISTPATH

if [ -z "$DISTPATH" ]; then
  echo
  echo "No path entered."
  exit 1
fi

mkdir -p "$DISTPATH"

if [ -n "$(ls -A "$DISTPATH" 2>/dev/null)" ]; then
  echo
  read -rp "The folder is not empty. Remove all contents first? (y/n): " ANSWER
  case "$ANSWER" in
    y|Y)
      echo "Clearing folder..."
      rm -rf "${DISTPATH:?}/"*
      ;;
    *)
      echo
      echo "Build cancelled."
      exit 1
      ;;
  esac
fi

echo
echo "Running PyInstaller..."
pyinstaller --name "$APPNAME" --onedir --distpath "$DISTPATH" \
  --add-data "assets:assets" \
  --add-data "resources:resources" \
  main.py

echo
echo "Build finished successfully."
echo "Opening built folder..."

if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$DISTPATH/$APPNAME" >/dev/null 2>&1 &
elif command -v gio >/dev/null 2>&1; then
  gio open "$DISTPATH/$APPNAME" >/dev/null 2>&1 &
else
  echo "Could not automatically open the built folder."
  echo "Open it manually here: $DISTPATH/$APPNAME"
fi