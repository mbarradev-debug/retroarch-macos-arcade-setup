# BIOS Files

Some systems need firmware dumped from your own console before their games will start. This guide shows the exact folder, every file the installed cores look for, and how to check them.

[[toc]]

## Where BIOS files go

All BIOS files go in the RetroArch **system folder**, which this setup sets to:

```text
~/Documents/RetroArch/system/
```

This opens the system folder in Finder.

```bash
open ~/Documents/RetroArch/system
```

Put files directly in that folder, with the exact names in the table below (names are case-sensitive). A few cores look in a sub-folder instead; the table shows those paths, such as `dc/dc_boot.bin` or `pcsx2/bios/`.

> [!IMPORTANT]
> This repository never includes or downloads BIOS files. They are copyrighted firmware. Dump them from consoles you own. The installer only downloads open-source emulator data into the same folder: Dolphin's `dolphin-emu/Sys`, PPSSPP's `PPSSPP` assets and the PS2 game database in `pcsx2/resources`. It also creates the empty `pcsx2/bios` folder for your PS2 BIOS.

The system folder is inside `~/Documents`. If iCloud Drive syncs your Documents folder, BIOS files are synced too; that is fine, because they are small and read once at start-up.

## Required and optional

- **Required:** the core will not start games of that system without the file.
- **Optional:** games run without it, using the core's built-in replacement (called HLE, high-level emulation). The real BIOS can improve compatibility, show the original boot screen, or is only needed for some games or add-ons.

Three entries listed as optional are needed in practice:

- **PlayStation (SwanStation, the default core):** needs at least one of the `scph55xx.bin` files, ideally the one matching your games' region (`scph5500` Japan, `scph5501` USA, `scph5502` Europe). Beetle PSX HW, the alternate core, needs all three.
- **Sega CD / Mega-CD:** CD games need `bios_CD_U.bin`, `bios_CD_E.bin` or `bios_CD_J.bin` for their region. Cartridge games do not.
- **PC Engine CD:** CD games need `syscard3.pce` (a few early ones run with `syscard1.pce` or `syscard2.pce`). HuCard games do not.

## BIOS files by system

Every file the installed cores declare, with the MD5 that libretro's `System.dat` expects. A file with the right name but a different MD5 may still work, but it is a different revision and can cause problems.

### PlayStation

| File | Needed? | MD5 |
|---|---|---|
| `ps1_rom.bin` | Optional | `81bbe60ba7a3d1cea1d48c14cbcc647b` |
| `psxonpsp660.bin` | Optional | `c53ca5908936d412331790f4426c6c33` |
| `scph5500.bin` | **Required** | `8dd7d5296a650fac7319bce665a6a53c` |
| `scph5501.bin` | **Required** | `490f666e1afb15b7362b406ed1cea246` |
| `scph5502.bin` | **Required** | `32736f17079d0b2b7024407c39bd3050` |

### PlayStation 2

| File | Needed? | MD5 |
|---|---|---|
| `pcsx2/bios/` (any PS2 BIOS dump) | **Required** | varies by console model |

### Saturn

| File | Needed? | MD5 |
|---|---|---|
| `mpr-17933.bin` | **Required** | `3240872c70984b6cbfda1586cab68dbe` |
| `mpr-18811-mx.ic1` | Optional | `255113ba943c92a54facd25a10fd780c` |
| `mpr-19367-mx.ic1` | Optional | `1cd19988d1d72a3e7caa0b73234c96b4` |
| `saturn_bios.bin` | Optional | `af5828fdff51384f99b3c4926be27762` |
| `sega_101.bin` | **Required** | `85ec9ca47d8f6807718151cbcca8b964` |

### Mega-CD / Sega CD

| File | Needed? | MD5 |
|---|---|---|
| `bios_CD_E.bin` | Optional | `e66fa1dc5820d254611fdcdba0662372` |
| `bios_CD_J.bin` | Optional | `278a9397d192149e84e820ac621a8edd` |
| `bios_CD_U.bin` | Optional | `2efd74e3232ff260e371b99f84024f7f` |

### Master System / Game Gear / Mega Drive

