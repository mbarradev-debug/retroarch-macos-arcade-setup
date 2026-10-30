#!/usr/bin/env python3
"""Build one RetroArch playlist per console system and fetch its thumbnails.

Expects one sub-folder per system inside the ROM folder, named as in cores.tsv
(snes, gba, psx, ...). Games are identified by CRC (inside zips, or of the raw
file for cartridge-sized files) against libretro-database DATs, falling back to
the file name with or without region tags.

Games are listed by a clean title: the official name without region, language
and revision tags ("Legend of Zelda, The - The Minish Cap (Europe) (En,Fr)" ->
"The Legend of Zelda - The Minish Cap"). A file you already named that way
(capitals or spaces, no brackets) keeps its own name, so "Pokemon Rubi.zip" stays
"Pokemon Rubi". When versions of one game would share a title, those not named
that way show their file name. Thumbnails are fetched by the official name and
saved under the title, since RetroArch matches them by label.

Next to each playlist it writes <playlist>.meta.json with the genre, release
year, developer, publisher and number of players from libretro-database's
metadat DATs, which make_esde_gamelists.py copies into ES-DE.
Arcade is handled separately by make_arcade_playlist.py.
Usage: make_playlists.py [--roms DIR] [--no-thumbnails]
"""
import argparse
import collections
import json
import os
import re
import urllib.parse
import urllib.request
import zipfile
import zlib
from concurrent.futures import ThreadPoolExecutor

import sync_playlists

HERE = os.path.dirname(os.path.abspath(__file__))
RA = os.path.expanduser("~/Library/Application Support/RetroArch")
# complete playlists; sync_playlists.py shows RetroArch the games present right now
PLAYLISTS = os.path.expanduser("~/Documents/RetroArch/playlists-full")
CACHE = os.path.expanduser("~/Library/Caches/retroarch-macos-arcade-setup/dats")
DB_URL = "https://raw.githubusercontent.com/libretro/libretro-database/master/"
THUMB_TYPES = ("Named_Boxarts", "Named_Snaps", "Named_Titles")
# metadat folder -> meta.json field; not every system has every DAT
META_FIELDS = {"genre": "genre", "releaseyear": "year", "developer": "developer",
               "publisher": "publisher", "maxusers": "players"}
MAX_RAW_CRC = 64 << 20  # hash raw files up to 64 MiB (cartridges); discs match by name
SKIP_EXT = {".sub", ".txt", ".nfo", ".jpg", ".png", ".srm", ".sav"}


