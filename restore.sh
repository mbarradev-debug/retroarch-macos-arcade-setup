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

[[ -f "$SRC/manifest.txt" ]] || { echo "Error: $SRC is not a backup made by backup.sh." >&2; exit 1; }
if pgrep -x RetroArch >/dev/null; then
  echo "Error: quit RetroArch first; it rewrites its configuration when it exits." >&2
  exit 1
fi

if [[ -d "$RA/config" ]]; then
  SAFETY="${HOME}/RetroArch-backup-pre-restore-$(date +%Y%m%d-%H%M%S)"
  echo "==> Saving the current configuration to $SAFETY"
  mkdir -p "$SAFETY"
  ditto "$RA/config" "$SAFETY/config"
fi

# name inside the backup -> destination
ITEMS=(
  "saves|$DOCS/saves"
  "states|$DOCS/states"
  "system|$DOCS/system"
  "playlists|$DOCS/playlists"
  "screenshots|$DOCS/screenshots"
  "config|$RA/config"
  "autoconfig|$RA/autoconfig"
  "roms|$ROMS"
)

for item in "${ITEMS[@]}"; do
  name="${item%%|*}" dest="${item#*|}"
  if [[ -d "$SRC/$name" ]]; then
    echo "==> $name -> $dest"
    mkdir -p "$dest"
    rsync -a "$SRC/$name/" "$dest/"
  fi
done

echo
echo "Restore complete. If your ROM folder moved, rebuild the playlists:"
echo "  python3 tools/make_playlists.py --roms \"$ROMS\""
echo "  python3 tools/make_arcade_playlist.py --roms \"$ROMS/arcade\""
