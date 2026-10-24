# MAME and Arcade

Arcade games work differently from console games. This guide explains which romset each installed MAME core expects, how to keep your files intact, and how to tell a broken game from an incompatible set.

[[toc]]

## The arcade cores in this setup

`cores.tsv` installs two MAME cores for the `arcade` folder. Each one is frozen at a specific MAME version, and each version expects ROM files built for it.

| Core | Based on MAME | Romset it expects | Role in this setup |
|---|---|---|---|
| **MAME 2003-Plus** (`mame2003_plus`) | 0.78, plus many later fixes and added games | MAME 2003-Plus set | Default core: tried first for every game |
| **MAME 2010** (`mame2010`) | 0.139 | MAME 0.139 set | Fallback for games 2003-Plus cannot run |

Both use the `crt-easymode` shader, set in `config/shaders/presets/MAME 2003-Plus/` and `config/shaders/presets/MAME 2010/`. MAME 2003-Plus also gets one frame of run-ahead from `config/overrides/MAME 2003-Plus/`; MAME 2010 does not, because it has no save states and run-ahead depends on them. No bezels are installed; the slang shader pack includes the Mega Bezel presets if you want to add them later (see the *Customising* section of the README).

The playlist tool can also evaluate MAME 2003 (`mame2003`, 0.78) and FinalBurn Neo (`fbneo`). They are not installed by default; add them to the `arcade` row of `cores.tsv` and run `./install.sh` if the report below shows they would help.

## Why MAME zips must stay as they are

A console ROM is one file. An arcade game is a circuit board with many chips: program code, graphics, sound. A MAME zip holds one file per chip, and MAME checks every one by **file name** and **CRC**.

> [!WARNING]
> **Never unzip, re-compress or rename MAME zips.** MAME finds a game by the zip name (`sf2.zip` is *Street Fighter II*) and finds each chip by its name inside the zip. A zip renamed to `Street Fighter II.zip` is invisible to MAME, and an unzipped folder of chips is not loaded. The same applies to BIOS zips like `neogeo.zip`: keep them in the `arcade` folder, next to the games.

The friendly names you see in the playlist come from the DAT, not from the file names, so there is never a reason to rename.

## Merged, split and non-merged sets

Many arcade games exist in several versions: a **parent** (usually the world release) and **clones** (other regions, revisions, bootlegs). Clones share most chips with their parent. Romsets differ in where those shared chips are stored.

| Set type | What is in each zip | Needs other zips? | Size |
|---|---|---|---|
| **Non-merged** | Every chip the game needs, including the ones shared with the parent | Only BIOS zips | Largest |
| **Split** | Parents hold their chips; each clone zip holds only the chips that differ | Clones need the parent zip | Medium |
| **Merged** | One zip per family: the parent and all its clones together | Only BIOS zips | Smallest |

In plain terms: **non-merged** is like giving each player a full copy of the board; **split** is like giving clones only the parts that differ and lending them the rest from the parent; **merged** puts the whole family in one box.

All three work with RetroArch's MAME cores, as long as the zips match the core's MAME version and the parent and BIOS zips are present when needed. The playlist tool checks this for you: it counts a game as playable when its own chips, its parent's chips and its BIOS chips are all available somewhere in the folder.

> [!TIP]
> If you rebuild a set, choose **split** or **non-merged**. A split set is compact and the easiest for the playlist tool to check game by game.

## Where the files go

| What | Where |
|---|---|
| Game and BIOS zips | `~/Games/roms/arcade/` (flat, no sub-folders) |
| CHD hard-disk and CD images | `~/Games/roms/arcade/<game>/<file>.chd`, in a folder named exactly like the game's zip, without `.zip` |
| Samples for MAME 2003-Plus | `~/Documents/RetroArch/system/mame2003-plus/samples/` (zipped, e.g. `galaga.zip`) |
| Samples for MAME 2010 | `~/Documents/RetroArch/system/mame2010/samples/` |

This shows the CHD layout. Here the game zip and its hard-disk image sit side by side.

```text
~/Games/roms/arcade/
├── kinst.zip
└── kinst/
    └── kinst.chd
```

> [!NOTE]
> Games that need a CHD are left out of the generated playlist, because the tool cannot check the CHD's contents. You can still start them from **Load Content**.

