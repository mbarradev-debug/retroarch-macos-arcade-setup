# retroarch-macos-arcade-setup

A reproducible RetroArch setup for Apple Silicon Macs: native arm64 cores for 40+ systems, a retro CRT look, low input lag, automatic box art, and a MAME arcade playlist that picks the right core for each game.

It is meant as an OpenEmu replacement with an arcade feel. Everything is installed by one idempotent script, and nothing copyrighted ships with it: **no ROMs, no BIOS files, no artwork**.

## What it looks like

- **Menu:** XMB (the PlayStation 3/PSP style menu), with the cover art on the right and an in-game screenshot beside it for each game.
- **TV consoles and arcade** (NES, SNES, Mega Drive, PC Engine, PlayStation, Saturn, MAME…): `crt-easymode`. It adds crisp scanlines and a soft CRT feel without darkening the picture, and it costs almost nothing on Apple Silicon.
- **Handhelds** (Game Boy, GBA, Game Gear, Lynx, Neo Geo Pocket, WonderSwan…): an LCD pixel grid that imitates the original screens. Game Boy and GBA use their own dot-matrix variants.
- **3D systems** (N64, PSP, Dreamcast, GameCube, DS, PS2): no filter. The internal resolution is raised instead (about 3x; 2x on PS2), since CRT filters tend to look poor on 3D.
- **Input lag:** run-ahead (1 frame, second instance) on 2D systems, so controls feel as responsive as the original hardware or better.

## Requirements

