# Quick Start

From a clean Apple Silicon Mac to a working RetroArch with native cores, CRT shaders and the XMB menu in about ten minutes.

[[toc]]

## What you need

- **A Mac with Apple Silicon** (M1, M2, M3, M4 or later). The installer stops on Intel Macs, because every core it downloads is an arm64 build.
- **macOS** with an internet connection. The setup was tested on macOS 26 with RetroArch 1.22.2.
- **Homebrew**, the package manager used to install RetroArch.
- **Git and Python 3**, both included in Apple's Command Line Tools.
- **About 1 GB of free disk space** for RetroArch, cores, shaders and emulator data. Your games come on top of that.

This command installs Apple's Command Line Tools, which provide `git` and `python3`. Skip it if they are already installed.

```bash
xcode-select --install
```

This command installs Homebrew. It is the official one-liner from brew.sh.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

> [!NOTE]
> At the end, Homebrew prints two commands that add `/opt/homebrew/bin` to your shell. Run them, then open a new Terminal window before you continue.

## Get the repository

This downloads the setup into a folder called `retroarch-macos-arcade-setup` and moves into it.

```bash
git clone https://github.com/mbarradev-debug/retroarch-macos-arcade-setup.git
cd retroarch-macos-arcade-setup
```

## Run the installer

Quit RetroArch first if it is open. RetroArch rewrites its configuration when it exits, which would undo the installer's changes.

This runs the installer with the default ROM folder, `~/Games/roms`.

```bash
./install.sh
```

To keep your games somewhere else, pass the folder with `--roms`. This example uses an external drive.

```bash
./install.sh --roms /Volumes/Games/roms
```

### What the installer does

1. Installs RetroArch with Homebrew (`retroarch-metal`, the native universal build), unless `/Applications/RetroArch.app` already exists.
2. Backs up `~/Library/Application Support/RetroArch/config` and `shaders/presets` to `~/RetroArch-backup-<date>`, if they exist.
3. Creates the folders: one ROM folder per system, plus `~/Documents/RetroArch/system`, `playlists`, `saves` and `states`.
4. Downloads the arm64 build of every core listed in `cores.tsv` (48 cores) from the libretro buildbot, along with the core info files.
5. Downloads the slang shader pack and installs the per-core shader presets.
6. Downloads open-source emulator data into the system folder: Dolphin's `Sys` folder, PPSSPP's assets and the PS2 game database. It does not download any BIOS.
7. Merges the settings from `config/retroarch.cfg` and the per-core overrides into your configuration. Settings it does not manage are left alone.

> [!TIP]
> The installer is safe to run again. It backs up first, skips anything already downloaded and merges settings instead of replacing files. Run `./install.sh --update` to refresh cores, info files, shaders and emulator data.

### If you already had the Intel version

The Homebrew cask `retroarch` is an Intel-only build that runs under Rosetta and is noticeably slower. When the installer finds it, it prints a warning. This command swaps it for the native build. Your settings are kept.

```bash
./install.sh --replace-intel
```

## First launch

Open **RetroArch** from the Applications folder or with Spotlight. You should see the **XMB** menu: a horizontal row of categories (Main Menu, Settings, History, playlists) over an animated background.

1. Use the **arrow keys** to move, **Enter** to confirm and **Backspace** to go back. A connected controller works too: RetroArch configures most controllers on its own.
2. Put a game you own in its system folder, for example `~/Games/roms/snes/`. Then open **Load Content** in the Main Menu and pick it. The [ROMs guide](02-roms.pdf) explains the folder for each system.
3. While a game runs, press **F1** to open the Quick Menu, where you can save states, change the shader or open the core options. Press **Esc** twice to quit.

> [!IMPORTANT]
> Some systems need BIOS files from your own consoles, for example PlayStation, Saturn, Sega CD and PC Engine CD. Without them those games will not start. See the [BIOS guide](04-bios.pdf).

## Check that everything worked

These checks take a minute and confirm the parts that matter most.

This should print `x86_64 arm64`. If `arm64` is missing, you are running the Intel build; use `--replace-intel`.

```bash
lipo -archs /Applications/RetroArch.app/Contents/MacOS/RetroArch
```

This counts the installed cores. It should print 48.

```bash
ls ~/Library/Application\ Support/RetroArch/cores/*.dylib | wc -l
```

This shows the video driver and the menu. You should see `video_driver = "vulkan"` and `menu_driver = "xmb"`.

```bash
grep -E '^(video_driver|menu_driver) ' ~/Library/Application\ Support/RetroArch/config/retroarch.cfg
```

You can also check inside RetroArch:

- **Settings → Drivers → Video** shows `vulkan`.
- **Main Menu → Load Core** lists the installed cores, such as Snes9x, mGBA, MAME 2003-Plus and PPSSPP.
- When you start a SNES or Mega Drive game, faint CRT scanlines appear. A Game Boy or GBA game shows an LCD pixel grid instead.

> [!WARNING]
> Do not switch the video driver to **metal**. On RetroArch 1.22.x with macOS 26, the Metal driver freezes about nine seconds after starting, in both the menu and in games. It also cannot run hardware-accelerated 3D cores. The [Troubleshooting guide](06-troubleshooting.pdf) explains why.

## Next steps

- [ROMs](02-roms.pdf): folder layout, file formats and building playlists with box art.
- [MAME and arcade](03-mame-arcade.pdf): which romset each arcade core needs.
- [BIOS](04-bios.pdf): where firmware goes and how to verify it.
- [Backup and restore](05-backup-restore.pdf): what to back up, and how to rebuild a freshly formatted Mac.
- [Troubleshooting and FAQ](06-troubleshooting.pdf): slow games, missing files, controls, logs.
