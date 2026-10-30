# Backup and Restore

The repository rebuilds the setup, not your data. This guide lists what you must back up yourself, what you can skip, and how to get everything working again on a freshly formatted Mac.

[[toc]]

## What the repository restores

Running `./install.sh` on a new Mac brings back everything that is configuration:

- RetroArch itself (`retroarch-metal` from Homebrew).
- The 48 arm64 cores listed in `cores.tsv`, their info files and the slang shader pack.
- The settings in `config/retroarch.cfg`: Vulkan, XMB, thumbnails, automatic shaders and overrides.
- The per-core shader presets in `config/shaders/presets/`.
- The run-ahead overrides and internal-resolution options in `config/overrides/`.
- Open-source emulator data: Dolphin `Sys`, PPSSPP assets and the PS2 game database.
- The empty ROM, system, playlist, save and state folders.

## What the repository does NOT store

These are yours. They are excluded by `.gitignore` and never pushed, so back them up separately.

| What | Where it lives on this setup | Notes |
|---|---|---|
| **ROMs** | `~/Games/roms/` (or your `--roms` folder) | Usually the largest item. Includes `arcade/` zips, CHDs and samples you keep with them. |
| **BIOS files** | `~/Documents/RetroArch/system/` | Also holds MAME samples (`mame2003-plus/samples`, `mame2010/samples`) and Dolphin/PCSX2 user data. |
| **Game saves** (`.srm`) | `~/Documents/RetroArch/saves/<Core>/` | In-game saves: battery saves, MAME high scores and NVRAM. One sub-folder per core. |
| **Memory cards** | `~/Documents/RetroArch/saves/` and `~/Documents/RetroArch/system/` | PlayStation memory cards are `.srm` files in `saves/`. PSP saves live in `saves/PPSSPP/`. GameCube and PS2 cards are kept by Dolphin and LRPS2 inside their folders in `saves/` or `system/`. Backing up both folders covers all of them. |
| **Save states** | `~/Documents/RetroArch/states/<Core>/` | `.state`, `.state1`… files and their screenshots. |
| **Screenshots** | Next to the game file by default (`screenshot_directory = default`) | To collect them in one place, set **Settings → Directory → Screenshot** to `~/Documents/RetroArch/screenshots`, which `backup.sh` copies. |
| **Playlists, history and favorites** | `~/Documents/RetroArch/playlists/` and `playlists-full/` | Playlists can be rebuilt, but history and favorites cannot. `playlists-full/` holds the complete playlists, including games on an external drive. |
| **Control remaps** | `~/Library/Application Support/RetroArch/config/remaps/` | Per-core and per-game button layouts (`.rmp`). |
| **Core options you changed** | `~/Library/Application Support/RetroArch/config/<Core>/<Core>.opt` | The repository restores its own `.opt` files; changes you made on top are only in your backup. |
| **Per-game overrides** | `~/Library/Application Support/RetroArch/config/<Core>/<Game>.cfg` | Settings saved with **Quick Menu → Overrides → Save Game Overrides**. |
| **Controller profiles you saved** | `~/Library/Application Support/RetroArch/autoconfig/` | Only needed if you created a profile with **Save Controller Profile**; the standard profiles ship with RetroArch. |
| **ES-DE settings, gamelists and collections** | `~/ES-DE/settings/`, `~/ES-DE/gamelists/`, `~/ES-DE/collections/` | Favourites, play counts, names and descriptions from the scraper, custom collections and your ScreenScraper login. |
| **RetroAchievements and Netplay credentials** | `~/Library/Application Support/RetroArch/config/retroarch.cfg` | `cheevos_username`, `cheevos_token` and the Netplay nickname. The repository's config never contains them. |

> [!WARNING]
> Your `retroarch.cfg` can contain your RetroAchievements login token. Keep backups on a private drive or in an encrypted folder, and never commit them to a public repository.

## What you do not need to back up

These are downloaded again, so leave them out of your backup to save space and time:

