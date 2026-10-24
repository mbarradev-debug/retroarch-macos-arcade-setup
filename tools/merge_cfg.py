#!/usr/bin/env python3
"""Merge key = "value" lines from one RetroArch .cfg/.opt file into another.

Keys present in the source replace the same keys in the target; every other
line of the target is kept. The target is created if it does not exist.
Usage: merge_cfg.py <source> <target>
"""
import os
import re
import sys

LINE = re.compile(r'^\s*([A-Za-z0-9_\-]+)\s*=\s*"(.*)"\s*$')


def read_values(path):
    values = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = LINE.match(line)
            if m:
                values[m.group(1)] = m.group(2)
    return values


def merge(source, target):
    values = read_values(source)
    lines = []
    if os.path.exists(target):
        with open(target, encoding="utf-8") as f:
            lines = f.read().splitlines()
    seen = set()
    for i, line in enumerate(lines):
        m = LINE.match(line)
        if m and m.group(1) in values:
            lines[i] = f'{m.group(1)} = "{values[m.group(1)]}"'
            seen.add(m.group(1))
    lines += [f'{k} = "{v}"' for k, v in values.items() if k not in seen]
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return len(values)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    print(f"merged {merge(sys.argv[1], sys.argv[2])} keys into {sys.argv[2]}")
