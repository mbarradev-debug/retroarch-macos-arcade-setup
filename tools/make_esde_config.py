#!/usr/bin/env python3
"""Point ES-DE (EmulationStation Desktop Edition) at this RetroArch setup.

Writes ~/ES-DE/custom_systems/es_systems.xml with one entry per system in
cores.tsv. Each entry replaces ES-DE's bundled system of the same name: it keeps
ES-DE's full name, file extensions, scraper platform and theme, but reads games
from this setup's folder (snes, lynx, pce...) and launches them with the cores
from cores.tsv, default first and alternates after it. Games start through the
"RetroArch CRT" launcher when it exists, so the 1:1 display mode still applies,
and through RetroArch itself otherwise.

Also sets in ~/ES-DE/settings/es_settings.xml: the ROM folder, the Slate theme
bundled with ES-DE (text list with videos, dark colours), skipping dot files
(the ._ files macOS writes on exFAT drives), and hiding games marked as hidden (make_esde_gamelists.py hides arcade zips that no installed core runs, as
the RetroArch MAME playlist does). Other settings are left alone.
Quit ES-DE first: it rewrites its settings when it exits.
Usage: make_esde_config.py [--roms DIR] [--update]
"""
import argparse
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, quoteattr

HERE = os.path.dirname(os.path.abspath(__file__))
ESDE = os.path.expanduser("~/ES-DE")
BUNDLED = "/Applications/ES-DE.app/Contents/Resources/resources/systems/macos/es_systems.xml"
RA = os.path.expanduser("~/Library/Application Support/RetroArch")
LAUNCHER = "~/Applications/RetroArch CRT.app/Contents/MacOS/RetroArch CRT"
RETROARCH = "/Applications/RetroArch.app/Contents/MacOS/RetroArch"
THEME = "slate-es-de"
# git URL of a theme that is not bundled with ES-DE; it is cloned into
# ~/ES-DE/themes and pulled again with --update. None for a bundled theme.
THEME_URL = None
# managed settings: (type, name, value)
SETTINGS = [
    ("bool", "ShowHiddenGames", "false"),
    # skip dot files, such as the ._game.zip companions macOS writes on exFAT drives
    ("bool", "ShowHiddenFiles", "false"),
    ("string", "Theme", THEME),
    ("string", "ThemeVariant", "withVideos"),  # text list with videos
    ("string", "ThemeColorScheme", "dark"),
]


def load_systems():
    systems = []
    with open(os.path.join(HERE, "..", "cores.tsv"), encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            folder, _playlist, _dat, core, alternates, esde = (line.rstrip("\n").split("\t") + [""] * 6)[:6]
            cores = [core] + [c for c in alternates.split(",") if c and c != core]
            systems.append((folder, esde or folder, cores))
    return systems


def core_display_name(core):
    info = os.path.join(RA, "info", f"{core}_libretro.info")
    if os.path.exists(info):
        m = re.search(r'^corename\s*=\s*"(.*)"', open(info, encoding="utf-8").read(), re.M)
        if m:
            return m.group(1)
    return core


def core_labels(system):
    """core -> label ES-DE uses for it in a bundled system."""
    labels = {}
    for command in system.findall("command"):
        m = re.search(r"%CORE_RETROARCH%/(\S+)_libretro\.dylib", command.text or "")
        if m and command.get("label"):
            labels.setdefault(m.group(1), command.get("label"))
    return labels


def system_xml(bundled, folder, cores):
    labels = core_labels(bundled)
    lines = ["    <system>"]
    for tag in ("name", "fullname", "systemsortname"):
        if bundled.findtext(tag):
            lines.append(f"        <{tag}>{escape(bundled.findtext(tag))}</{tag}>")
    lines.append(f"        <path>%ROMPATH%/{escape(folder)}</path>")
    lines.append(f"        <extension>{escape(' '.join(bundled.findtext('extension').split()))}</extension>")
    used = set()
    for core in cores:
        label = labels.get(core) or core_display_name(core)
        while label in used:
            label += f" ({core})"
        used.add(label)
        command = f"%EMULATOR_RETROARCH-CRT% -L %CORE_RETROARCH%/{core}_libretro.dylib %ROM%"
        lines.append(f"        <command label={quoteattr(label)}>{escape(command)}</command>")
    for tag in ("platform", "theme"):
        if bundled.findtext(tag):
            lines.append(f"        <{tag}>{escape(bundled.findtext(tag))}</{tag}>")
    lines.append("    </system>")
    return "\n".join(lines)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"wrote {path}")


def set_settings(path, settings):
    """es_settings.xml is a flat list of <type name="..." value="..." /> lines."""
    text = open(path, encoding="utf-8").read() if os.path.exists(path) else '<?xml version="1.0"?>\n'
    for kind, name, value in settings:
        line = f"<{kind} name={quoteattr(name)} value={quoteattr(value)} />"
        pattern = rf'<\w+ name="{re.escape(name)}" value="[^"]*" />'
        if re.search(pattern, text):
            text = re.sub(pattern, lambda _: line, text)
        else:
            text = text.rstrip("\n") + "\n" + line + "\n"
    write(path, text)


def install_theme(update):
    if not THEME_URL:
        return
    path = os.path.join(ESDE, "themes", THEME)
    if not os.path.isdir(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        print(f"downloading the {THEME} theme")
        subprocess.run(["git", "clone", "--quiet", THEME_URL, path], check=True)
    elif update:
        print(f"updating the {THEME} theme")
        subprocess.run(["git", "-C", path, "pull", "--quiet", "--ff-only"], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--roms", default=os.path.expanduser("~/Games/roms"), help="folder with one sub-folder per system")
    parser.add_argument("--update", action="store_true", help="pull the latest version of the theme")
    args = parser.parse_args()
    if not os.path.exists(BUNDLED):
        parser.error(f"ES-DE is not installed ({BUNDLED} not found)")

    bundled = {s.findtext("name"): s for s in ET.parse(BUNDLED).getroot().findall("system")}
    entries = []
    for folder, esde, cores in load_systems():
        if esde not in bundled:
            print(f"warning: ES-DE has no system named {esde!r}; skipping {folder}")
            continue
        entries.append(system_xml(bundled[esde], folder, cores))
    write(os.path.join(ESDE, "custom_systems", "es_systems.xml"),
          '<?xml version="1.0"?>\n'
          "<!-- Written by retroarch-macos-arcade-setup (tools/make_esde_config.py); edits are overwritten. -->\n"
          "<systemList>\n" + "\n".join(entries) + "\n</systemList>\n")
    write(os.path.join(ESDE, "custom_systems", "es_find_rules.xml"),
          '<?xml version="1.0"?>\n'
          "<!-- Written by retroarch-macos-arcade-setup (tools/make_esde_config.py); edits are overwritten. -->\n"
          "<ruleList>\n"
          '    <emulator name="RETROARCH-CRT">\n'
          "        <!-- RetroArch through the 1:1 display-mode launcher, or RetroArch itself -->\n"
          '        <rule type="staticpath">\n'
          f"            <entry>{escape(LAUNCHER)}</entry>\n"
          f"            <entry>{escape(RETROARCH)}</entry>\n"
          "        </rule>\n"
          "    </emulator>\n"
          "</ruleList>\n")
    install_theme(args.update)
    roms = os.path.abspath(os.path.expanduser(args.roms))
    set_settings(os.path.join(ESDE, "settings", "es_settings.xml"), [("string", "ROMDirectory", roms)] + SETTINGS)
    print(f"{len(entries)} systems, ROM folder {roms}")


if __name__ == "__main__":
    main()
