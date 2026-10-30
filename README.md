# retroarch-macos-arcade-setup

A reproducible RetroArch setup for Apple Silicon Macs: native arm64 cores for 40+ systems, a retro CRT look, low input lag, automatic box art, and a MAME arcade playlist that picks the right core for each game.

It is meant as an OpenEmu replacement with an arcade feel. Everything is installed by one idempotent script, and nothing copyrighted ships with it: **no ROMs, no BIOS files, no artwork**.

## What it looks like

- **Game browser:** [ES-DE](https://www.es-de.org/) (EmulationStation Desktop Edition), with one themed screen per system and each game's box art, screenshot, title screen and video. It launches every game in RetroArch with the cores and shaders below. See [ES-DE frontend](#es-de-frontend).
- **RetroArch menu:** XMB (the PlayStation 3/PSP style menu), with the cover art on the right and an in-game screenshot beside it for each game.
- **TV consoles** (NES, SNES, Mega Drive, PC Engine, PlayStation, Saturn…): `crt-guest-advanced` as the global preset ([`config/shaders/presets/global.slangp`](config/shaders/presets/global.slangp)), tuned for the 2560×1664 MacBook Air panel: no curvature or rounded corners, SMPTE-C (NTSC TV) colours, CRT gamma, well-defined scanlines, an RGB aperture-grille mask one display pixel per phosphor, halation, glow and bloom. Mask bloom, bright boost and a little extra saturation give back the light the mask and scanlines take away: the picture keeps about 98% of the original brightness, with slightly richer colour. Integer scaling on the vertical axis puts every scanline on whole display rows (SNES 7×, GBA 10×), and each system keeps its own aspect ratio.
- **Arcade** (MAME): the same `crt-guest-advanced` look as the TV consoles; the MAME presets point at `global.slangp`.
- **Handhelds** (Game Boy, GBA, Game Gear, Lynx, Neo Geo Pocket, WonderSwan…): an LCD pixel grid that imitates the original screens. Game Boy uses a dot-matrix variant; GBA uses `zfast-lcd`, a fine LCD grid that keeps natural colours and about 90% of the original brightness (the original GBA colour emulation looked too dim on this panel).
- **3D systems** (N64, PSP, Dreamcast, GameCube, DS, PS2): no filter. The internal resolution is raised instead (about 3x; 2x on PS2), since CRT filters tend to look poor on 3D.
- **Console bezels** (NES, SNES, Game Boy, Game Boy Color, GBA, Master System, Game Gear, Mega Drive): artwork of the console, its controller and logo fills the sides of the screen, from [The Bezel Project](https://github.com/thebezelproject/BezelProject). To leave room for it the game is drawn one step smaller, still with whole display rows per line: SNES, NES and Mega Drive 6×, GBA 9×, Game Boy and Game Gear 10×. See [Bezels](#bezels).
- **Sharp on Retina:** the *RetroArch CRT* launcher (built into `~/Applications` by `install.sh`) switches the built-in display to 1280×832 points, which is 2560×1664 pixels drawn 1:1, while RetroArch runs, and macOS restores your usual mode when it quits. Scaled modes such as *More Space* shrink the picture by a non-integer factor, which causes moiré on scanlines and masks. Open RetroArch from this launcher.
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
2. Backs up your existing configuration to `~/RetroArch-backups/install-<date>`, keeping the three newest copies.
3. Downloads the arm64 cores listed in [`cores.tsv`](cores.tsv) from the libretro buildbot, along with the core info files and the slang shader pack.
4. Downloads open-source emulator data: Dolphin's `Sys` folder, PPSSPP's assets and the PS2 game database. It never downloads BIOS files.
5. Merges the settings from [`config/retroarch.cfg`](config/retroarch.cfg) into your `retroarch.cfg`, and the per-core overrides and shader presets into place. Settings it does not manage are left alone.
6. Creates the ROM folders, one per system.
7. Builds the *RetroArch CRT* launcher in `~/Applications`.
8. Installs [ES-DE](#es-de-frontend) with Homebrew and points it at the ROM folder and the cores (skip with `--no-esde`).
9. Builds the playlists from the games in the ROM folder (console systems and arcade), downloads their box art, copies them into ES-DE and reports missing BIOS files.

You can run it again at any time, and you should after adding games or BIOS files: that one command updates everything. It backs up first, and only downloads what is missing. Use `--update` to refresh cores and shaders, and `--no-thumbnails` to skip the artwork downloads.

> Quit RetroArch and ES-DE before running the script. Both rewrite their configuration when they exit.

### Options

| Option | Meaning |
|---|---|
| `--roms DIR` | ROM folder to create (default `~/Games/roms`) |
| `--update` | Re-download cores, info files, shaders and emulator data |
| `--replace-intel` | Swap an Intel-only RetroArch for the native build |
| `--no-esde` | Do not install or configure ES-DE |
| `--no-thumbnails` | Build the playlists without downloading box art and screenshots |
| `--no-bezels` | Do not frame games with artwork of their console |
| `--esde-auto-update` | Also refresh the playlists and ES-DE in the background each time ES-DE quits, so games you copy in appear with their artwork next time |

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

Then run the installer again; it builds the playlists and updates ES-DE:

```bash
./install.sh
```

It runs three tools, which you can also run by hand: `tools/make_playlists.py` (console systems), `tools/make_arcade_playlist.py` (arcade, see below) and `tools/make_esde_gamelists.py` (copies both, with their artwork, into ES-DE).

Games are identified by CRC against the official [libretro-database](https://github.com/libretro/libretro-database) DATs, so they are recognised even when your files are renamed. Disc images are matched by file name, with or without region tags. Games are listed by a clean title, the official name without region, language and revision tags (*The Legend of Zelda - The Minish Cap* rather than *Legend of Zelda, The - The Minish Cap (Europe) (En,Fr,De,Es,It)*), and a file you named yourself, such as `Pokemon Rubi.zip`, keeps its name. Box art, screenshots and title screens are downloaded from the libretro thumbnail server by official name and saved under the title.

You can also use RetroArch's own **Import Content → Scan Directory**. Thumbnails are fetched on demand either way.

> Avoid keeping ROMs in an iCloud-synced folder such as `~/Documents` or `~/Desktop`. macOS may evict files to the cloud, and RetroArch then has to wait for them to download.

> Large sets can live on an external drive (exFAT for Mac, Windows and Linux, or APFS for Mac only): link `~/Games/roms/<system>` to the system's folder on the drive, for example `ln -s /Volumes/BACKUP/roms/arcade ~/Games/roms/arcade`. RetroArch and ES-DE show those games while the drive is connected and hide them, without *file is missing* errors, while it is not: the playlist tools keep complete playlists in `~/Documents/RetroArch/playlists-full`, and `tools/sync_playlists.py`, which the RetroArch CRT launcher runs each time, shows RetroArch only the games present. Delete the hidden `._*` files macOS writes on exFAT. The [ROMs guide](docs/guides/02-roms.pdf) has the steps.

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

## ES-DE frontend

RetroArch's menu is built for settings, not for browsing a collection. `install.sh` therefore also installs [ES-DE](https://www.es-de.org/), a controller-friendly game browser, and configures it with `tools/make_esde_config.py`:

- `~/ES-DE/custom_systems/es_systems.xml` replaces ES-DE's entry for each system in `cores.tsv`, so ES-DE reads this setup's folder names (the last column of `cores.tsv` maps them to ES-DE's names, such as `lynx` → `atarilynx`) and starts games with the default core. The alternates appear under *Alternative emulators*.
- Games start through the *RetroArch CRT* launcher, so the 1:1 display mode and every shader, override and remap apply exactly as when you start them from RetroArch.
- `ROMDirectory` in `~/ES-DE/settings/es_settings.xml` is set to your `--roms` folder.
- The Slate theme bundled with ES-DE is selected, as a text list with videos and dark colours.

`tools/make_esde_gamelists.py` then copies the RetroArch playlists into ES-DE: the same clean titles, the libretro box art, snaps and title screens (hard-linked, so they use no extra space), the genre, release year, developer, publisher and number of players (from libretro-database's metadata DATs for console games, from the MAME metadata for arcade), the per-game MAME core chosen by `make_arcade_playlist.py`, and hidden entries for `.cue` tracks, `.m3u` discs and arcade zips no core runs. For videos, logos and descriptions, use ES-DE's scraper with a free [ScreenScraper](https://www.screenscraper.fr) account. The [ES-DE guide](docs/guides/07-es-de.pdf) covers scraping, themes and controls.

Quit ES-DE before running `install.sh` or the tool; ES-DE rewrites its settings and gamelists when it exits.

## Controller and hotkeys

Tested with an 8BitDo NS30 Pro in Switch mode over Bluetooth (macOS sees it as a *Switch Pro Controller*). Switch mode is the right mode on a Mac: X-input only works over USB and macOS has no driver for it, while Switch mode uses Apple's GameController framework.

macOS reports this pad by printed letter, but RetroArch 1.22's `mfi` driver ignores the button numbers in controller profiles and always delivers the printed A as RetroPad B, B as A, X as Y and Y as X. Two things put it right: per-core remaps in [`config/remaps`](config/remaps) cross A/B and X/Y back, so games get the SNES layout printed on the pad (B jumps and Y runs in Donkey Kong Country). In arcade games Y is Button 1, B Button 2, X Button 3 and A Button 4 (fire on Y and jump on B; on Neo Geo, Y and X punch, B and A kick), and coin is −; and `menu_swap_ok_cancel_buttons` makes the menu work like a Switch: **A confirms, B goes back**. The profile in [`config/autoconfig/mfi`](config/autoconfig/mfi/8BitDo_NS30_Pro_Switch.cfg) adds the digital ZL/ZR binds the hotkeys use. If you edit a core's controls in *Quick Menu → Controls* and save a remap, keep those four lines. It applies to port 1 in every core.

Hotkeys: **hold ZL** and press:

| Combo | Action |
|---|---|
| ZL + `+` | Open / close the menu |
| ZL + `−` | Close the game (back to ES-DE, or to RetroArch's menu if you started it there) |
| ZL + R | Save state |
| ZL + L | Load state |
| ZL + D-pad → / ← | Next / previous save slot |
| hold ZL + ZR | Fast-forward while held |

HOME is not used because macOS Tahoe keeps it (it opens the Games app). Select is not the hotkey button because RetroArch blocks all game input while that button is held, and games such as Pokémon use Select. ZL is unused on NES, SNES, Game Boy, GBA and Mega Drive; if you add N64, PlayStation or GameCube games, which use ZL, set a different `input_enable_hotkey_btn` in that core's override. Quit RetroArch from *Main Menu → Quit RetroArch*.

## Customising

- **Global settings:** [`config/retroarch.cfg`](config/retroarch.cfg). Each key is commented.
- **Scanline strength:** in a game, *Quick Menu → Shaders → Shader Parameters*. *Scanline Shape Dark Pixels* (`beam_min`, 1.60) and *Scanline Shape Bright Pixels* (`beam_max`, 1.10): higher values give thinner, more visible scanlines; lower values give thicker, softer ones. *Mask Strength* (`maskstr`, 0.55) controls the phosphor mask. If the picture looks dim after making scanlines or the mask stronger, raise *Mask Bloom* (`mask_bloom`, 0.60) or *Bright Boost Bright Pixels* (`brightboost1`, 1.40) rather than the general brightness, which washes out colours. To keep a change for every system, edit [`config/shaders/presets/global.slangp`](config/shaders/presets/global.slangp) and run `./install.sh` again, or use *Save → Save Global Preset* in that menu.
- **Shader per core:** `config/shaders/presets/<Core>/<Core>.slangp`. Cores without one use `global.slangp`; 3D cores have a plain `stock` preset (no filter). Each one references a shader in the slang pack, so you can point it at `crt/crt-royale.slangp`, `crt/crt-guest-advanced.slangp`, `bezel/Mega_Bezel/...`, etc. Folder names must match the core's internal library name (for example `MAME 2010`, `dolphin-emu`, `freeintv`, `ParaLLEl PS2`), which is not always the name shown in the menu.
- **Shader per content folder:** `config/shaders/presets/Genesis Plus GX/gamegear.slangp` gives Game Gear an LCD filter, even though it shares its core with the Mega Drive.
- **Button remaps per core:** `config/remaps/<Core>/<Core>.rmp`, named like the shader folders. Add one for a new core by copying an existing file.
- **Per-core settings and options:** `config/overrides/<Core>/<Core>.cfg` (run-ahead) and `.opt` (internal resolution).

Run `./install.sh` again after editing.

## Bezels

[`tools/make_bezels.py`](tools/make_bezels.py), run by `install.sh`, downloads one system image per console from The Bezel Project (pinned to a commit) into `~/Library/Application Support/RetroArch/overlays/bezels`, and writes a RetroArch overlay that places it around the game. It then adds content folder overrides, `config/<Core>/<folder>.cfg` (for example `Snes9x/snes.cfg` and `Gambatte/gbc.cfg`), for every core that runs the system. They turn the overlay on at full opacity and set a centred custom viewport in place of integer scaling. The viewport is the largest whole-number multiple of the game's lines that fits inside the artwork's screen hole. The artwork is scaled to the screen width, or slightly wider (at most 2% off each side) when that lets the game be one step larger.

- **Screen size:** the layout is computed for 2560×1606 pixels: the 2560×1664 MacBook Air panel minus the band beside the camera notch, which RetroArch leaves out in full screen. On a different display, run `python3 tools/make_bezels.py --screen WIDTHxHEIGHT` with the size RetroArch logs as `[Vulkan] Using resolution` (start it with `--verbose`). On a display of another size the artwork and the game would not line up.
- **Turn them off:** `python3 tools/make_bezels.py --remove` takes the keys out of the overrides again, and `./install.sh --no-bezels` stops adding them. For a single game, *Quick Menu → On-Screen Overlay → Display Overlay*.
- **Lines per frame:** the viewport assumes 224 lines for NES, SNES and Mega Drive (Nestopia's default overscan crop). A game or core that outputs a different number, such as a SNES game in 239-line mode or FCEUmm showing all 240 NES lines, is drawn at a slightly non-whole scale.
- **ROMs on an external drive:** the overrides match the name of the folder that holds the game, so keep the system folder names (`snes`, `gba`…) on the drive too.

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
| [7. ES-DE Frontend](docs/guides/07-es-de.pdf) | The game browser, artwork from the playlists, ScreenScraper, themes, controls |

The guides are written in Markdown in [`docs/guides/src/`](docs/guides/src). After editing them, regenerate every PDF with one command (needs Node.js and Google Chrome; the first run installs two npm packages into `docs/node_modules`):

```bash
./docs/build-guides.sh
```

The script renders each guide with a shared stylesheet in headless Chrome, measures the content and uses that height as the page size, so each PDF is one page. It stops if a guide grows past 200 inches, the page-height limit of most PDF viewers; split such a guide in two.

## Backup and restore

The repository restores the setup, not your saves, BIOS files or ROMs. `backup.sh` copies those user folders (saves, states, system, playlists, configuration, controller profiles, the ES-DE settings, gamelists and collections and, with `--roms`, your games) into a dated folder wherever you choose; `restore.sh` puts them back after `install.sh` on a new Mac.

```bash
./backup.sh /Volumes/MyDrive --roms ~/Games/roms
./restore.sh /Volumes/MyDrive/retroarch-backup-<date>
```

See the [Backup and Restore guide](docs/guides/05-backup-restore.pdf) for the full list and the steps for a freshly formatted Mac.

## Troubleshooting

**Games or the menu freeze after a few seconds, or feel slow and choppy.**
On RetroArch 1.22.x with macOS 26, the Metal video driver stalls 10–20 seconds into a game: CPU use drops to zero, RetroArch stops answering, and no error is logged (reproduced with Snes9x on 1.22.2, a MacBook Air M4 and macOS 26; not caused by App Nap or window focus). Vulkan and glcore are not affected. This setup uses Vulkan; check that `video_driver = "vulkan"` is set in Settings → Drivers. The libretro docs also describe the Metal driver as experimental.

**3D games (PSP, N64, Dreamcast, GameCube, PS1 with Beetle PSX HW) are slow or show nothing.**
The Metal driver gives cores no hardware 3D context, so they fall back to software rendering. Use Vulkan. Cores that only support OpenGL (melonDS DS for upscaling, Mupen64Plus-Next) are switched to glcore automatically, because `driver_switch_enable` is on.

**RetroArch is slow overall.**
Check that it is not the Intel build running under Rosetta: `lipo -archs /Applications/RetroArch.app/Contents/MacOS/RetroArch` must include `arm64`. If it does not, run `./install.sh --replace-intel`. Low Power Mode also reduces performance.

**A game says files are missing, or does not start.**
Run `python3 tools/check_bios.py`. For arcade games, the set probably does not match the core's MAME version; run the `--report` described above.

**A shader or override is not applied.**
The preset or override folder must be named after the core's internal library name. To find it, open a game and look in `~/Library/Application Support/RetroArch/config`: RetroArch creates a folder named after each core it has run.

**Thumbnails do not appear.**
Thumbnails are matched by the playlist label. Rebuild the playlist with `tools/make_playlists.py`, which downloads the artwork by official name and saves it under each game's title. Some games have no artwork on the libretro server.

**Launching RetroArch from the terminal pauses it.**
With *Pause when focus is lost* enabled, a window launched behind the terminal pauses immediately. Click the window, or set `pause_nonactive = "false"`.

**My settings were overwritten.**
Every run of `install.sh` first backs up `config/`, `shaders/presets/` and the ES-DE settings to `~/RetroArch-backups/install-<date>`, keeping the three newest. Copy the files back from there. These copies hold settings only; use `backup.sh` for your games, saves and BIOS.

## Legal

This repository contains only configuration, scripts and documentation, under the MIT license. Cores, shaders and emulator data are downloaded from libretro at install time, and the bezel artwork from The Bezel Project; each keeps its own license. Use it only with games and firmware you own.
