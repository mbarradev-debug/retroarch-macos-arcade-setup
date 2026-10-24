# Troubleshooting and FAQ

Fixes for the problems you are most likely to hit with this setup, in the order you should check them, plus how to read RetroArch's log when nothing else explains it.

[[toc]]

## A game or the menu is slow

### The video driver rule

The rule for this setup is: **use Metal whenever it works, and make exceptions per core.** Metal is Apple's native graphics API, and RetroArch's Metal driver has the lowest overhead on a Mac when it runs properly.

Right now it does not. On **RetroArch 1.22.x with macOS 26**, the Metal driver stalls about eight to nine seconds after RetroArch starts, in the menu and in games alike. CPU use drops to zero and nothing is logged. It also gives hardware-rendered cores (PPSSPP, Flycast, Mupen64Plus-Next, Beetle PSX HW, Dolphin, LRPS2) no 3D context, so they fall back to slow software rendering or show a black screen. For that reason `config/retroarch.cfg` sets **Vulkan** (through MoltenVK) as the global driver, with `driver_switch_enable = "true"` so cores that only support OpenGL switch to `glcore` automatically.

This shows which driver is set. It should print `video_driver = "vulkan"`.

```bash
grep '^video_driver ' ~/Library/Application\ Support/RetroArch/config/retroarch.cfg
```

> [!WARNING]
> If the menu freezes after a few seconds, the driver was switched to `metal` (for example from **Settings → Drivers → Video**). Quit RetroArch, set `video_driver = "vulkan"` in the file above, or run `./install.sh` again, which re-applies it.

### Making an exception for one core

A per-core override changes the driver for one core only, leaving the global setting alone. Overrides live in `~/Library/Application Support/RetroArch/config/<Core>/<Core>.cfg`, where `<Core>` is the core's internal name (the folder RetroArch creates the first time you run the core, for example `Snes9x`, `MAME 2010` or `dolphin-emu`).

This makes Snes9x use Metal while everything else stays on Vulkan. It adds the line to the core's override file, creating it if needed.

```bash
mkdir -p ~/Library/Application\ Support/RetroArch/config/Snes9x
echo 'video_driver = "metal"' >> ~/Library/Application\ Support/RetroArch/config/Snes9x/Snes9x.cfg
```

To keep an exception in the repository, add the same line to `config/overrides/<Core>/<Core>.cfg` and run `./install.sh`. Remove the line to undo it.

### Testing whether Metal works again

When a new RetroArch version comes out, you can test Metal without touching your configuration. This creates a temporary settings file that switches to Metal and tells RetroArch not to save on exit.

```bash
printf 'video_driver = "metal"\nconfig_save_on_exit = "false"\n' > ~/metal-test.cfg
```

This starts RetroArch with that file layered on top of your configuration. Leave it on the menu for 30 seconds: if the animation keeps moving, Metal works on your version.

```bash
/Applications/RetroArch.app/Contents/MacOS/RetroArch --appendconfig ~/metal-test.cfg
```

This deletes the test file afterwards.

```bash
rm ~/metal-test.cfg
```

If Metal works, change `video_driver` in `config/retroarch.cfg` to `"metal"` and add `video_driver = "vulkan"` overrides for the 3D cores listed above.

### Other causes of slowness

1. **The Intel build under Rosetta.** This must include `arm64`; if it does not, run `./install.sh --replace-intel`.

   ```bash
   lipo -archs /Applications/RetroArch.app/Contents/MacOS/RetroArch
   ```

2. **Low Power Mode.** It limits the CPU and GPU. Turn it off in **System Settings → Battery**, or check it with this command (`lowpowermode 1` means on):

   ```bash
   pmset -g | grep lowpowermode
   ```

3. **Run-ahead on a heavy core.** This setup enables one frame of run-ahead for 2D cores in `config/overrides/`, which runs the core twice per frame. If a 2D game stutters, turn it off for that game in **Quick Menu → Latency → Run-Ahead**.
4. **Internal resolution on 3D systems.** PPSSPP, Flycast, Mupen64Plus-Next, melonDS DS and Dolphin render at about 3x, and LRPS2 at 2x (from the `.opt` files in `config/overrides/`). If a demanding game slows down, lower it in **Quick Menu → Core Options**.
5. **A heavy shader.** The default `crt-easymode` and LCD presets are light. If you switched to `crt-royale` or Mega Bezel, try **Quick Menu → Shaders → Video Shaders: Off** to see if it helps.

## A game says BIOS or files are missing

Most disc systems need BIOS files from your own console in `~/Documents/RetroArch/system`.

This lists the required files that are missing or have the wrong checksum.

```bash
python3 tools/check_bios.py
```

Check the file name and letter case exactly as in the [BIOS guide](04-bios.pdf). A PS2 BIOS goes in the `pcsx2/bios/` sub-folder, and Dreamcast's in `dc/`. For an arcade game, a missing file usually means the romset does not match the core; see the next section.

## A MAME game does not start