def load_systems():
    systems = []
    with open(os.path.join(HERE, "..", "cores.tsv"), encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            folder, playlist, dat, core, _alternates = (line.rstrip("\n").split("\t") + [""])[:5]
            if dat != "-":
                systems.append((folder, playlist, dat, core))
    return systems


def core_display_name(core):
    info = os.path.join(RA, "info", f"{core}_libretro.info")
    if os.path.exists(info):
        m = re.search(r'^display_name\s*=\s*"(.*)"', open(info, encoding="utf-8").read(), re.M)
        if m:
            return m.group(1)
    return core


def fetch_dat(rel, cached=None):
    path = os.path.join(CACHE, cached or os.path.basename(rel))
    if not os.path.exists(path):
        os.makedirs(CACHE, exist_ok=True)
        urllib.request.urlretrieve(DB_URL + urllib.parse.quote(rel), path)
    return path


def load_metadata(system):
    """CRC or official name -> {field: value}, merged from the metadat DATs that exist for the system."""
    meta = {}
    for folder, field in META_FIELDS.items():
        try:
            path = fetch_dat(f"metadat/{folder}/{system}.dat", f"{folder}-{system}.dat")
        except OSError:
            continue
        for block in open(path, encoding="utf-8", errors="ignore").read().split("\ngame (")[1:]:
            value = re.search(rf'^\s*{folder} "([^"]+)"', block, re.M)
            if not value:
                continue
            keys = re.findall(r"crc (\w+)", block) + re.findall(r'^\s*(?:name|comment) "([^"]+)"', block, re.M)
            for key in keys:
                meta.setdefault(key.upper() if re.fullmatch(r"[0-9A-Fa-f]{8}", key) else key, {})[field] = value.group(1)
    return meta


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def clean_title(name):
    """Official name without (region), (languages), (Rev 1) or [tags]; a trailing ", The" moves to the front."""
    title = re.sub(r"\s*[(\[][^)\]]*[)\]]", "", name).strip()
    head, sep, rest = title.partition(" - ")
    if head.endswith(", The"):
        title = "The " + head[:-5] + sep + rest
    return title


def is_clean(stem):
    """A file name chosen by hand: no tags, and not a lowercase slug such as super-mario-world-usa."""
    return not re.search(r"[(\[]", stem) and not re.fullmatch(r"[a-z0-9_.-]+", stem)


def load_dat(path):
    """CRC -> game name, and normalized name (with and without tags) -> game name."""
    by_crc, by_slug = {}, {}
    for block in open(path, encoding="utf-8", errors="ignore").read().split("\ngame (")[1:]:
        name = re.search(r'^\s*name "([^"]+)"', block, re.M)
        if not name:
            continue
        by_slug.setdefault(slug(name.group(1)), name.group(1))
        # a disc matched by title gets the USA entry's artwork when there is one
        key = "title:" + slug(clean_title(name.group(1)))
        if key not in by_slug or "(USA" in name.group(1) and "(USA" not in by_slug[key]:
            by_slug[key] = name.group(1)
        for crc in re.findall(r"rom \( .*?crc (\w+)", block):
            by_crc[crc.upper()] = name.group(1)
    return by_crc, by_slug


def identify(path, by_crc, by_slug):
    crcs = []
    if path.lower().endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            crcs = [f"{i.CRC:08X}" for i in z.infolist()]
    elif os.path.getsize(path) <= MAX_RAW_CRC:
        with open(path, "rb") as f:
            crcs = [f"{zlib.crc32(f.read()) & 0xFFFFFFFF:08X}"]
    for crc in crcs:
        if crc in by_crc:
            return by_crc[crc], crc
    stem = slug(os.path.splitext(os.path.basename(path))[0])
    return by_slug.get(stem) or by_slug.get("title:" + stem), crcs[0] if crcs else "00000000"


def thumb_name(label):
    return re.sub(r'[&*/:`<>?\\|"]', "_", label) + ".png"


def download_thumbs(job):
    system, official, label = job
    got = 0
    for kind in THUMB_TYPES:
        dest = os.path.join(RA, "thumbnails", system, kind, thumb_name(label))
        if os.path.exists(dest):
            got += 1
            continue
        # already downloaded under the official name (older playlists): reuse it
        old = os.path.join(RA, "thumbnails", system, kind, thumb_name(official))
        if os.path.exists(old):
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            os.link(old, dest)
            got += 1
            continue
        url = "https://thumbnails.libretro.com/" + "/".join(urllib.parse.quote(p) for p in (system, kind, thumb_name(official)))
        try:
            data = urllib.request.urlopen(url, timeout=30).read()
        except Exception:
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
        got += 1
    return got


def game_files(folder):
    files = sorted(f for f in os.listdir(folder) if not f.startswith(".") and os.path.isfile(os.path.join(folder, f)))
    # tracks listed in a .cue and discs listed in a .m3u are not separate games
    referenced = set()
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext in (".cue", ".m3u"):
            text = open(os.path.join(folder, f), encoding="utf-8", errors="ignore").read()
            names = re.findall(r'^\s*FILE\s+"([^"]+)"', text, re.M | re.I) if ext == ".cue" else text.splitlines()
            referenced |= {os.path.basename(n.strip()) for n in names if n.strip()}
    for f in files:
        if f in referenced or os.path.splitext(f)[1].lower() in SKIP_EXT:
            continue
        yield os.path.join(folder, f)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--roms", default=os.path.expanduser("~/Games/roms"), help="folder with one sub-folder per system")
    parser.add_argument("--no-thumbnails", action="store_true")
    args = parser.parse_args()

    jobs = []
    for folder, system, dat, core in load_systems():
        src = os.path.join(os.path.expanduser(args.roms), folder)
        if not os.path.isdir(src):
            continue
        by_crc, by_slug = load_dat(fetch_dat(dat))
        metadata = load_metadata(system)
        core_path = os.path.join(RA, "cores", f"{core}_libretro.dylib")
        items, officials, matched = [], [], 0
        for path in game_files(src):
            official, crc = identify(path, by_crc, by_slug)
            stem = os.path.splitext(os.path.basename(path))[0]
            label = stem if is_clean(stem) or not official else clean_title(official)
            matched += bool(official)
            officials.append(official)
            items.append({
                "path": path,
                "label": label,
                "core_path": core_path,
                "core_name": core_display_name(core),
                "crc32": f"{crc}|crc",
                "db_name": system + ".lpl",
            })
        if not items:
            continue
        # several versions of one game (regions, revisions, hacks) would share a title:
        # all but a file already named that way show their file name instead
        uses = collections.Counter(i["label"] for i in items)
        meta = {}
        for item, official in zip(items, officials):
            info = metadata.get(item["crc32"].split("|")[0]) or metadata.get(official) or {}
            if info:
                meta[os.path.basename(item["path"])] = info
            stem = os.path.splitext(os.path.basename(item["path"]))[0]
            if uses[item["label"]] > 1 and stem != item["label"]:
                item["label"] = stem
            if official:
                jobs.append((system, official, item["label"]))
        playlist = {
            "version": "1.5",
            "default_core_path": core_path,
            "default_core_name": core_display_name(core),
            "label_display_mode": 0,
            "right_thumbnail_mode": 0,
            "left_thumbnail_mode": 0,
            "thumbnail_match_mode": 0,
            "sort_mode": 0,
            "items": sorted(items, key=lambda i: i["label"].lower()),
        }
        os.makedirs(PLAYLISTS, exist_ok=True)
        with open(os.path.join(PLAYLISTS, system + ".lpl"), "w", encoding="utf-8") as f:
            json.dump(playlist, f, indent=2, ensure_ascii=False)
        with open(os.path.join(PLAYLISTS, system + ".meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=1, ensure_ascii=False)
        print(f"{system}: {len(items)} games, {matched} identified, {len(meta)} with metadata")

    sync_playlists.sync()

    if jobs and not args.no_thumbnails:
        with ThreadPoolExecutor(16) as pool:
            found = list(pool.map(download_thumbs, jobs))
        print(f"thumbnails: {sum(1 for n in found if n)}/{len(jobs)} identified games have at least one image")


if __name__ == "__main__":
    main()
