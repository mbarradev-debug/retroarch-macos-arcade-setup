#!/usr/bin/env python3
"""Check the RetroArch system folder against the firmware the installed cores expect.

Reads firmwareN_path/firmwareN_opt from each installed core's .info file, looks
up the expected MD5 in libretro-database's System.dat (downloaded on first run)
and reports which files are missing or do not match. It never downloads BIOS.
Usage: check_bios.py [--system DIR] [--all]
"""
import argparse
import hashlib
import os
import re
import sys
import urllib.request
from collections import defaultdict

RA = os.path.expanduser("~/Library/Application Support/RetroArch")
CACHE = os.path.expanduser("~/Library/Caches/retroarch-macos-arcade-setup")
SYSTEM_DAT_URL = "https://raw.githubusercontent.com/libretro/libretro-database/master/dat/System.dat"


def system_dat():
    path = os.path.join(CACHE, "System.dat")
    if not os.path.exists(path):
        os.makedirs(CACHE, exist_ok=True)
        urllib.request.urlretrieve(SYSTEM_DAT_URL, path)
    return path


def load_md5s(path):
    """File name (lower case, no folder) -> set of valid MD5 hashes."""
    md5s = defaultdict(set)
    text = open(path, encoding="utf-8", errors="ignore").read()
    for m in re.finditer(r'rom \( name "?([^"]+?)"? size \d+ crc \w+ md5 (\w+)', text):
        md5s[os.path.basename(m.group(1)).lower()].add(m.group(2).lower())
    return md5s


def core_firmware():
    """(relative path, optional) -> cores that use it."""
    needed = defaultdict(list)
    for core in sorted(os.listdir(os.path.join(RA, "cores"))):
        if not core.endswith("_libretro.dylib"):
            continue
        name = core[: -len(".dylib")]
        info = os.path.join(RA, "info", name + ".info")
        if not os.path.exists(info):
            continue
        fields = dict(re.findall(r'^(\w+)\s*=\s*"?(.*?)"?\s*$', open(info, encoding="utf-8", errors="ignore").read(), re.M))
        for i in range(int(fields.get("firmware_count", 0) or 0)):
            path = fields.get(f"firmware{i}_path")
            if path:
                optional = fields.get(f"firmware{i}_opt", "false").lower() == "true"
                needed[(path, optional)].append(name.replace("_libretro", ""))
    return needed


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--system", default=os.path.expanduser("~/Documents/RetroArch/system"))
    parser.add_argument("--all", action="store_true", help="also list optional files")
    args = parser.parse_args()

    known = load_md5s(system_dat())
    problems = 0
    print("status\trequired\tfile\tcores\texpected_md5")
    for (path, optional), cores in sorted(core_firmware().items(), key=lambda x: (x[0][1], x[0][0].lower())):
        full = os.path.join(args.system, path)
        expected = known.get(os.path.basename(path).lower(), set())
        if not os.path.exists(full):
            status = "MISSING"
        elif not expected or os.path.isdir(full):
            status = "OK (no reference MD5)"
        else:
            status = "OK" if md5(full) in expected else "BAD MD5"
        if not status.startswith("OK"):
            problems += 1
        if args.all or not optional:
            print(f"{status}\t{'optional' if optional else 'REQUIRED'}\t{path}\t{', '.join(cores)}\t{'/'.join(sorted(expected)) or '-'}")
    print(f"\n{problems} file(s) missing or not matching (run with --all to include optional files).", file=sys.stderr)


if __name__ == "__main__":
    main()
