#!/usr/bin/env python3
"""Build the MAME playlist from a MAME romset, picking a working core per game.

MAME romsets only work with the emulator version they were built for. This tool
compares the CRCs inside your zips with each core's official DAT and assigns
every game to the first core (in the order given) that has all of its required
ROMs (its own, its parent's or its BIOS's) and whose driver is not marked as
not working. Parent games are listed; clones only when no parent works.

  --report   only print how much of the romset each core can run, to help you
             choose cores (or decide to rebuild the set with clrmamepro/igir)
Usage: make_arcade_playlist.py [--roms DIR] [--cores mame2003_plus,mame2010] [--report]
"""
import argparse
import json
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from concurrent.futures import ThreadPoolExecutor

RA = os.path.expanduser("~/Library/Application Support/RetroArch")
PLAYLIST = os.path.expanduser("~/Documents/RetroArch/playlists/MAME.lpl")
CACHE = os.path.expanduser("~/Library/Caches/retroarch-macos-arcade-setup/dats")
SYSTEM = "MAME"
THUMB_TYPES = ("Named_Boxarts", "Named_Snaps", "Named_Titles")

# core -> official DAT (MAME version the romset must match)
DATS = {
    "mame2003_plus": "https://raw.githubusercontent.com/libretro/mame2003-plus-libretro/master/metadata/mame2003-plus.xml",  # 0.78+
    "mame2003": "https://raw.githubusercontent.com/libretro/mame2003-libretro/master/metadata/mame2003.xml",  # 0.78
    "mame2010": "https://raw.githubusercontent.com/libretro/mame2010-libretro/master/metadata/mame2010.xml",  # 0.139
    "fbneo": "https://raw.githubusercontent.com/libretro/FBNeo/master/dats/FinalBurn%20Neo%20(ClrMame%20Pro%20XML,%20Arcade%20only).dat",
}


def fetch_dat(core):
    path = os.path.join(CACHE, f"{core}.xml")
    if not os.path.exists(path):
        os.makedirs(CACHE, exist_ok=True)
        print(f"downloading {core} DAT...")
        urllib.request.urlretrieve(DATS[core], path)
    return path


def core_display_name(core):
    info = os.path.join(RA, "info", f"{core}_libretro.info")
    if os.path.exists(info):
        m = re.search(r'^display_name\s*=\s*"(.*)"', open(info, encoding="utf-8").read(), re.M)
        if m:
            return m.group(1)
    return core


def pack_crcs(folder):
    crcs = {}
    for fn in os.listdir(folder):
        if fn.lower().endswith(".zip"):
            try:
                with zipfile.ZipFile(os.path.join(folder, fn)) as z:
                    crcs[fn[:-4].lower()] = {f"{i.CRC:08x}" for i in z.infolist()}
            except zipfile.BadZipFile:
                print(f"warning: {fn} is not a valid zip")
    return crcs


def load_dat(path):
    """Return (games, has_biossets). MAME DATs tag alternate BIOS ROMs; FBNeo's do not."""
    games = {}
    has_biossets = False
    for _, el in ET.iterparse(path):
        if el.tag not in ("game", "machine"):
            continue
        # ROMs of alternate BIOS versions are only needed for the default BIOS
        default_bios = {b.get("name") for b in el.findall("biosset") if b.get("default") == "yes"}
        has_biossets = has_biossets or bool(default_bios)
        drv = el.find("driver")
        games[el.get("name")] = {
            "description": (el.findtext("description") or el.get("name")).strip(),
            "cloneof": el.get("cloneof"),
            "romof": el.get("romof"),
            "isbios": el.get("isbios") == "yes",
            "skip": el.get("isbios") == "yes" or el.get("isdevice") == "yes" or el.get("runnable") == "no",
            "disk": any(d.get("status") != "nodump" for d in el.findall("disk")),
            "working": (drv.get("status") if drv is not None else "good") in ("good", "imperfect"),
            "roms": {r.get("crc").lower() for r in el.findall("rom")
                     if r.get("crc") and r.get("status") != "nodump" and r.get("optional") != "yes"
                     and (r.get("bios") is None or r.get("bios") in default_bios)},
        }
        el.clear()
    return games, has_biossets


def available(name, games, crcs, seen=None):
    seen = seen if seen is not None else set()
    if not name or name in seen:
        return set()
    seen.add(name)
    g = games.get(name, {})
    return crcs.get(name, set()) | available(g.get("cloneof"), games, crcs, seen) | available(g.get("romof"), games, crcs, seen)