1. Check that the zip is **not unzipped or renamed**: `sf2.zip`, not `Street Fighter II.zip`.
2. Check that the **parent and BIOS zips** are in the same folder (for example `neogeo.zip` for Neo Geo games).
3. Run the report to see which core can run your set.

   ```bash
   python3 tools/make_arcade_playlist.py --report
   ```

4. Try the other core: in the game's playlist entry choose **Set Core Association** and switch between MAME 2003-Plus and MAME 2010.
5. Read the core's messages in the log (see the last section) for `NOT FOUND` or `WRONG CHECKSUM` lines.

The [MAME and arcade guide](03-mame-arcade.pdf) explains romsets and how to rebuild one.

## Box art does not appear

1. **Is the Mac online?** Images are downloaded on demand from `thumbnails.libretro.com` when you highlight a game (`network_on_demand_thumbnails = "true"`).
2. **Is the playlist name official?** Box art is looked up by playlist name and game label. Playlists made by `tools/make_playlists.py` use the official libretro names. A playlist you created by hand with another name finds no images.
3. **Is the label official?** A game labelled `smw` finds nothing; *Super Mario World (USA)* does. Rebuild the playlist with the tool, which identifies games by CRC.
4. **Download them all at once** with **Main Menu → Online Updater → Playlist Thumbnails Updater**.
5. **Some games have no artwork** on the server. Nothing can be done for those, other than adding your own PNG to `~/Library/Application Support/RetroArch/thumbnails/<playlist name>/Named_Boxarts/` with the label as the file name.

## The controls do not respond

1. **Click the RetroArch window.** If it opened behind another window, *Pause when focus is lost* (`pause_nonactive`) keeps the game paused until RetroArch is in front.
2. **Check that macOS sees the controller.** Bluetooth controllers must be paired in **System Settings → Bluetooth**. For wired ones, try another cable: many charge-only cables carry no data.
3. **Try the other joypad driver.** This setup uses `hid`. Many Bluetooth controllers (Xbox, PlayStation, 8BitDo in X-input or Switch mode) work better with `mfi`, Apple's Game Controller framework. Change it in **Settings → Drivers → Joypad**, then restart RetroArch.
4. **Update the controller profiles** with **Main Menu → Online Updater → Update Controller Profiles**. RetroArch recognises most controllers automatically from these profiles.
5. **Map the buttons yourself** in **Settings → Input → RetroPad Binds → Port 1 Controls → Set All Controls**, then save with **Save Controller Profile**.
6. **Check for a remap.** A remap for one core or game (**Quick Menu → Controls → Manage Remap Files**) can move buttons around. Delete it there if the layout is wrong for one game only.

> [!TIP]
> On the keyboard, the default keys are the arrows to move, **X** and **Z** for A and B, **S** and **A** for X and Y, **Enter** for Start, **Right Shift** for Select and **F1** for the Quick Menu. To open the menu from a controller, set **Settings → Input → Hotkeys → Menu Toggle (Controller Combo)**, for example to *L3 + R3* or *Start + Select*.

## How to see RetroArch's log

The log shows which core loaded, which files it opened, and why it failed.

### From the Terminal (most detail)

This starts RetroArch with verbose logging and shows the log in the Terminal while you play.

```bash
/Applications/RetroArch.app/Contents/MacOS/RetroArch --verbose
```

This also saves the log to a file, which is handy for sharing it.

```bash
/Applications/RetroArch.app/Contents/MacOS/RetroArch --verbose --log-file ~/Desktop/retroarch.log
```

This filters an existing log for errors and warnings.

```bash
grep -E '\[(ERROR|WARN)\]' ~/Desktop/retroarch.log
```

### From RetroArch

1. Go to **Settings → Logging** and turn on **Logging Verbosity** and **Log to File**.
2. Restart RetroArch and reproduce the problem.
3. The log files are saved in `~/Documents/RetroArch/logs/` (the `log_dir` of this setup), one file per session when **Timestamp Log Files** is on.

> [!NOTE]
> Turn **Log to File** off again when you are done. This setup leaves it off by default (`log_to_file = "false"`), because writing a log every session is rarely needed. Before sharing a log, look for your user name in it: logs contain full paths such as your home folder.

## Quick FAQ

**Can I use OpenEmu's BIOS folder?** Yes. Copy the files into `~/Documents/RetroArch/system`, rename them to the names in the BIOS guide if needed, and run `python3 tools/check_bios.py`.

**Can I update the cores?** Yes. This re-downloads every core, info file, shader and emulator data pack, after backing up your configuration.

```bash
./install.sh --update
```

**My settings were changed after running the installer.** Every run backs up first. Your previous configuration is in the newest `~/RetroArch-backup-<date>` folder; copy the files you need from `config/` back into `~/Library/Application Support/RetroArch/config/` while RetroArch is closed.

**Why are there no bezels?** This setup uses shaders only. The slang pack it installs includes bezel presets (Mega Bezel and others) in `~/Library/Application Support/RetroArch/shaders/shaders_slang/bezel/`; point a preset in `config/shaders/presets/` at one of them to try it. Mega Bezel is heavy, so test the game speed afterwards.