- **Cores** (`~/Library/Application Support/RetroArch/cores/`): `./install.sh` downloads them from the libretro buildbot.
- **Core info files** (`.../RetroArch/info/`): downloaded by `./install.sh`.
- **Shaders** (`.../RetroArch/shaders/shaders_slang/`): downloaded by `./install.sh`. Your presets come from the repository.
- **Thumbnails** (`.../RetroArch/thumbnails/`): downloaded on demand, or with `tools/make_playlists.py`.
- **DATs and System.dat** (`~/Library/Caches/retroarch-macos-arcade-setup/`): downloaded by the tools on first run.
- **RetroArch itself** and **ES-DE**: installed by Homebrew.
- **ES-DE media** (`~/ES-DE/downloaded_media/`): `tools/make_esde_gamelists.py` links it from the RetroArch thumbnails, and the ES-DE scraper downloads the rest. Copy it by hand if you scraped many videos and do not want to scrape again.
- **ES-DE system files** (`~/ES-DE/custom_systems/`): written by `./install.sh`, which also selects the bundled Slate theme. Themes you download from ES-DE (`~/ES-DE/themes/`) are not backed up.

## Back up with backup.sh

`backup.sh` copies exactly the user folders from the table above into a dated folder at a location you choose, such as an external drive. It skips cores, shaders and thumbnails. ROMs are copied only when you ask for them.

Quit RetroArch first; the script refuses to run while it is open, so saves are fully written.

This backs up saves, states, the system folder, playlists, screenshots, configuration and controller profiles to an external drive called *MyDrive*.

```bash
./backup.sh /Volumes/MyDrive
```

This also copies your ROM folder. It can take a while, depending on the size of your collection.

```bash
./backup.sh /Volumes/MyDrive --roms ~/Games/roms
```

Each run creates a new folder, for example `/Volumes/MyDrive/retroarch-backup-20261024-115355/`, with a `manifest.txt` that records the date, the RetroArch version and the size of each part:

```text
retroarch-backup-20261024-115355/
├── manifest.txt
├── saves/
├── states/
├── system/
├── playlists/
├── config/
├── autoconfig/
└── roms/            only with --roms
```

> [!TIP]
> Time Machine also covers all of these folders, because they are inside your home folder. `backup.sh` is still useful for a small, self-contained copy that you can restore in one step, without restoring the whole Mac.

## Restore on a freshly formatted Mac

Follow these steps in order. Installing first and restoring afterwards means your saves and settings land on top of a working setup.

### 1. Install the Command Line Tools and Homebrew

This installs `git` and `python3`.

```bash
xcode-select --install
```

This installs Homebrew. When it finishes, run the two commands it prints to add it to your shell, then open a new Terminal window.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Clone the repository and run the installer

This downloads the setup and installs RetroArch, the cores, the shaders and the configuration.

```bash
git clone https://github.com/mbarradev-debug/retroarch-macos-arcade-setup.git
cd retroarch-macos-arcade-setup
./install.sh
```

### 3. Restore your folders

Connect the drive with your backup. This restores the backup over the fresh install. It first saves the new configuration to `~/RetroArch-backups/pre-restore-<date>`, then copies each folder back to its place. Files that exist only on the new Mac are kept.

```bash
./restore.sh /Volumes/MyDrive/retroarch-backup-20261024-115355
```

If the backup contains ROMs and you want them somewhere other than `~/Games/roms`, say where.

```bash
./restore.sh /Volumes/MyDrive/retroarch-backup-20261024-115355 --roms /Volumes/Games/roms
```

If you keep ROMs on their own drive and did not back them up with `--roms`, copy them into `~/Games/roms/` now, keeping the folder names from `cores.tsv`.

> [!NOTE]
> The restored `retroarch.cfg` replaces the fresh one, so it brings back your own settings and RetroAchievements login. Run `./install.sh` once more afterwards to re-apply the repository's settings on top. It backs up first and keeps everything it does not manage.

### 4. Rebuild the playlists

The second run of `./install.sh` from the note above also rebuilds the playlists from your ROM folder, downloads their box art and copies them into ES-DE. If your ROMs live in another folder, pass it the same way:

```bash
./install.sh --roms /Volumes/Games/roms
```

### 5. Verify

This checks that the BIOS files came back intact.

```bash
python3 tools/check_bios.py
```

This counts the restored save files, so you can compare with the old Mac.

```bash
find ~/Documents/RetroArch/saves ~/Documents/RetroArch/states -type f | wc -l
```

Then open RetroArch and check:

1. The video driver is `vulkan` (**Settings → Drivers**), and the XMB menu shows your playlists with box art.
2. A game you had saved loads its in-game save, and **Quick Menu → Load State** finds your states.
3. Your controller works and has your button layout.
4. If you use RetroAchievements, **Settings → Achievements** shows you logged in.
