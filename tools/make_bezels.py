#!/usr/bin/env python3
"""Frame each console game with artwork of its system (a "bezel").

The artwork is The Bezel Project's system image (logo, controller, console) for
NES, SNES, Game Boy, Game Boy Color, Game Boy Advance, Master System, Game Gear
and Mega Drive. Each image is downloaded from a pinned commit into
~/Library/Application Support/RetroArch/overlays/bezels; none of it ships with
this repository.

The images are 1920x1080 with a transparent hole for the game. For every system
this picks the largest whole-number scale at which the game fits inside that
hole, then places the image so the hole sits around the game: the image is
scaled to the screen width, or a little more (cropping at most CROP of each
side) when that lets the game be one step larger. The game keeps whole display
rows per line, as integer scaling gives it, but is drawn smaller than without a
bezel (SNES 6x instead of 7x, GBA 9x instead of 10x).

RetroArch reads this from content folder overrides,
config/<Core>/<folder>.cfg, for every core cores.tsv lists for the system, so
Gambatte shows the Game Boy art for games in gb and the Game Boy Color art for
games in gbc. The keys are merged into those files; other keys are kept.
--remove takes them out again.

The layout is computed for SCREEN, the picture RetroArch draws full screen
through the RetroArch CRT launcher on a 13" MacBook Air: 2560x1664 minus the
band beside the camera notch. Pass --screen for a different display.
Usage: make_bezels.py [--screen WxH] [--update] [--remove]
"""
import argparse
import os
import subprocess
import sys

from merge_cfg import merge

HERE = os.path.dirname(os.path.abspath(__file__))
RA = os.path.expanduser("~/Library/Application Support/RetroArch")
BEZELS = os.path.join(RA, "overlays", "bezels")
SCREEN = (2560, 1606)
# how much of each side of the artwork may fall off screen, as a share of the
# screen width, to make room for a larger game
CROP = 0.02
RAW = "https://raw.githubusercontent.com/thebezelproject"

# folder: (repository, commit, image, transparent hole in the image as
# left, top, right, bottom, game height in lines, game aspect ratio).
# The holes were measured on these commits: the largest rectangle with no
# opaque pixel, so the rounded corners of the TV frames never cover the game.
TV = (283, 42, 1635, 1034)
SYSTEMS = {
    "nes": ("bezelprojectSA-NES", "0f470ac01ddbcddf993b0bb14e3a2e33b69e5ce1",
            "Nintendo-Entertainment-System.png", TV, 224, 4 / 3),
    "snes": ("bezelprojectSA-SNES", "94551c42cd44bc9a8d790acd41372e7bc5f5036b",
             "Super-Nintendo-Entertainment-System.png", TV, 224, 4 / 3),
    "gb": ("bezelprojectSA-GB", "6f602eec05514e002891a18b6894cf4cd2720cb8",
           "Nintendo-Game-Boy.png", (362, 0, 1556, 1079), 144, 10 / 9),
    "gbc": ("bezelprojectSA-GBC", "79cf39590ef10569573dd6059cefade6fc3a9c02",
            "Nintendo-Game-Boy-Color.png", (362, 0, 1556, 1079), 144, 10 / 9),
    "gba": ("bezelprojectSA-GBA", "a64378d36e56a09bfd6a88404bfb6552a5cbafb1",
            "Nintendo-Game-Boy-Advance.png", (168, 0, 1751, 1079), 160, 3 / 2),
    "mastersystem": ("bezelprojectSA-MasterSystem", "99b57decfb3a009cb3275f505deeb1869c237003",
                     "Sega-Master-System.png", TV, 192, 4 / 3),
    "gamegear": ("bezelprojectSA-GameGear", "3efb87233a2efc233f591523d1d1844d4604369f",
                 "Sega-Game-Gear.png", (288, 0, 1631, 1079), 144, 10 / 9),
    # no system-art pack for the Mega Drive; this is the standard one
    "genesis": ("bezelproject-MegaDrive", "16aad58f1f11eaea76ea7c2aab6d697a12c0e4a1",
                "Sega-Mega-Drive.png", TV, 224, 4 / 3),
}
IMAGE = (1920, 1080)
# keys written to every override; the viewport and overlay path are added per system
OVERRIDE = {
    "input_overlay_enable": "true",
    "input_overlay_opacity": "1.000000",
    "input_overlay_show_inputs": "0",
    "input_overlay_hide_in_menu": "true",
    "input_overlay_hide_when_gamepad_connected": "false",
    "input_overlay_auto_scale": "false",
    "input_overlay_scale_landscape": "1.000000",
    "input_overlay_aspect_adjust_landscape": "0.000000",
    "input_overlay_x_offset_landscape": "0.000000",
    "input_overlay_y_offset_landscape": "0.000000",
    "input_overlay_x_separation_landscape": "0.000000",
    "input_overlay_y_separation_landscape": "0.000000",
    # a custom viewport, centred (RetroArch adds half the free space to x and y)
    "video_scale_integer": "false",
    "aspect_ratio_index": "23",
    "custom_viewport_x": "0",
    "custom_viewport_y": "0",
    "video_viewport_bias_x": "0.500000",
    "video_viewport_bias_y": "0.500000",
}
KEYS = set(OVERRIDE) | {"input_overlay", "custom_viewport_width", "custom_viewport_height"}


