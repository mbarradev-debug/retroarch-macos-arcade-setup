#!/usr/bin/env bash
# Restore a backup made by backup.sh. Run install.sh first.
#
# Files from the backup are copied over the current ones; files that exist only
# on this Mac are kept (nothing is deleted). The current configuration is backed
# up before anything is overwritten.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./restore.sh BACKUP [--roms DIR]

  BACKUP       a retroarch-backup-<date> folder created by backup.sh
  --roms DIR   where to restore the ROMs, if the backup contains them (default: ~/Games/roms)
EOF
}

[[ $# -ge 1 && "$1" != -h && "$1" != --help ]] || { usage; exit 0; }
SRC="$1"; shift
ROMS="${HOME}/Games/roms"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --roms) ROMS="${2:?--roms needs a folder}"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

RA="${HOME}/Library/Application Support/RetroArch"
DOCS="${HOME}/Documents/RetroArch"
ESDE="${HOME}/ES-DE"

[[ -f "$SRC/manifest.txt" ]] || { echo "Error: $SRC is not a backup made by backup.sh." >&2; exit 1; }
if pgrep -x RetroArch >/dev/null; then
  echo "Error: quit RetroArch first; it rewrites its configuration when it exits." >&2
  exit 1
fi
if pgrep -x ES-DE >/dev/null; then
  echo "Error: quit ES-DE first; it rewrites its gamelists and settings when it exits." >&2
  exit 1
fi

SAFETY="${HOME}/RetroArch-backups/pre-restore-$(date +%Y%m%d-%H%M%S)"
for pair in "$RA/config|config" "$ESDE/settings|es-de/settings" "$ESDE/gamelists|es-de/gamelists"; do
  src="${pair%%|*}" name="${pair#*|}"
  if [[ -d "$src" ]]; then
    [[ -d "$SAFETY" ]] || echo "==> Saving the current configuration to $SAFETY"
    mkdir -p "$SAFETY/$name"
    ditto "$src" "$SAFETY/$name"
  fi
done

# name inside the backup -> destination
ITEMS=(
  "saves|$DOCS/saves"
  "states|$DOCS/states"
  "system|$DOCS/system"
  "playlists|$DOCS/playlists"
  "playlists-full|$DOCS/playlists-full"
  "screenshots|$DOCS/screenshots"
  "config|$RA/config"
  "autoconfig|$RA/autoconfig"
  "es-de/settings|$ESDE/settings"
  "es-de/gamelists|$ESDE/gamelists"
  "es-de/collections|$ESDE/collections"
  "roms|$ROMS"
)

for item in "${ITEMS[@]}"; do
  name="${item%%|*}" dest="${item#*|}"
  if [[ -d "$SRC/$name" ]]; then
    echo "==> $name -> $dest"
    mkdir -p "$dest"
    # exFAT and other non-Mac drives hold a ._ companion next to every file macOS
    # wrote there; on the Mac they would show up as broken playlists and profiles
    rsync -a --exclude '._*' --exclude '.DS_Store' "$SRC/$name/" "$dest/"
  fi
done

echo
echo "Restore complete. Run the installer again to re-apply its settings and rebuild"
echo "the playlists and ES-DE from your ROM folder:"
echo "  ./install.sh --roms \"$ROMS\""
