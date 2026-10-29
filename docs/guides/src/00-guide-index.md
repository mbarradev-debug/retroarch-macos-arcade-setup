# Guide Index

Reading guides for **retroarch-macos-arcade-setup**, a RetroArch setup for Apple Silicon Macs with native cores, CRT shaders and a multi-core MAME playlist. Each guide is a single continuous page; start with the Quick Start.

<ul class="guide-list">
<li><a href="01-quick-start.pdf"><strong>1. Quick Start</strong></a><br>Requirements, cloning the repository, running <code>install.sh</code>, the first launch and how to check the install worked.</li>
<li><a href="02-roms.pdf"><strong>2. ROMs</strong></a><br>The folder for each system, the file formats each core accepts, zips, CD images (<code>.chd</code>, <code>.cue</code>/<code>.bin</code>, <code>.m3u</code>), playlists and automatic box art.</li>
<li><a href="03-mame-arcade.pdf"><strong>3. MAME and Arcade</strong></a><br>Which romset MAME 2003-Plus and MAME 2010 expect, why MAME zips stay untouched, merged/split/non-merged sets, CHDs, samples and diagnosing games that do not start.</li>
<li><a href="04-bios.pdf"><strong>4. BIOS Files</strong></a><br>The exact system folder, a table of every BIOS file with its MD5 and whether it is required, and how to verify them from RetroArch or the Terminal.</li>
<li><a href="05-backup-restore.pdf"><strong>5. Backup and Restore</strong></a><br>What the repository does not store, what can be downloaded again, <code>backup.sh</code> / <code>restore.sh</code>, and rebuilding everything on a freshly formatted Mac.</li>
<li><a href="06-troubleshooting.pdf"><strong>6. Troubleshooting and FAQ</strong></a><br>Slow games and the video driver rule, missing BIOS, MAME games that fail, missing box art, unresponsive controls and reading the log.</li>
<li><a href="07-es-de.pdf"><strong>7. ES-DE Frontend</strong></a><br>The game browser <code>install.sh</code> sets up, copying playlists and artwork into it, scraping videos with ScreenScraper, themes, controls and choosing a core per game.</li>
</ul>

## How these guides are made

The guides are written in Markdown in `docs/guides/src/` and turned into PDFs by `docs/build-guides.sh`, which renders each one in a headless Chrome and sets the page height to the height of the content. Edit the Markdown and run the script to regenerate them.

<p class="footer">Released under the MIT license as part of retroarch-macos-arcade-setup. No ROMs, BIOS files or other copyrighted material are included.</p>
