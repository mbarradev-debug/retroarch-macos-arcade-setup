#!/usr/bin/env python3
"""Show in RetroArch only the games whose files are present right now.

make_playlists.py and make_arcade_playlist.py write the complete playlists to
~/Documents/RetroArch/playlists-full. This copies each one into RetroArch's
playlist folder keeping only the entries whose file exists, and removes a
playlist that has none left. Games on an external drive (ROM folders linked to
it, see the ROMs guide) therefore appear while the drive is connected and
disappear, instead of failing with "file is missing", while it is not.

The playlist tools run this after writing, and the RetroArch CRT launcher runs it
every time it opens RetroArch. History, favourites and playlists that have no
complete copy are not touched. Changes made in RetroArch to a filtered playlist
(renamed entries, core associations) are replaced the next time it runs.
Usage: sync_playlists.py
"""
import json
import os

PLAYLISTS = os.path.expanduser("~/Documents/RetroArch/playlists")
FULL = os.path.expanduser("~/Documents/RetroArch/playlists-full")


def sync():
    """Returns {playlist: (games shown, games in the complete playlist)}."""
    counts = {}
    if not os.path.isdir(FULL):
        return counts
    os.makedirs(PLAYLISTS, exist_ok=True)
    for name in sorted(os.listdir(FULL)):
        if not name.endswith(".lpl") or name.startswith("."):
            continue
        with open(os.path.join(FULL, name), encoding="utf-8") as f:
            playlist = json.load(f)
        items = playlist.get("items", [])
        playlist["items"] = [it for it in items if os.path.exists(it.get("path", ""))]
        dest = os.path.join(PLAYLISTS, name)
        if playlist["items"]:
            tmp = dest + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(playlist, f, indent=2, ensure_ascii=False)
            os.replace(tmp, dest)
        elif os.path.exists(dest):
            os.remove(dest)
        counts[name[:-4]] = (len(playlist["items"]), len(items))
    return counts


def main():
    for name, (shown, total) in sync().items():
        print(f"{name}: {shown}/{total} games available")


if __name__ == "__main__":
    main()
