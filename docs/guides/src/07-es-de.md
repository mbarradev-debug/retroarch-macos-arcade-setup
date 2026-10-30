# ES-DE Frontend

[ES-DE](https://www.es-de.org/) (EmulationStation Desktop Edition) is a game browser built for TV and controller use: one screen per system, themes with system logos, and each game's box art, screenshot, title screen and video side by side. It does not emulate anything itself. Every game still runs in RetroArch with the cores, shaders and settings from this setup.

[[toc]]

## What install.sh sets up

`./install.sh` installs ES-DE with Homebrew (`brew install --cask es-de`) and runs `tools/make_esde_config.py`, which writes three files:

| File | What it holds |
|---|---|
| `~/ES-DE/custom_systems/es_systems.xml` | One entry per system in `cores.tsv`. It replaces ES-DE's built-in entry of the same name, so ES-DE reads this setup's folders (`lynx`, `pce`, `wswan`…) and starts games with the default core from `cores.tsv`. The alternate cores are offered after it. |
| `~/ES-DE/custom_systems/es_find_rules.xml` | Where to find RetroArch: the *RetroArch CRT* launcher first, so the 1:1 display mode applies to games started from ES-DE too, and `/Applications/RetroArch.app` if the launcher was not built. |
| `~/ES-DE/settings/es_settings.xml` | Only these settings are changed: `ROMDirectory` (your `--roms` folder), `ShowHiddenGames` (off) and the theme (`Theme` Slate, `ThemeVariant` text list with videos, `ThemeColorScheme` dark). ES-DE adds its own defaults on first start. |

Both files in `custom_systems` are rewritten on every run of `install.sh`; put your own changes in `cores.tsv` instead. To skip ES-DE entirely, run `./install.sh --no-esde`.

> [!NOTE]
> ES-DE uses its own system names, which differ from some of this setup's folder names. You do not need to rename anything: the custom systems file maps them. For example, `lynx` is ES-DE's `atarilynx`, `gamecube` is `gc` and `pce` is `pcengine`; the last column of `cores.tsv` lists them all.

## Bring your games and artwork across

`./install.sh` builds the RetroArch playlists and then copies them into ES-DE with `tools/make_esde_gamelists.py`. After adding games, run it again:

```bash
./install.sh
```

ES-DE lists a new game file as soon as it starts, but its name, artwork and details come from that step. To have it happen by itself, install once with `--esde-auto-update`:

```bash
./install.sh --esde-auto-update
```

This turns on **Other settings → Enable custom event scripts** and writes `~/ES-DE/scripts/quit/update-games.sh`. Each time ES-DE quits, that script starts `tools/update_games.sh` in the background; it waits until ES-DE has closed, then deletes `._` files, rebuilds the playlists, downloads artwork and updates the gamelists. Copy games in, open and close ES-DE once, and the next time it opens they have their artwork. The output goes to `~/ES-DE/logs/update-games.log`. The script points at this repository's folder, so run `./install.sh --esde-auto-update` again if you move it. To stop it, delete the script or turn the setting off.

`make_esde_gamelists.py` writes `~/ES-DE/gamelists/<system>/gamelist.xml` and fills `~/ES-DE/downloaded_media/<system>/` from what RetroArch already has:

- **Names:** the clean title from the playlist, without region or revision tags. A name that ES-DE's scraper or you already set is kept; a console name ending in tags such as *(USA)* counts as a file name and is replaced.
- **Artwork:** RetroArch's box art becomes ES-DE's `covers`, snaps become `screenshots` and title screens become `titlescreens`. The files are hard-linked, so they take no extra space. Artwork ES-DE already has is kept.
- **Hidden files:** files ES-DE would list but RetroArch's playlist leaves out: the `.bin` tracks of a `.cue`, the discs of a `.m3u`, arcade zips no installed core can run, and clones whose parent runs. They are marked hidden, not deleted.
- **Arcade cores:** a game the MAME playlist assigns to MAME 2010 gets MAME 2010 as its per-game emulator; the rest use MAME 2003-Plus.
- **Console details:** genre, release year, developer, publisher and number of players, from libretro-database's metadata files. Disc games have few of them.
- **Arcade details:** genre, year, manufacturer, number of players and a short name without the version in brackets, from the MAME data files (see the MAME guide).
- **Deleted games:** entries for files you deleted are removed, unless they hold play counts, favourites or scraped data.

Run it again after adding games or rebuilding a playlist. Quit ES-DE first: it rewrites its gamelists when it exits, and the tool refuses to run while ES-DE is open.

## Scraping for videos and richer artwork

The libretro thumbnails cover box art, screenshots and title screens. ES-DE's own scraper adds videos, marquees (logos), 3D boxes, descriptions, release dates and ratings, which most themes use.

1. Create a free account at [screenscraper.fr](https://www.screenscraper.fr). Without one, ScreenScraper is slow and limits how many games you can scrape per day.
2. In ES-DE, open the main menu (Start) and choose **Scraper**.
3. Set **Scrape from** to *ScreenScraper*, then under **Account settings** turn on *Use this account for ScreenScraper* and enter your user name and password.
4. Under **Content settings**, choose the media you want. Videos take the most space, roughly 5–10 MB per game.
5. Choose **Scrape these systems**, pick the systems, and **Start**.

To keep the artwork from RetroArch and only fill in what is missing, turn off **Other settings → Overwrite files and data** in the scraper menu before you start.

> [!WARNING]
> ES-DE stores the ScreenScraper password in plain text in `~/ES-DE/settings/es_settings.xml`. `backup.sh` copies that folder, so keep backups private.

## Themes

This setup uses **Slate**, one of the themes bundled with ES-DE, with its *Textlist with videos* variant and the *Dark* colour scheme. Being bundled, it needs no download and is updated together with ES-DE.

To try others, use **UI settings → Theme downloader**, then pick a theme under **UI settings → Theme**. Each theme has its own *variants* (layouts with or without video, with a grid or a list), *colour schemes* and *aspect ratios*; on a MacBook choose **16:10** where the theme offers it. Each run of `./install.sh` switches back to Slate. To keep another theme, change `THEME` and the theme settings at the top of `tools/make_esde_config.py`; for a theme that is not bundled, also set `THEME_URL` to its git URL so `./install.sh` downloads it (and `--update` pulls it again).

## Controls

ES-DE has its own controller mapping, separate from RetroArch's. It detects the 8BitDo NS30 Pro in Switch mode automatically.

- **A** opens a system or launches a game, **B** goes back, **Start** opens the main menu, **Back/Select** opens the options for the current game list.
- If A and B feel reversed, turn on **Input device settings → Swap the A/B and X/Y buttons**.
- **Input device settings → Controller type → Switch Pro** makes the on-screen help show Switch button names.
- While a game is running, the RetroArch hotkeys from the main README apply. **ZL + `−`** closes the game and quits RetroArch, so you are back in ES-DE (`quit_on_close_content = "2"`: games started from RetroArch's own menu still return to that menu).
- **ZL + `+`** opens RetroArch's Quick Menu over the game, for save states, shader parameters and core options. Press **ZL + `+`** again to resume.

## Choosing a different core

- **For every game of a system:** **Other settings → Alternative emulators**, pick the system and the core.
- **For one game:** select the game, press **Back/Select**, choose **Edit this game's metadata** and set **Alternative emulator**.

Only the cores listed in `cores.tsv` are offered. To add one, add it to the alternates column of `cores.tsv` and run `./install.sh` again: that downloads the core and updates the ES-DE entry.

## Common problems

**A system is missing in ES-DE.**
ES-DE only shows systems with at least one game. Check that the folder in your ROM directory matches the first column of `cores.tsv`, and that the file extension is one ES-DE accepts for that system (listed in the `<extension>` line of `~/ES-DE/custom_systems/es_systems.xml`).

**ES-DE says the emulator or core is not found.**
Run `./install.sh` again. It downloads any missing cores and rewrites the custom systems file. The log is at `~/ES-DE/logs/es_log.txt`.

**A game shows twice, or a `.bin` file appears as a game.**
Run `python3 tools/make_esde_gamelists.py`. It hides track and disc files referenced by `.cue` and `.m3u` files. To list the hidden files anyway, turn on **Other settings → Show hidden games**.

**The ES-DE window changes size when a game starts.**
The *RetroArch CRT* launcher switches the display to 1280×832 points while RetroArch runs, and macOS restores the previous mode when it quits. ES-DE follows the change. If you prefer no switch, delete `~/Applications/RetroArch CRT.app`; ES-DE then starts RetroArch directly.