def core_names(folder):
    """Library names (the override folder names) of the cores that run a system."""
    with open(os.path.join(HERE, "..", "cores.tsv"), encoding="utf-8") as f:
        for line in f:
            cols = line.rstrip("\n").split("\t")
            if line.startswith("#") or len(cols) < 4 or cols[0] != folder:
                continue
            cores = [cols[3]] + [c for c in (cols[4].split(",") if len(cols) > 4 else []) if c]
            names = []
            for core in cores:
                try:
                    with open(os.path.join(RA, "info", f"{core}_libretro.info"), encoding="utf-8") as info:
                        for entry in info:
                            key, _, value = entry.partition("=")
                            if key.strip() == "corename":
                                names.append(value.strip().strip('"'))
                                break
                except FileNotFoundError:
                    print(f"  {folder}: no core info for {core}, skipped", file=sys.stderr)
            return names
    return []


def layout(screen, hole, lines, aspect):
    """The game size and the artwork's rectangle on screen, for the largest scale that fits."""
    sw, sh = screen
    iw, ih = IMAGE
    left, top, right, bottom = hole
    hw, hh = right - left + 1, bottom - top + 1
    fit = min(sw / iw, sh / ih)
    best = None
    for n in range(1, 50):
        gh = n * lines
        gw = round(gh * aspect)
        scale = max(fit, gh / hh, gw / hw)
        if iw * scale > sw * (1 + 2 * CROP) or ih * scale > sh:
            break
        best = (gw, gh, scale)
    if best is None:
        raise SystemExit(f"Screen {sw}x{sh} is too small for a bezel")
    gw, gh, scale = best
    # the centre of the hole goes to the centre of the screen, where the game is
    x = sw / 2 - (left + hw / 2) * scale
    y = sh / 2 - (top + hh / 2) * scale
    return gw, gh, (x / sw, y / sh, iw * scale / sw, ih * scale / sh)


def download(repo, commit, image, dest, update):
    if os.path.exists(dest) and not update:
        return
    url = f"{RAW}/{repo}/{commit}/retroarch/overlay/{image}"
    subprocess.run(["curl", "-fsSL", "--retry", "3", "-o", dest + ".part", url], check=True)
    os.replace(dest + ".part", dest)


def remove(path):
    """Take this script's keys out of an override; delete it if nothing is left."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        lines = [l for l in f.read().splitlines() if l.split("=")[0].strip() not in KEYS]
    if any(l.strip() for l in lines):
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    else:
        os.remove(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--screen", default=f"{SCREEN[0]}x{SCREEN[1]}",
                        help="size of the picture RetroArch draws, in pixels (default %(default)s)")
    parser.add_argument("--update", action="store_true", help="download the artwork again")
    parser.add_argument("--remove", action="store_true", help="turn the bezels off again")
    args = parser.parse_args()
    screen = tuple(int(v) for v in args.screen.lower().split("x"))

    os.makedirs(BEZELS, exist_ok=True)
    for folder, (repo, commit, image, hole, lines, aspect) in SYSTEMS.items():
        cores = core_names(folder)
        overrides = [os.path.join(RA, "config", core, f"{folder}.cfg") for core in cores]
        if args.remove:
            for path in overrides:
                remove(path)
            continue

        png = os.path.join(BEZELS, f"{folder}.png")
        download(repo, commit, image, png, args.update)
        gw, gh, rect = layout(screen, hole, lines, aspect)
        cfg = os.path.join(BEZELS, f"{folder}.cfg")
        with open(cfg, "w", encoding="utf-8") as f:
            f.write(f"# {repo}/{image}, placed for a {screen[0]}x{screen[1]} screen by make_bezels.py\n"
                    "overlays = 1\n"
                    f"overlay0_overlay = {folder}.png\n"
                    "overlay0_full_screen = true\n"
                    f"overlay0_rect = \"{','.join(f'{v:.6f}' for v in rect)}\"\n"
                    "overlay0_descs = 0\n")

        values = dict(OVERRIDE, input_overlay=cfg,
                      custom_viewport_width=str(gw), custom_viewport_height=str(gh))
        source = os.path.join(BEZELS, ".override.cfg")
        with open(source, "w", encoding="utf-8") as f:
            f.writelines(f'{k} = "{v}"\n' for k, v in values.items())
        for path in overrides:
            merge(source, path)
        os.remove(source)
        print(f"  {folder}: {gw}x{gh} ({gh // lines}x) for {', '.join(cores) or 'no installed core'}")


if __name__ == "__main__":
    main()