| File | Needed? | MD5 |
|---|---|---|
| `bios.gg` | Optional | `672e104c3be3a238301aceffc3b23fd6` |
| `bios_E.sms` | Optional | `840481177270d5642a14ca71ee72844c` |
| `bios_J.sms` | Optional | `24a519c53f67b00640d0048ef7089105` |
| `bios_MD.bin` | Optional | `d3293ebaaa7f4eb2a6766b68a0fb4609` |
| `bios_U.sms` | Optional | `840481177270d5642a14ca71ee72844c` |

### PC Engine CD

| File | Needed? | MD5 |
|---|---|---|
| `gexpress.pce` | Optional | `6d2cb14fc3e1f65ceb135633d1694122` |
| `syscard1.pce` | Optional | `2b7ccb3d86baa18f6402c176f3065082` |
| `syscard2.pce` | Optional | `3cdd6614a918616bfc41c862e889dd79` |
| `syscard3.pce` | Optional | `38179df8f4ac870017db21ebcbf53114` |

### PC-FX

| File | Needed? | MD5 |
|---|---|---|
| `pcfx.rom` | **Required** | `08e36edbea28a017f79f8d4f7ff9b6d7` |

### 3DO

| File | Needed? | MD5 |
|---|---|---|
| `3do_arcade_saot.bin` | Optional | `8970fc987ab89a7f64da9f8a8c4333ff` |
| `goldstar.bin` | Optional | `8639fd5e549bd6238cfee79e3e749114` |
| `panafz1-kanji.bin` | Optional | `b8dc97f778a6245c58e064b0312e8281` |
| `panafz1.bin` | Optional | `f47264dd47fe30f73ab3c010015c155b` |
| `panafz10-norsa.bin` | Optional | `1477bda80dc33731a65468c1f5bcbee9` |
| `panafz10.bin` | Optional | `51f2f43ae2f3508a14d9f56597e2d3ce` |
| `panafz10e-anvil-norsa.bin` | Optional | `cf11bbb5a16d7af9875cca9de9a15e09` |
| `panafz10e-anvil.bin` | Optional | `a48e6746bd7edec0f40cff078f0bb19f` |
| `panafz10ja-anvil-kanji.bin` | Optional | `428577250f43edc902ea239c50d2240d` |
| `panafz1j-kanji.bin` | Optional | `c23fb5d5e6bb1c240d02cf968972be37` |
| `panafz1j-norsa.bin` | Optional | `f6c71de7470d16abe4f71b1444883dc8` |
| `panafz1j.bin` | Optional | `a496cfdded3da562759be3561317b605` |
| `sanyotry.bin` | Optional | `35fa1a1ebaaeea286dc5cd15487c13ea` |

### Dreamcast

| File | Needed? | MD5 |
|---|---|---|
| `dc/dc_boot.bin` | Optional | `e10c53c2f8b90bab96ead2d368858623` |

### Nintendo DS

| File | Needed? | MD5 |
|---|---|---|
| `bios7.bin` | Optional | `df692a80a5b1bc90728bc3dfc76cd948` |
| `bios9.bin` | Optional | `a392174eb3e572fed6447e956bde4b25` |
| `dsi_bios7.bin` | Optional | `559dae4ea78eb9d67702c56c1d791e81` |
| `dsi_bios9.bin` | Optional | `87b665fce118f76251271c3732532777` |
| `dsi_firmware.bin` | Optional | `-` |
| `dsi_nand.bin` | Optional | `-` |
| `dsi_sd_card.bin` | Optional | `-` |
| `firmware.bin` | Optional | `e45033d9b0fa6b0de071292bba7c9d13` |

### Game Boy / Color / Advance

| File | Needed? | MD5 |
|---|---|---|
| `cgb_boot.bin` | Optional | `dbfce9db9deaa2567f6a84fde55f9680` |
| `dmg_boot.bin` | Optional | `32fbbd84168d3482956eb3c5051637f5` |
| `gb_bios.bin` | Optional | `32fbbd84168d3482956eb3c5051637f5` |
| `gba_bios.bin` | Optional | `a860e8c0b6d573d191e4ec7db1b1e4f6` |
| `gbc_bios.bin` | Optional | `dbfce9db9deaa2567f6a84fde55f9680` |
| `sgb_bios.bin` | Optional | `d574d4f9c12f305074798f54c091a8b4` |

### Famicom Disk System

| File | Needed? | MD5 |
|---|---|---|
| `disksys.rom` | Optional | `ca30b50f880eb660a320674ed365ef7a` |

