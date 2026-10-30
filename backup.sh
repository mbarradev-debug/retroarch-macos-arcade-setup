#!/usr/bin/env bash
# Back up the RetroArch data that this repository does not store.
#
# Copies saves, save states, BIOS/system files, playlists, controller profiles
# and your RetroArch configuration (core options, remaps, per-game overrides), plus
# the ES-DE settings, gamelists and collections, into a dated folder inside DEST.
# Cores, shaders, thumbnails and ES-DE media are not copied: they are downloaded
# again by install.sh, the playlist tools or the ES-DE scraper. ROMs are only
# copied with --roms.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./backup.sh DEST [--roms DIR]

  DEST         folder where a dated backup folder is created (e.g. an external drive)
  --roms DIR   also copy your ROM folder (can be large)
EOF
}

[[ $# -ge 1 && "$1" != -h && "$1" != --help ]] || { usage; exit 0; }
DEST="$1"; shift
ROMS=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --roms) ROMS="${2:?--roms needs a folder}"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

RA="${HOME}/Library/Application Support/RetroArch"
DOCS="${HOME}/Documents/RetroArch"
ESDE="${HOME}/ES-DE"

[[ -d "$DEST" ]] || { echo "Error: $DEST does not exist." >&2; exit 1; }
if pgrep -x RetroArch >/dev/null; then
  echo "Error: quit RetroArch first so saves and settings are fully written." >&2
  exit 1
fi
if pgrep -x ES-DE >/dev/null; then
  echo "Error: quit ES-DE first so its gamelists and settings are fully written." >&2
  exit 1
fi

OUT="$DEST/retroarch-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT"

# source -> name inside the backup
ITEMS=(
  "$DOCS/saves|saves"                 # .srm saves, memory cards, MAME nvram/hiscores
  "$DOCS/states|states"               # save states
  "$DOCS/system|system"               # BIOS, MAME samples, Dolphin/PCSX2 user data
  "$DOCS/playlists|playlists"         # playlists, history and favorites
  "$DOCS/playlists-full|playlists-full"  # complete playlists, external-drive games included
  "$DOCS/screenshots|screenshots"     # screenshots, if you use this folder
  "$RA/config|config"                 # retroarch.cfg, core options, overrides, remaps
  "$RA/autoconfig|autoconfig"         # controller profiles you saved
  "$ESDE/settings|es-de/settings"     # ES-DE settings, including a ScreenScraper login
  "$ESDE/gamelists|es-de/gamelists"   # ES-DE game names, favourites and play counts
  "$ESDE/collections|es-de/collections"  # ES-DE custom collections
)
[[ -n "$ROMS" ]] && ITEMS+=("$ROMS|roms")

for item in "${ITEMS[@]}"; do
  src="${item%%|*}" name="${item#*|}"
  if [[ -d "$src" ]]; then
    echo "==> $name"
    rsync -a --exclude '.DS_Store' "$src/" "$OUT/$name/"
  fi
done

{
  echo "RetroArch backup created $(date)"
  echo "RetroArch version: $(defaults read /Applications/RetroArch.app/Contents/Info.plist CFBundleShortVersionString 2>/dev/null || echo unknown)"
  echo
  du -sh "$OUT"/* 2>/dev/null
} > "$OUT/manifest.txt"

echo
echo "Backup written to $OUT"
echo "Note: config/retroarch.cfg may contain your RetroAchievements token, and es-de/settings your ScreenScraper password. Keep this backup private."