def bios_roms(name, games):
    """ROMs of the BIOS set a game depends on (DATs like FBNeo list them inline)."""
    g = games[name]
    while g.get("romof") and g["romof"] in games:
        g = games[g["romof"]]
        if g["isbios"]:
            return g["roms"]
    return set()


def playable(games, crcs, has_biossets):
    result = set()
    for n, g in games.items():
        if n not in crcs or g["skip"] or not g["roms"] or g["disk"] or not g["working"]:
            continue
        have = available(n, games, crcs)
        need = g["roms"]
        if not has_biossets:
            # the DAT lists every BIOS variant inline; any one of them is enough
            bios = bios_roms(n, games)
            if bios & have:
                need = need - bios
        if need <= have:
            result.add(n)
    return result


def thumb_name(label):
    return re.sub(r'[&*/:`<>?\\|"]', "_", label) + ".png"


def download(label):
    got = 0
    for kind in THUMB_TYPES:
        dest = os.path.join(RA, "thumbnails", SYSTEM, kind, thumb_name(label))
        if os.path.exists(dest):
            got += 1
            continue
        url = "https://thumbnails.libretro.com/" + "/".join(urllib.parse.quote(p) for p in (SYSTEM, kind, thumb_name(label)))
        try:
            data = urllib.request.urlopen(url, timeout=30).read()
        except Exception:
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
        got += 1
    return got


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--roms", default=os.path.expanduser("~/Games/roms/arcade"))
    parser.add_argument("--cores", default="mame2003_plus,mame2010", help=f"comma-separated, in order of preference: {', '.join(DATS)}")
    parser.add_argument("--report", action="store_true", help="only report coverage per core")
    parser.add_argument("--no-thumbnails", action="store_true")
    args = parser.parse_args()

    cores = [c.strip() for c in args.cores.split(",") if c.strip()]
    unknown = [c for c in cores if c not in DATS]
    if unknown:
        parser.error(f"unknown core(s): {', '.join(unknown)}")
    crcs = pack_crcs(os.path.expanduser(args.roms))
    loaded = [load_dat(fetch_dat(c)) for c in cores]
    dats = [games for games, _ in loaded]
    works = [playable(games, crcs, has_biossets) for games, has_biossets in loaded]

    if args.report:
        print(f"romset: {len(crcs)} zips")
        for core, games, ok in zip(cores, dats, works):
            known = sum(1 for n in crcs if n in games)
            parents = sum(1 for n in ok if not games[n]["cloneof"])
            print(f"{core:14} recognised {known:5}  playable {len(ok):5} ({100 * len(ok) / max(len(crcs), 1):.0f}%)  parents {parents}")
        print(f"{'combined':14} playable {len(set().union(*works)):5}")
        return

    chosen = {}  # zip name -> index of the first core that runs it
    for name in sorted(crcs):
        for i, ok in enumerate(works):
            if name in ok:
                chosen[name] = i
                break

    def parent(name):
        return dats[chosen[name]][name]["cloneof"]

    entries = [n for n in chosen if not parent(n) or parent(n) not in chosen]
    items = []
    for name in sorted(entries, key=lambda n: dats[chosen[n]][n]["description"].lower()):
        core = cores[chosen[name]]
        items.append({
            "path": os.path.join(os.path.expanduser(args.roms), name + ".zip"),
            "label": dats[chosen[name]][name]["description"],
            "core_path": os.path.join(RA, "cores", f"{core}_libretro.dylib"),
            "core_name": core_display_name(core),
            "crc32": "DETECT",
            "db_name": "MAME.lpl",
        })
    playlist = {
        "version": "1.5",
        "default_core_path": "",
        "default_core_name": "",
        "label_display_mode": 0,
        "right_thumbnail_mode": 0,
        "left_thumbnail_mode": 0,
        "thumbnail_match_mode": 0,
        "sort_mode": 0,
        "items": items,
    }
    os.makedirs(os.path.dirname(PLAYLIST), exist_ok=True)
    with open(PLAYLIST, "w", encoding="utf-8") as f:
        json.dump(playlist, f, indent=2, ensure_ascii=False)
    per_core = {c: sum(1 for it in items if it["core_path"].endswith(f"/{c}_libretro.dylib")) for c in cores}
    print(f"zips: {len(crcs)} | playable with some core: {len(chosen)} | in playlist: {len(items)} {per_core}")

    if not args.no_thumbnails:
        with ThreadPoolExecutor(16) as pool:
            found = list(pool.map(download, [it["label"] for it in items]))
        print(f"thumbnails: {sum(1 for n in found if n)}/{len(items)} games have at least one image")


if __name__ == "__main__":
    main()