### Super Nintendo (special chips)

| File | Needed? | MD5 |
|---|---|---|
| `BS-X.bin` | Optional | `fed4d8242cfbed61343d53d48432aced` |
| `cx4.data.rom` | Optional | `037ac4296b6b6a5c47c440188d3c72e3` |
| `dsp1.data.rom` | Optional | `3d81b45fa0c2aa8b852dfb1ece7c0971` |
| `dsp1.program.rom` | Optional | `ae209fbe789fbf11a48aea5ab1197321` |
| `dsp1b.data.rom` | Optional | `1e3f568634a7d8284020dddc0ae905bc` |
| `dsp1b.program.rom` | Optional | `d10f446888e097cbf500f3f663cf4f6d` |
| `dsp2.data.rom` | Optional | `e9417e29223b139c3c4b635a2a3b8744` |
| `dsp2.program.rom` | Optional | `aa6e5922a3ed5ded54f24247c11143c5` |
| `dsp3.data.rom` | Optional | `0a81210c0a940b997dd9843281008ee6` |
| `dsp3.program.rom` | Optional | `d99ca4562818d49cee1f242705bba6f8` |
| `dsp4.data.rom` | Optional | `ee4990879eb68e3cbca239c5bc20303d` |
| `dsp4.program.rom` | Optional | `a151023b948b90ffc23a5b594bb6fef2` |
| `SGB1.sfc` | Optional | `b15ddb15721c657d82c5bab6db982ee9` |
| `SGB2.sfc` | Optional | `8ecd73eb4edf7ed7e81aef1be80031d5` |
| `st010.data.rom` | Optional | `254d70762b6f59f99c27c395aba7d07d` |
| `st010.program.rom` | Optional | `1d70019179a59a566a0bb5d3f2845544` |
| `st011.data.rom` | Optional | `10bd3f4aa949737ab9836512c35bcc29` |
| `st011.program.rom` | Optional | `95222ebf1c0c2990bcf25db43743f032` |
| `st018.data.rom` | Optional | `49c898b60d0f15e90d0ba780dd12f366` |
| `st018.program.rom` | Optional | `dda40ccd57390c96e49d30a041f9a9e7` |
| `STBIOS.bin` | Optional | `d3a44ba7d42a74d3ac58cb9c14c6a5ca` |

### Nintendo 64 (64DD)

| File | Needed? | MD5 |
|---|---|---|
| `Mupen64plus/IPL.n64` | Optional | `8d3d9f294b6e174bc7b1d2fd1c727530` |

### Pokémon mini

| File | Needed? | MD5 |
|---|---|---|
| `bios.min` | Optional | `1e4fb124a3a886865acb574f388c803d` |

### Atari 5200 / 8-bit

| File | Needed? | MD5 |
|---|---|---|
| `5200.rom` | Optional | `281f20ea4320404ec820fb7ec0693b38` |
| `ATARIBAS.ROM` | Optional | `0bac0c6a50104045d902df4503a4c30b` |
| `ATARIOSA.ROM` | Optional | `eb1f32f5d9f382db1bbfb8d7f9cb343a` |
| `ATARIOSB.ROM` | Optional | `a3e8d617c95d08031fe1b20d541434b2` |
| `ATARIXL.ROM` | Optional | `06daac977823773a3eea3422fd26a703` |
| `BB01R4_OS.ROM` | Optional | `b7a2a04677d34f069eeb643d5238bf86` |
| `XEGAME.ROM` | Optional | `d7eb37aec6960cba36bc500e0e5d00bc` |

### Atari 7800

| File | Needed? | MD5 |
|---|---|---|
| `7800 BIOS (U).rom` | Optional | `0763f1ffb006ddbe32e52d497ee848ae` |

### Atari Lynx

| File | Needed? | MD5 |
|---|---|---|
| `lynxboot.img` | **Required** | `fcd403db69f54290b51035d82f835e7b` |

### ColecoVision

| File | Needed? | MD5 |
|---|---|---|
| `colecovision.rom` | **Required** | `2c66f5911e5b42b8ebe113403548eee7` |

### Intellivision

| File | Needed? | MD5 |
|---|---|---|
| `exec.bin` | **Required** | `62e761035cb657903761800f4437b8af` |
| `grom.bin` | **Required** | `0cd5946c6473e42e8e4c2137785e427f` |

