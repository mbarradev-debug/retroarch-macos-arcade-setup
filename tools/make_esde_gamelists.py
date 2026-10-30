#!/usr/bin/env python3
"""Copy the RetroArch playlists and thumbnails into ES-DE.

For every system with a playlist (from make_playlists.py or
make_arcade_playlist.py) this updates ~/ES-DE/gamelists/<system>/gamelist.xml
and fills ~/ES-DE/downloaded_media/<system> with the thumbnails RetroArch already
downloaded, so ES-DE shows the same official names and artwork without scraping:

  Named_Boxarts -> covers, Named_Snaps -> screenshots, Named_Titles -> titlescreens

- Games keep the playlist name unless ES-DE already has another one (scraped or
  edited by hand).
- Files ES-DE would list but the playlist leaves out are hidden: .bin tracks of
  a .cue, discs of a .m3u, and arcade zips no installed core runs (or clones of
  a parent that runs).
- Arcade games the playlist assigns to an alternate core get that core as their
  per-game emulator, and the genre, year, manufacturer, number of players and
  short name that make_arcade_playlist.py wrote to MAME.meta.json.
- Entries for files that were deleted are removed, unless ES-DE or you added
  something to them (play counts, favourites, scraped data).
- Artwork ES-DE already has (from its scraper, for example) is kept.

Run make_esde_config.py first, and quit ES-DE: it rewrites gamelists when it exits.
Usage: make_esde_gamelists.py [--roms DIR]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

ESDE = os.path.expanduser("~/ES-DE")
SYSTEMS = os.path.join(ESDE, "custom_systems", "es_systems.xml")
RA = os.path.expanduser("~/Library/Application Support/RetroArch")
PLAYLISTS = os.path.expanduser("~/Documents/RetroArch/playlists-full")
HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = {"Named_Boxarts": "covers", "Named_Snaps": "screenshots", "Named_Titles": "titlescreens"}
IMAGE_EXT = (".png", ".jpg", ".jpeg")
# tags this tool writes; an entry holding only these can be dropped with its file
OWN_TAGS = {"path", "name", "hidden", "altemulator", "genre", "releasedate", "developer", "publisher", "players"}


def load_systems():
    """(folder, playlist, ES-DE system) from cores.tsv."""
    systems = []
    with open(os.path.join(HERE, "..", "cores.tsv"), encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            folder, playlist, _dat, _core, _alternates, esde = (line.rstrip("\n").split("\t") + [""] * 6)[:6]
            systems.append((folder, playlist, esde or folder))
    return systems


def load_esde_systems():
    """ES-DE system -> (extensions, [(core, label)] with the default first)."""
    systems = {}
    for s in ET.parse(SYSTEMS).getroot().findall("system"):
        cores = []
        for command in s.findall("command"):
            m = re.search(r"%CORE_RETROARCH%/(\S+)_libretro\.dylib", command.text or "")
            if m:
                cores.append((m.group(1), command.get("label")))
        systems[s.findtext("name")] = (set(s.findtext("extension").split()), cores)
    return systems


def thumb_name(label):
    return re.sub(r'[&*/:`<>?\\|"]', "_", label) + ".png"


def rom_files(folder, extensions):
    """Paths relative to the system folder of every file ES-DE would list."""
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if not f.startswith(".") and os.path.splitext(f)[1] in extensions:
                yield os.path.relpath(os.path.join(root, f), folder)


def set_text(game, tag, value):
    node = game.find(tag)
    if value is None:
        if node is not None:
            game.remove(node)
        return
    if node is None:
        node = ET.SubElement(game, tag)
    node.text = value


def link_media(system, playlist, label, rel):
    """Hard-link (or copy) the playlist thumbnails as ES-DE media; returns how many were added."""
    added = 0
    stem = os.path.splitext(rel)[0]
    for kind, media in MEDIA.items():
        src = os.path.join(RA, "thumbnails", playlist, kind, thumb_name(label))
        dest = os.path.join(ESDE, "downloaded_media", system, media, stem + ".png")
        if not os.path.exists(src) or any(os.path.exists(os.path.splitext(dest)[0] + e) for e in IMAGE_EXT):
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        try:
            os.link(src, dest)
        except OSError:
            shutil.copy2(src, dest)
        added += 1
    return added


def update_system(folder, playlist, system, extensions, cores, roms):
    lpl = os.path.join(PLAYLISTS, playlist + ".lpl")
    rom_dir = os.path.join(roms, folder)
    if not os.path.exists(lpl) or not os.path.isdir(rom_dir):
        return
    meta_path = os.path.join(PLAYLISTS, playlist + ".meta.json")
    meta = json.load(open(meta_path, encoding="utf-8")) if os.path.exists(meta_path) else {}
    items = {}
    for item in json.load(open(lpl, encoding="utf-8"))["items"]:
        path = os.path.abspath(item["path"])
        if path.startswith(rom_dir + os.sep):
            items[os.path.relpath(path, rom_dir)] = item

    gamelist = os.path.join(ESDE, "gamelists", system, "gamelist.xml")
    root = ET.parse(gamelist).getroot() if os.path.exists(gamelist) else ET.Element("gameList")
    games = {}
    for game in root.findall("game"):
        games[os.path.normpath(game.findtext("path", "").removeprefix("./"))] = game
    default_core = cores[0][0] if cores else None
    labels = dict(cores)

    files = set(rom_files(rom_dir, extensions))
    removed = 0
    for rel, game in games.items():
        if rel not in files and rel not in items and {c.tag for c in game} <= OWN_TAGS:
            root.remove(game)
            removed += 1

    hidden = media = 0
    for rel in sorted(files | set(items)):
        game = games.get(rel)
        if game is None:
            game = ET.SubElement(root, "game")
            set_text(game, "path", "./" + rel)
        item = items.get(rel)
        if item is None:
            set_text(game, "hidden", "true")
            hidden += 1
            continue
        if game.findtext("hidden") == "true":
            set_text(game, "hidden", None)
        info = meta.get(rel, {})
        name = game.findtext("name")
        if not name or name in (os.path.splitext(os.path.basename(rel))[0], item["label"]):
            set_text(game, "name", info.get("name") or item["label"])
        for tag, value in (("genre", info.get("genre")), ("developer", info.get("developer")),
                           ("publisher", info.get("developer")), ("players", info.get("players")),
                           ("releasedate", info["year"] + "0101T000000" if info.get("year") else None)):
            if value and not game.findtext(tag):
                set_text(game, tag, value)
        core = os.path.basename(item.get("core_path", "")).removesuffix("_libretro.dylib")
        if core in labels and default_core and folder == "arcade":
            set_text(game, "altemulator", labels[core] if core != default_core else None)
        media += link_media(system, playlist, item["label"], rel)

    ET.indent(root, space="\t")
    os.makedirs(os.path.dirname(gamelist), exist_ok=True)
    ET.ElementTree(root).write(gamelist, encoding="utf-8", xml_declaration=True)
    print(f"{system}: {len(items)} games, {hidden} hidden files, {media} images added"
          + (f", {removed} entries of deleted files removed" if removed else ""))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--roms", default=os.path.expanduser("~/Games/roms"), help="folder with one sub-folder per system")
    args = parser.parse_args()
    if not os.path.exists(SYSTEMS):
        parser.error(f"{SYSTEMS} not found; run tools/make_esde_config.py first")
    if subprocess.run(["pgrep", "-x", "ES-DE"], capture_output=True).returncode == 0:
        parser.error("quit ES-DE first; it rewrites its gamelists when it exits")

    roms = os.path.abspath(os.path.expanduser(args.roms))
    esde_systems = load_esde_systems()
    for folder, playlist, system in load_systems():
        if system in esde_systems:
            update_system(folder, playlist, system, *esde_systems[system], roms)


if __name__ == "__main__":
    main()
