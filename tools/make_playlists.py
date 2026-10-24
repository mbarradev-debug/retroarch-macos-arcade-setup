#!/usr/bin/env python3
"""Build one RetroArch playlist per console system and fetch its thumbnails.

Expects one sub-folder per system inside the ROM folder, named as in cores.tsv
(snes, gba, psx, ...). Games are identified by CRC (inside zips, or of the raw
file for cartridge-sized files) against libretro-database DATs, falling back to
the file name, so playlists get official libretro names and thumbnails match.
Arcade is handled separately by make_arcade_playlist.py.
Usage: make_playlists.py [--roms DIR] [--no-thumbnails]
"""
import argparse
import json
import os
import re
import urllib.parse
import urllib.request
import zipfile
import zlib
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
RA = os.path.expanduser("~/Library/Application Support/RetroArch")
PLAYLISTS = os.path.expanduser("~/Documents/RetroArch/playlists")
CACHE = os.path.expanduser("~/Library/Caches/retroarch-macos-arcade-setup/dats")
DB_URL = "https://raw.githubusercontent.com/libretro/libretro-database/master/"
THUMB_TYPES = ("Named_Boxarts", "Named_Snaps", "Named_Titles")
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


def fetch_dat(rel):
    path = os.path.join(CACHE, os.path.basename(rel))
    if not os.path.exists(path):
        os.makedirs(CACHE, exist_ok=True)
        urllib.request.urlretrieve(DB_URL + urllib.parse.quote(rel), path)
    return path


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def load_dat(path):
    """CRC -> game name, and normalized name -> game name."""
    by_crc, by_slug = {}, {}
    for block in open(path, encoding="utf-8", errors="ignore").read().split("\ngame (")[1:]:
        name = re.search(r'^\s*name "([^"]+)"', block, re.M)
        if not name:
            continue
        by_slug.setdefault(slug(name.group(1)), name.group(1))
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
    return by_slug.get(slug(os.path.splitext(os.path.basename(path))[0])), crcs[0] if crcs else "00000000"


def thumb_name(label):
    return re.sub(r'[&*/:`<>?\\|"]', "_", label) + ".png"


def download_thumbs(job):
    system, label = job
    got = 0
    for kind in THUMB_TYPES:
        dest = os.path.join(RA, "thumbnails", system, kind, thumb_name(label))
        if os.path.exists(dest):
            got += 1
            continue
        url = "https://thumbnails.libretro.com/" + "/".join(urllib.parse.quote(p) for p in (system, kind, thumb_name(label)))
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
        core_path = os.path.join(RA, "cores", f"{core}_libretro.dylib")
        items, matched = [], 0
        for path in game_files(src):
            label, crc = identify(path, by_crc, by_slug)
            matched += bool(label)
            if label:
                jobs.append((system, label))
            items.append({
                "path": path,
                "label": label or os.path.splitext(os.path.basename(path))[0],
                "core_path": core_path,
                "core_name": core_display_name(core),
                "crc32": f"{crc}|crc",
                "db_name": system + ".lpl",
            })
        if not items:
            continue
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
        print(f"{system}: {len(items)} games, {matched} identified")

    if jobs and not args.no_thumbnails:
        with ThreadPoolExecutor(16) as pool:
            found = list(pool.map(download_thumbs, jobs))
        print(f"thumbnails: {sum(1 for n in found if n)}/{len(jobs)} identified games have at least one image")


if __name__ == "__main__":
    main()