### Odyssey² / Videopac

| File | Needed? | MD5 |
|---|---|---|
| `c52.bin` | **Required** | `f1071cdb0b6b10dde94d3bc8a6146387` |
| `g7400.bin` | **Required** | `c500ff71236068e0dc0d0603d265ae76` |
| `jopac.bin` | **Required** | `279008e4a0db2dc5f1c048853b033828` |
| `o2rom.bin` | **Required** | `562d5ebf9e030a40d6fabfc2f33139fd` |

### MSX

| File | Needed? | MD5 |
|---|---|---|
| `Machines/Shared Roms/MSX.rom` | **Required** | `364a1a579fe5cb8dba54519bcfcdac0d or aa95aea2563cd5ec0a0919b44cc17d47` |

### Commodore 64

| File | Needed? | MD5 |
|---|---|---|
| `vice/JiffyDOS_1541-II.bin` | Optional | `1b1e985ea5325a1f46eb7fd9681707bf` |
| `vice/JiffyDOS_1571_repl310654.bin` | Optional | `41c6cc528e9515ffd0ed9b180f8467c0` |
| `vice/JiffyDOS_1581.bin` | Optional | `20b6885c6dc2d42c38754a365b043d71` |
| `vice/JiffyDOS_C64.bin` | Optional | `be09394f0576cf81fa8bacf634daf9a2` |

**No BIOS needed:** NES, SNES (except the special-chip games above), Nintendo 64, GameCube (Dolphin uses its own HLE), PSP, Virtual Boy, Neo Geo Pocket, WonderSwan, Vectrex, Atari 2600, Atari Jaguar, Watara Supervision and SG-1000.

**Arcade BIOS** such as `neogeo.zip` are not part of the system folder. They go next to the games in `~/Games/roms/arcade`; see the [MAME and arcade guide](03-mame-arcade.pdf).

> [!NOTE]
> **MSX (blueMSX)** needs a `Machines` folder and a `Databases` folder in the system folder. They contain MSX system ROMs, so the installer deliberately does not download them. Copy the ones you own from a blueMSX installation.

## Check your BIOS files

### From the Terminal

`tools/check_bios.py` reads the firmware list from each installed core's info file and compares the MD5 of each file in your system folder with `System.dat`. It downloads `System.dat` once into `~/Library/Caches/retroarch-macos-arcade-setup`, and never downloads BIOS files.

This lists the **required** files that are missing or wrong. Run it from the repository folder.

```bash
python3 tools/check_bios.py
```

This includes the optional files too.

```bash
python3 tools/check_bios.py --all
```

If your system folder is somewhere else, point the check at it.

```bash
python3 tools/check_bios.py --system /path/to/system
```

The output is tab-separated, one line per file, followed by a count of the problems found:

```text
status   required  file              cores                       expected_md5
OK       REQUIRED  scph5501.bin      mednafen_psx_hw             490f666e1afb15b7362b406ed1cea246
BAD MD5  optional  bios_CD_U.bin     genesis_plus_gx, picodrive  2efd74e3232ff260e371b99f84024f7f
MISSING  REQUIRED  colecovision.rom  gearcoleco                  2c66f5911e5b42b8ebe113403548eee7
```

- **OK:** present with the expected MD5.
- **OK (no reference MD5):** present, but `System.dat` has no checksum for it (for example the `pcsx2/bios` folder).
- **BAD MD5:** present, but a different revision or a bad dump.
- **MISSING:** not found at that path. Check the name, the letter case and the sub-folder.

To check one file by hand, this prints its MD5 so you can compare it with the table.

```bash
md5 ~/Documents/RetroArch/system/scph5501.bin
```

### From RetroArch

RetroArch shows the firmware status for the core that is loaded.

1. Go to **Main Menu → Load Core** and pick the core, for example *Sony - PlayStation (SwanStation)*.
2. Go to **Main Menu → Information → Core Information**.
3. Scroll to **Firmware**. Each file is listed as **Present** or **Missing**, and as *Required* or *Optional*.

RetroArch only checks that the file exists. It does not check the MD5, so use `check_bios.py` to catch a wrong revision.

> [!TIP]
> If a disc game boots to a black screen or straight back to the menu, the BIOS is the first suspect. Run `python3 tools/check_bios.py` before anything else.
