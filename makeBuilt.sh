#!/usr/bin/env bash
set -e

APPNAME="PRRI-Game"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  PyInstaller Linux Build Script"
echo "========================================"
echo

echo "Checking PyInstaller..."
if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "PyInstaller is not installed or not available on PATH."
  read -rp "Install PyInstaller now? (y/n): " INSTALL_ANSWER
  case "$INSTALL_ANSWER" in
    y|Y)
      echo
      echo "Installing PyInstaller with pip..."
      python3 -m pip install -U pyinstaller
      ;;
    *)
      echo
      echo "Installation declined. Exiting."
      exit 1
      ;;
  esac
fi

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
echo "Removing old local PyInstaller build artifacts..."
rm -rf build *.spec

echo
echo "Running PyInstaller..."
pyinstaller \
  --noconfirm \
  --name "$APPNAME" \
  --onedir \
  --distpath "$DISTPATH" \
  --windowed \
  --exclude-module numpy \
  --add-data "Assets:Assets" \
  --add-data "resources:resources" \
  main.py

echo
echo "Build finished successfully."
echo "Built folder:"
echo "$DISTPATH/$APPNAME"
echo

echo "Opening built folder..."
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$DISTPATH/$APPNAME" >/dev/null 2>&1 &
elif command -v gio >/dev/null 2>&1; then
  gio open "$DISTPATH/$APPNAME" >/dev/null 2>&1 &
else
  echo "Could not automatically open the built folder."
  echo "Open it manually here: $DISTPATH/$APPNAME"
fi