- A Mac with Apple Silicon (M1 or later). Tested on a MacBook Air M4 with macOS 26.
- [Homebrew](https://brew.sh)
- `python3` (included with the Xcode Command Line Tools: `xcode-select --install`)
- About 1 GB of disk for RetroArch, cores and shaders, plus your games.

## Installation

```bash
git clone https://github.com/mbarradev-debug/retroarch-macos-arcade-setup.git
cd retroarch-macos-arcade-setup
./install.sh
```

The script:

1. Installs RetroArch with Homebrew (`retroarch-metal`, the native universal build) if it is missing. If you have the Intel-only `retroarch` cask, run `./install.sh --replace-intel`; your settings are kept.
2. Backs up your existing configuration to `~/RetroArch-backup-<date>`.
3. Downloads the arm64 cores listed in [`cores.tsv`](cores.tsv) from the libretro buildbot, along with the core info files and the slang shader pack.
4. Downloads open-source emulator data: Dolphin's `Sys` folder, PPSSPP's assets and the PS2 game database. It never downloads BIOS files.
5. Merges the settings from [`config/retroarch.cfg`](config/retroarch.cfg) into your `retroarch.cfg`, and the per-core overrides and shader presets into place. Settings it does not manage are left alone.
6. Creates the ROM folders, one per system.

You can run it again at any time. It backs up first, and only downloads what is missing. Use `--update` to refresh cores and shaders.

> Quit RetroArch before running the script. RetroArch rewrites its configuration when it exits.

### Options

| Option | Meaning |
|---|---|
| `--roms DIR` | ROM folder to create (default `~/Games/roms`) |
| `--update` | Re-download cores, info files, shaders and emulator data |
| `--replace-intel` | Swap an Intel-only RetroArch for the native build |

## Systems

All cores are native arm64 builds. The default core is used for playlists; the alternates are installed too, and you can switch to them per game.

| Folder | System | Default core | Alternates |
|---|---|---|---|
| `atari2600` | Atari 2600 | Stella | |
| `atari5200` | Atari 5200 | Atari800 | |
| `atari7800` | Atari 7800 | ProSystem | |
| `lynx` | Atari Lynx | Handy | Beetle Lynx |
| `jaguar` | Atari Jaguar | Virtual Jaguar | |
| `coleco` | ColecoVision | Gearcoleco | blueMSX |
| `intellivision` | Intellivision | FreeIntv | |
| `odyssey2` | Odyssey² / Videopac | O2EM | |
| `vectrex` | Vectrex | vecx | |
| `nes`, `fds` | NES / Famicom Disk System | Nestopia | FCEUmm, Mesen |
| `snes` | Super Nintendo | Snes9x | bsnes |
| `n64` | Nintendo 64 | Mupen64Plus-Next | |
| `gb`, `gbc` | Game Boy / Color | Gambatte | SameBoy, mGBA |
| `gba` | Game Boy Advance | mGBA | |
| `nds` | Nintendo DS | melonDS DS | melonDS, DeSmuME |
| `vb` | Virtual Boy | Beetle VB | |
| `pokemini` | Pokémon mini | PokeMini | |
| `gamecube` | GameCube | Dolphin | |
| `sg1000` | SG-1000 | Genesis Plus GX | Gearsystem |
| `mastersystem` | Master System | Genesis Plus GX | Gearsystem, PicoDrive |
| `gamegear` | Game Gear | Genesis Plus GX | Gearsystem |
| `genesis` | Mega Drive / Genesis | Genesis Plus GX | PicoDrive |
| `segacd` | Mega-CD / Sega CD | Genesis Plus GX | PicoDrive |
| `32x` | 32X | PicoDrive | |
| `saturn` | Saturn | Beetle Saturn | Yabause |
| `dreamcast` | Dreamcast | Flycast | |
| `psx` | PlayStation | SwanStation | Beetle PSX HW, PCSX ReARMed |
| `psp` | PSP | PPSSPP | |
| `ps2` | PlayStation 2 | LRPS2 | |
| `pce`, `pcecd` | PC Engine / TurboGrafx (CD) | Beetle PCE Fast | Beetle PCE, Beetle SuperGrafx |
| `pcfx` | PC-FX | Beetle PC-FX | |
| `wswan`, `wswanc` | WonderSwan / Color | Beetle WonderSwan | |
| `ngp`, `ngpc` | Neo Geo Pocket / Color | Beetle NeoPop | |
| `3do` | 3DO | Opera | |
| `msx` | MSX | blueMSX | |
| `c64` | Commodore 64 | VICE x64sc | |
| `supervision` | Watara Supervision | Potator | |
| `arcade` | Arcade (MAME) | MAME 2003-Plus | MAME 2010 |

This covers every system OpenEmu supports, including its experimental ones.

## Adding your games

Put the games you own in `~/Games/roms/<folder>`, using the folder names above. Zipped cartridge games are fine. Disc games can be `.chd`, `.cue`/`.bin` or `.m3u`.

Then build the playlists:

```bash
python3 tools/make_playlists.py          # console systems
python3 tools/make_arcade_playlist.py    # arcade (see below)
```

Games are identified by CRC against the official [libretro-database](https://github.com/libretro/libretro-database) DATs, so the playlists use official names and the thumbnails match even when your files are renamed. Disc images are matched by file name. Box art, screenshots and title screens are downloaded from the libretro thumbnail server.

You can also use RetroArch's own **Import Content → Scan Directory**. Thumbnails are fetched on demand either way.

> Avoid keeping ROMs in an iCloud-synced folder such as `~/Documents` or `~/Desktop`. macOS may evict files to the cloud, and RetroArch then has to wait for them to download.

## BIOS files

Some systems need BIOS files from your own hardware. Put them in `~/Documents/RetroArch/system`, then check what is present or wrong:

```bash
python3 tools/check_bios.py          # required files
python3 tools/check_bios.py --all    # include optional ones
```

The check compares each file's MD5 with libretro's System.dat. These are required, or effectively required:

| System | Files |
|---|---|
| PlayStation | `scph5500.bin`, `scph5501.bin`, `scph5502.bin` |
| Saturn | `sega_101.bin`, `mpr-17933.bin` |
| Sega CD | `bios_CD_U.bin`, `bios_CD_E.bin`, `bios_CD_J.bin` |
| PC Engine CD | `syscard3.pce` |
| PC-FX | `pcfx.rom` |
| 3DO | `panafz10.bin` (or another Panasonic/Goldstar BIOS) |
| Atari 5200 | `5200.rom` |
| Atari Lynx | `lynxboot.img` |
| ColecoVision | `colecovision.rom` |
| Intellivision | `exec.bin`, `grom.bin` |
| Odyssey² | `o2rom.bin` |
| Dreamcast | `dc/dc_boot.bin` |
| PS2 | your console's BIOS in `pcsx2/bios/` |
| MSX | `Machines/Shared Roms/MSX.rom` |

Nintendo DS, Game Boy, GBA and N64 work without BIOS files.

## Arcade: MAME versions and romsets

MAME ROM sets change between MAME versions. A set built for one version often fails on another, because ROMs get renamed, added or redumped. Each libretro MAME core is frozen at a specific version:

| Core | MAME version | Romset to use |
|---|---|---|
| MAME 2003-Plus | 0.78 (plus many fixes and additions) | MAME 2003-Plus |
| MAME 2003 | 0.78 | 0.78 |
| MAME 2010 | 0.139 | 0.139 |
| MAME 2015 | 0.160 | 0.160 |
| FinalBurn Neo | current | current FBNeo |
| MAME (current) | latest | matching current MAME |

If your romset matches one of these exactly, use that core. If it does not, which is common with older packs, measure before deciding:

```bash
python3 tools/make_arcade_playlist.py --roms ~/Games/roms/arcade \
  --cores mame2003_plus,mame2010,fbneo --report
```

The report compares the CRC of every ROM in your zips with each core's official DAT. It counts a game as playable when all of its required ROMs are present (its own, its parent's or its BIOS's) and its driver is not marked as non-working. Here is a real example, an untouched MAME 0.122 set with 6,895 zips:

```
mame2003_plus  recognised  4967  playable  3979 (58%)  parents 2250
mame2010       recognised  5817  playable  3925 (57%)  parents 2318
fbneo          recognised  3729  playable  2245 (33%)  parents 1322
combined       playable  5324
```

No single core runs most of that set, but combining them does. Building the playlist with several cores assigns each game to the first core that can run it:

```bash
python3 tools/make_arcade_playlist.py --roms ~/Games/roms/arcade --cores mame2003_plus,mame2010
```

Only parent games are listed, which keeps the list readable. A clone is added only when its parent works in no core.

**Rebuilding a set.** To get a clean set for a single core, rebuild your files against that core's DAT with [clrmamepro](https://mamedev.emulab.it/clrmamepro/) (Windows, or Wine), [RomVault](https://www.romvault.com/) or [igir](https://igir.io/) (cross-platform, works on macOS). The DATs live in the core repositories: [MAME 2003-Plus](https://github.com/libretro/mame2003-plus-libretro/tree/master/metadata), [MAME 2010](https://github.com/libretro/mame2010-libretro/tree/master/metadata) and [FinalBurn Neo](https://github.com/libretro/FBNeo/tree/master/dats). Rebuilding only reorganises the ROMs you already have; anything the DAT needs that is missing from your files stays missing.

**Samples.** Some older games use recorded sound samples. Put the sample zips you have in `~/Documents/RetroArch/system/mame2003-plus/samples` and `~/Documents/RetroArch/system/mame2010/samples`.

## Customising

- **Global settings:** [`config/retroarch.cfg`](config/retroarch.cfg). Each key is commented.
- **Shader per core:** `config/shaders/presets/<Core>/<Core>.slangp`. Each one is a one-line reference to a shader in the slang pack, so you can point it at `crt/crt-royale.slangp`, `crt/crt-guest-advanced.slangp`, `bezel/Mega_Bezel/...`, etc. Folder names must match the core's internal library name (for example `MAME 2010`, `dolphin-emu`, `freeintv`, `ParaLLEl PS2`), which is not always the name shown in the menu.
- **Shader per content folder:** `config/shaders/presets/Genesis Plus GX/gamegear.slangp` gives Game Gear an LCD filter, even though it shares its core with the Mega Drive.
- **Per-core settings and options:** `config/overrides/<Core>/<Core>.cfg` (run-ahead) and `.opt` (internal resolution).

Run `./install.sh` again after editing.

## Guides

Step-by-step reading guides, each one a single continuous PDF page:

| Guide | What it covers |
|---|---|
| [Guide Index](docs/guides/00-guide-index.pdf) | One-line summary of every guide |
| [1. Quick Start](docs/guides/01-quick-start.pdf) | Requirements, install, first launch and how to check it worked |
| [2. ROMs](docs/guides/02-roms.pdf) | Folder per system, accepted extensions, zips, CD images, playlists and box art |
| [3. MAME and Arcade](docs/guides/03-mame-arcade.pdf) | Romset per core, merged/split/non-merged sets, CHDs, samples, failing games |
| [4. BIOS Files](docs/guides/04-bios.pdf) | Exact folder, every file with its MD5, and how to verify them |
| [5. Backup and Restore](docs/guides/05-backup-restore.pdf) | What to back up, `backup.sh` / `restore.sh`, rebuilding a formatted Mac |
| [6. Troubleshooting and FAQ](docs/guides/06-troubleshooting.pdf) | Slow games and video drivers, missing files, box art, controls, logs |

The guides are written in Markdown in [`docs/guides/src/`](docs/guides/src). After editing them, regenerate every PDF with one command (needs Node.js and Google Chrome; the first run installs two npm packages into `docs/node_modules`):

```bash
./docs/build-guides.sh
```

The script renders each guide with a shared stylesheet in headless Chrome, measures the content and uses that height as the page size, so each PDF is one page. It stops if a guide grows past 200 inches, the page-height limit of most PDF viewers; split such a guide in two.

## Backup and restore

The repository restores the setup, not your saves, BIOS files or ROMs. `backup.sh` copies those user folders (saves, states, system, playlists, configuration, controller profiles and, with `--roms`, your games) into a dated folder wherever you choose; `restore.sh` puts them back after `install.sh` on a new Mac.

```bash
./backup.sh /Volumes/MyDrive --roms ~/Games/roms
./restore.sh /Volumes/MyDrive/retroarch-backup-<date>
```

See the [Backup and Restore guide](docs/guides/05-backup-restore.pdf) for the full list and the steps for a freshly formatted Mac.

## Troubleshooting

**Games or the menu freeze after a few seconds, or feel slow and choppy.**
On RetroArch 1.22.x with macOS 26, the Metal video driver stalls about 8–9 seconds after starting: CPU use drops to zero and no error is logged. Vulkan and glcore are not affected. This setup uses Vulkan; check that `video_driver = "vulkan"` is set in Settings → Drivers. The libretro docs also describe the Metal driver as experimental.

**3D games (PSP, N64, Dreamcast, GameCube, PS1 with Beetle PSX HW) are slow or show nothing.**
The Metal driver gives cores no hardware 3D context, so they fall back to software rendering. Use Vulkan. Cores that only support OpenGL (melonDS DS for upscaling, Mupen64Plus-Next) are switched to glcore automatically, because `driver_switch_enable` is on.

**RetroArch is slow overall.**
Check that it is not the Intel build running under Rosetta: `lipo -archs /Applications/RetroArch.app/Contents/MacOS/RetroArch` must include `arm64`. If it does not, run `./install.sh --replace-intel`. Low Power Mode also reduces performance.

**A game says files are missing, or does not start.**
Run `python3 tools/check_bios.py`. For arcade games, the set probably does not match the core's MAME version; run the `--report` described above.

**A shader or override is not applied.**
The preset or override folder must be named after the core's internal library name. To find it, open a game and look in `~/Library/Application Support/RetroArch/config`: RetroArch creates a folder named after each core it has run.

**Thumbnails do not appear.**
Thumbnails are matched by the playlist label. Rebuild the playlist with `tools/make_playlists.py` so labels use official names. Some games have no artwork on the libretro server.

**Launching RetroArch from the terminal pauses it.**
With *Pause when focus is lost* enabled, a window launched behind the terminal pauses immediately. Click the window, or set `pause_nonactive = "false"`.

**My settings were overwritten.**
Every run of `install.sh` backs up `config/` and `shaders/presets/` to `~/RetroArch-backup-<date>` first. Copy the files back from there.

## Legal

This repository contains only configuration, scripts and documentation, under the MIT license. Cores, shaders and emulator data are downloaded from libretro at install time and keep their own licenses. Use it only with games and firmware you own.
