#!/usr/bin/env bash
# Bring the playlists and ES-DE up to date with the games in the ROM folder.
#
# Deletes the ._ files macOS writes on exFAT drives, builds the console and arcade
# playlists (downloading their artwork) and copies them into ES-DE. Systems on a
# disconnected external drive are skipped; their playlists are kept. install.sh
# runs it at the end, and ES-DE runs it after quitting (see make_esde_config.py),
# so games copied into the ROM folder appear with their artwork the next time.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/update_games.sh [options]

  --roms DIR        ROM folder, one sub-folder per system (default: ~/Games/roms)
  --no-thumbnails   do not download box art and screenshots
  --no-esde         do not update ES-DE
  --after-esde      first wait for ES-DE to quit (used by its quit event)
EOF
}

ROMS="${HOME}/Games/roms"
THUMBNAILS=1
ESDE=1
WAIT=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --roms) ROMS="${2:?--roms needs a folder}"; shift 2 ;;
    --no-thumbnails) THUMBNAILS=0; shift ;;
    --no-esde) ESDE=0; shift ;;
    --after-esde) WAIT=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

TOOLS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
info() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }

if [[ $WAIT -eq 1 ]]; then
  while pgrep -x ES-DE >/dev/null; do sleep 1; done
  date
fi

# macOS writes a ._ companion file next to every file copied to an exFAT drive;
# they only hold metadata. Delete them, following links to external drives (two
# passes, because exFAT can skip entries while deleting).
for _ in 1 2; do
  find -L "$ROMS" -name '._*' -type f -delete 2>/dev/null || true
done

thumbs=()
[[ $THUMBNAILS -eq 0 ]] && thumbs=(--no-thumbnails)
info "Building the playlists from $ROMS"
python3 "$TOOLS/make_playlists.py" --roms "$ROMS" ${thumbs[@]+"${thumbs[@]}"}
if compgen -G "$ROMS/arcade/*.zip" >/dev/null; then
  info "Building the arcade playlist (it reads every zip; a large set takes a minute)"
  python3 "$TOOLS/make_arcade_playlist.py" --roms "$ROMS/arcade" ${thumbs[@]+"${thumbs[@]}"}
fi
if [[ $ESDE -eq 1 && -d "${HOME}/ES-DE/custom_systems" ]]; then
  info "Copying the playlists and their artwork into ES-DE"
  python3 "$TOOLS/make_esde_gamelists.py" --roms "$ROMS"
fi
