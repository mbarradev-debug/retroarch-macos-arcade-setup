#!/usr/bin/env bash
# Install and configure RetroArch for Apple Silicon Macs.
#
# Safe to run more than once: existing configuration is backed up first, settings
# are merged (not replaced) and nothing already downloaded is fetched again unless
# --update is given. It never downloads ROMs or BIOS files. It ends by building
# the playlists from the games in the ROM folder, copying them into ES-DE and
# checking the BIOS files, so run it again after adding games.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./install.sh [options]

  --roms DIR        ROM folder to create, one sub-folder per system (default: ~/Games/roms)
  --update          re-download cores, core info files, shaders and system data, and
                    update a downloaded ES-DE theme
  --replace-intel   replace an Intel-only RetroArch (Homebrew cask "retroarch") with the
                    native universal build (cask "retroarch-metal"); settings are kept
  --no-esde         do not install or configure the ES-DE frontend
  --no-thumbnails   build the playlists without downloading box art and screenshots
  --esde-auto-update
                    also update the playlists and ES-DE in the background each time
                    ES-DE quits, so new games appear there with their artwork
  -h, --help        show this help
EOF
}

ROMS="${HOME}/Games/roms"
UPDATE=0
REPLACE_INTEL=0
ESDE=1
THUMBNAILS=1
ESDE_AUTO=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --roms) ROMS="${2:?--roms needs a folder}"; shift 2 ;;
    --update) UPDATE=1; shift ;;
    --replace-intel) REPLACE_INTEL=1; shift ;;
    --no-esde) ESDE=0; shift ;;
    --no-thumbnails) THUMBNAILS=0; shift ;;
    --esde-auto-update) ESDE_AUTO=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="/Applications/RetroArch.app"
RA="${HOME}/Library/Application Support/RetroArch"
DOCS="${HOME}/Documents/RetroArch"
SYSTEM_DIR="${DOCS}/system"
BUILDBOT="https://buildbot.libretro.com"
CORES_URL="${BUILDBOT}/nightly/apple/osx/arm64/latest"

info() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33mWarning:\033[0m %s\n' "$*" >&2; }
die() { printf '\033[1;31mError:\033[0m %s\n' "$*" >&2; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Download a zip into its own empty folder and extract it into a destination.
fetch_zip() {
  local url="$1" dest="$2" name
  name="$(basename "$url")"
  mkdir -p "$TMP/$name.d" "$dest"
  curl -fsSL --retry 3 -o "$TMP/$name.d/$name" "$url"
  unzip -oq "$TMP/$name.d/$name" -d "$dest"
  rm -rf "$TMP/$name.d"
}

# --- Preflight ---------------------------------------------------------------
[[ "$(uname -s)" == "Darwin" ]] || die "This script is for macOS."
[[ "$(uname -m)" == "arm64" ]] || die "This setup targets Apple Silicon (arm64) Macs."
command -v brew >/dev/null || die "Homebrew is required: https://brew.sh"
command -v python3 >/dev/null || die "python3 is required (run: xcode-select --install)."
if pgrep -x RetroArch >/dev/null; then
  die "Quit RetroArch first; it rewrites its configuration when it exits."
fi
if [[ $ESDE -eq 1 ]] && pgrep -x ES-DE >/dev/null; then
  die "Quit ES-DE first; it rewrites its settings when it exits."
fi

# --- RetroArch ---------------------------------------------------------------
if [[ ! -d "$APP" ]]; then
  info "Installing RetroArch (native universal build)"
  brew install --cask retroarch-metal
elif ! lipo -archs "$APP/Contents/MacOS/RetroArch" | grep -qw arm64; then
  if [[ $REPLACE_INTEL -eq 1 ]] && brew list --cask retroarch >/dev/null 2>&1; then
    info "Replacing the Intel-only RetroArch with the native build"
    brew uninstall --cask retroarch
    brew install --cask retroarch-metal
  else
    warn "The installed RetroArch is Intel-only and runs under Rosetta. Re-run with --replace-intel."
  fi
else
  info "RetroArch is already installed ($(defaults read "$APP/Contents/Info.plist" CFBundleShortVersionString), $(lipo -archs "$APP/Contents/MacOS/RetroArch"))"
fi

# --- Backup ------------------------------------------------------------------
# A safety copy of the configuration before it is merged, in ~/RetroArch-backups.
# Only the three newest are kept; older ones go to the Trash. These hold settings
# only: before formatting the Mac, use backup.sh to save games, saves and BIOS.
BACKUPS="${HOME}/RetroArch-backups"
if [[ -d "$RA/config" ]]; then
  BACKUP="$BACKUPS/install-$(date +%Y%m%d-%H%M%S)"
  info "Backing up the current configuration to $BACKUP"
  mkdir -p "$BACKUP"
  ditto "$RA/config" "$BACKUP/config"
  [[ -d "$RA/shaders/presets" ]] && ditto "$RA/shaders/presets" "$BACKUP/shaders/presets"
  for dir in custom_systems settings; do
    [[ -d "${HOME}/ES-DE/$dir" ]] && ditto "${HOME}/ES-DE/$dir" "$BACKUP/es-de/$dir"
  done
  # ls -t lists the newest first; the folder names have no spaces
  for old in $(ls -dt "$BACKUPS"/install-* 2>/dev/null | tail -n +4); do
    mv "$old" "${HOME}/.Trash/RetroArch-$(basename "$old")"
  done
fi

# --- Folders -----------------------------------------------------------------
info "Creating folders"
mkdir -p "$RA/cores" "$RA/info" "$RA/config" "$RA/shaders/presets" \
  "$SYSTEM_DIR" "$DOCS/playlists" "$DOCS/saves" "$DOCS/states" "$ROMS"
while IFS=$'\t' read -r folder _; do
  [[ -z "$folder" || "$folder" == \#* ]] && continue
  # a system folder can be a link to an external drive (see the ROMs guide)
  [[ -L "$ROMS/$folder" ]] || mkdir -p "$ROMS/$folder"
done < "$HERE/cores.tsv"

# --- Cores -------------------------------------------------------------------
# default and alternate cores from cores.tsv (columns 4 and 5), without duplicates
CORES="$(awk -F'\t' '!/^#/ && NF >= 4 { print $4; n = split($5, alt, ","); for (i = 1; i <= n; i++) if (alt[i] != "") print alt[i] }' \
  "$HERE/cores.tsv" | sort -u)"

info "Installing $(echo "$CORES" | wc -l | tr -d ' ') cores for arm64"
failed=""
for core in $CORES; do
  dylib="$RA/cores/${core}_libretro.dylib"
  if [[ -f "$dylib" && $UPDATE -eq 0 ]]; then
    continue
  fi
  if fetch_zip "$CORES_URL/${core}_libretro.dylib.zip" "$RA/cores" 2>/dev/null; then
    lipo -archs "$dylib" | grep -qw arm64 || warn "$core is not an arm64 build"
    printf '  %s\n' "$core"
  else
    failed="$failed $core"
  fi
done
[[ -z "$failed" ]] || warn "Not available on the arm64 buildbot:$failed"

if [[ $UPDATE -eq 1 || -z "$(ls -A "$RA/info" 2>/dev/null)" ]]; then
  info "Installing core info files"
  fetch_zip "$BUILDBOT/assets/frontend/info.zip" "$RA/info"
fi

# --- Shaders -----------------------------------------------------------------
# The slang shaders are downloaded from libretro rather than bundled here: each
# shader keeps its own license (mostly GPL). Only the small presets that point at
# them ship with this repository.
if [[ $UPDATE -eq 1 || ! -d "$RA/shaders/shaders_slang" ]]; then
  info "Installing slang shaders"
  fetch_zip "$BUILDBOT/assets/frontend/shaders_slang.zip" "$RA/shaders/shaders_slang"
fi
info "Installing the global and per-core shader presets"
ditto "$HERE/config/shaders/presets" "$RA/shaders/presets"
# Older versions shipped one crt-easymode preset per TV console; global.slangp
# replaces them. Remove only untouched copies so the global preset applies. The
# MAME presets that ship here now point at global.slangp too.
for preset in "$RA/shaders/presets"/*/*.slangp; do
  [[ "$(cat "$preset")" == '#reference "../../shaders_slang/crt/crt-easymode.slangp"' ]] && rm "$preset"
done

# --- Controller profiles -----------------------------------------------------
info "Installing controller profiles and per-core button remaps"
ditto "$HERE/config/autoconfig" "$RA/autoconfig"
ditto "$HERE/config/remaps" "$RA/config/remaps"

# --- Emulator data (open source, not BIOS) -----------------------------------
# Dolphin's Sys folder, PPSSPP's assets and the PS2 game database. The blueMSX
# pack is deliberately skipped because it contains copyrighted machine ROMs.
for pack in Dolphin:dolphin-emu PPSSPP:PPSSPP LRPS2:pcsx2; do
  name="${pack%%:*}" folder="${pack#*:}"
  if [[ $UPDATE -eq 1 || ! -d "$SYSTEM_DIR/$folder" ]]; then
    info "Installing $name system data"
    fetch_zip "$BUILDBOT/assets/system/$name.zip" "$SYSTEM_DIR"
  fi
done
mkdir -p "$SYSTEM_DIR/pcsx2/bios"

# --- Configuration -----------------------------------------------------------
info "Merging settings into retroarch.cfg"
python3 "$HERE/tools/merge_cfg.py" "$HERE/config/retroarch.cfg" "$RA/config/retroarch.cfg"

info "Merging per-core overrides and core options"
find "$HERE/config/overrides" -type f \( -name '*.cfg' -o -name '*.opt' \) | while read -r src; do
  rel="${src#"$HERE/config/overrides/"}"
  python3 "$HERE/tools/merge_cfg.py" "$src" "$RA/config/$rel" >/dev/null
done

# --- Launcher ----------------------------------------------------------------
# "RetroArch CRT" switches the built-in display to a 1:1 mode while RetroArch runs,
# so CRT masks and scanlines are not resampled by a scaled desktop mode.
LAUNCHER="${HOME}/Applications/RetroArch CRT.app"
if command -v swiftc >/dev/null; then
  info "Building the RetroArch CRT launcher in ~/Applications"
  mkdir -p "$LAUNCHER/Contents/MacOS" "$LAUNCHER/Contents/Resources"
  swiftc -O -o "$LAUNCHER/Contents/MacOS/RetroArch CRT" "$HERE/tools/retroarch_crt.swift"
  cp "$HERE/tools/sync_playlists.py" "$LAUNCHER/Contents/Resources/"
  icon="$(defaults read "$APP/Contents/Info.plist" CFBundleIconFile 2>/dev/null || true)"
  [[ -n "$icon" ]] && cp "$APP/Contents/Resources/${icon%.icns}.icns" "$LAUNCHER/Contents/Resources/AppIcon.icns" 2>/dev/null || true
  cat > "$LAUNCHER/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>RetroArch CRT</string>
  <key>CFBundleIdentifier</key><string>io.github.retroarch-macos-arcade-setup.crt-launcher</string>
  <key>CFBundleExecutable</key><string>RetroArch CRT</string>
  <key>CFBundleIconFile</key><string>AppIcon</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>LSUIElement</key><true/>
</dict>
</plist>
PLIST
  codesign --force --sign - "$LAUNCHER" >/dev/null 2>&1 || warn "Could not sign the launcher"
else
  warn "swiftc not found (run: xcode-select --install); skipping the RetroArch CRT launcher"
fi

# --- ES-DE --------------------------------------------------------------------
# ES-DE is a game browser with themes, cover art, screenshots and videos. It
# launches every game with the cores above, through the RetroArch CRT launcher.
if [[ $ESDE -eq 1 ]]; then
  if [[ ! -d /Applications/ES-DE.app ]]; then
    info "Installing ES-DE"
    brew install --cask es-de
  fi
  info "Pointing ES-DE at the ROM folder, the RetroArch cores and the Slate theme"
  esde_args=(--roms "$ROMS")
  [[ $UPDATE -eq 1 ]] && esde_args+=(--update)
  [[ $ESDE_AUTO -eq 1 ]] && esde_args+=(--quit-script)
  python3 "$HERE/tools/make_esde_config.py" "${esde_args[@]}"
fi

# --- Games -------------------------------------------------------------------
# Playlists, artwork and ES-DE gamelists for the games in the ROM folder. ES-DE
# also runs this after it quits, so new games show up there with their artwork.
games_args=(--roms "$ROMS")
[[ $THUMBNAILS -eq 0 ]] && games_args+=(--no-thumbnails)
[[ $ESDE -eq 0 ]] && games_args+=(--no-esde)
"$HERE/tools/update_games.sh" "${games_args[@]}"

info "Checking BIOS files"
bios_problems="$(python3 "$HERE/tools/check_bios.py" 2>&1 >/dev/null | tail -1)"

cat <<EOF

Done. Open ES-DE (or ~/Applications/RetroArch CRT) to play.
  - Games go in $ROMS/<system>; the folder names are listed in cores.tsv.
  - BIOS files go in $SYSTEM_DIR.
    ${bios_problems:-All required BIOS files are present.}
    Run python3 tools/check_bios.py to see which ones; only the systems you play need theirs.
  - Run ./install.sh again after adding games or BIOS files.
EOF