**Samples** are recordings of sounds some early arcade boards produced with analogue circuits, such as the explosions in *Asteroids* or the voices in *Galaga*. Games run without them, but those sounds are missing. Keep sample zips zipped too.

## Building the arcade playlist

The arcade playlist is built with its own tool, which assigns each game to the first core that can run it.

This measures how much of your set each core can run, without changing anything. Use it before deciding on cores.

```bash
python3 tools/make_arcade_playlist.py --report
```

This adds FinalBurn Neo and plain MAME 2003 to the comparison. The tool downloads each core's DAT the first time.

```bash
python3 tools/make_arcade_playlist.py --cores mame2003_plus,mame2010,fbneo,mame2003 --report
```

This builds `MAME.lpl` with the two installed cores, trying MAME 2003-Plus first, and downloads box art and snaps.

```bash
python3 tools/make_arcade_playlist.py
```

If your arcade zips are somewhere else, pass the folder.

```bash
python3 tools/make_arcade_playlist.py --roms /Volumes/Games/roms/arcade
```

What the tool does:

1. Reads the list of files and CRCs inside each zip (it does not unpack them).
2. Compares them with the official DAT of each core, downloaded from the core's repository and cached in `~/Library/Caches/retroarch-macos-arcade-setup`.
3. Marks a game as playable on a core when every required chip is present (skipping chips the DAT marks as `nodump` or optional) and the core does not flag its driver as not working.
4. Lists parent games only, to keep the list readable. A clone is listed only when its parent does not work on any core.

On a real, untouched MAME 0.122 set of 6,895 zips, the report looked like this. No single core ran much more than half of the set, but combining cores covered far more of it.

```text
mame2003_plus  recognised  4967  playable  3979 (58%)  parents 2250
mame2010       recognised  5817  playable  3925 (57%)  parents 2318
fbneo          recognised  3729  playable  2245 (33%)  parents 1322
combined       playable  5324
```

> [!IMPORTANT]
> Neo Geo games depend on `neogeo.zip`. Its contents changed between MAME versions, so an old `neogeo.zip` can work in MAME 2003-Plus and fail in MAME 2010. The tool takes that into account and assigns the game to the core where its BIOS matches.

## When an arcade game does not start

When a MAME game fails, RetroArch usually returns to the menu with *Failed to load content*, or the core shows a short message about missing files. Almost always the cause is a romset that does not match the core's MAME version.

### 1. Check what the tool thinks

Rebuild the playlist, or run the report. If a game you expect is not in `MAME.lpl`, the installed cores cannot run it with the files you have.

### 2. Read the core's own message

This starts RetroArch from the Terminal with full logging and runs one arcade game directly with MAME 2003-Plus. Replace `sf2` with the zip name.

```bash
/Applications/RetroArch.app/Contents/MacOS/RetroArch --verbose \
  -L ~/Library/Application\ Support/RetroArch/cores/mame2003_plus_libretro.dylib \
  ~/Games/roms/arcade/sf2.zip
```

Look in the output for the chip names MAME complains about:

- `NOT FOUND`: a chip is missing from the zip (or from the parent or BIOS zip).
- `INCORRECT LENGTH` or `WRONG CHECKSUM` / `CRC`: the zip has a different version of that chip, built for another MAME version.
- A missing `neogeo.zip`, `pgm.zip`, `decocass.zip` or similar: a BIOS zip is absent.

### 3. Try the other core

Open the game's playlist entry, choose **Set Core Association** and pick MAME 2010 (or the other way round). Some games need a newer MAME, some an older one.

### 4. Fix the set, not the game

If many games fail, rebuild the set for one core with a ROM manager: **clrmamepro** (Windows, or through Wine), **RomVault** or **igir** (runs on macOS). Point it at your zips and at the core's DAT from the core's repository (MAME 2003-Plus, MAME 2010 or FinalBurn Neo). Rebuilding only re-arranges chips you already have; anything the DAT needs that your files do not contain stays missing.

> [!NOTE]
> A few games run on none of these cores, for example some late CPS-2/CPS-3 and 3D titles. They need a newer MAME than any libretro core in this setup provides.
