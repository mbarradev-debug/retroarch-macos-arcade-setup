// Launch RetroArch with the built-in display drawing 1:1 with its panel.
//
// Scaled modes such as "More Space" render at a larger size and macOS shrinks the
// result to fit the panel. That resampling causes moire on CRT scanlines and
// phosphor masks. While RetroArch runs, this launcher switches the main display to
// the HiDPI mode whose backing store equals the panel's native pixels (1280x832
// points = 2560x1664 pixels on a 13" MacBook Air). The change is made "for this
// app only", so macOS restores the previous mode as soon as the launcher exits,
// even if it crashes.
//
// Before RetroArch starts it also runs sync_playlists.py (bundled in Resources),
// so RetroArch's playlists list only the games present right now, for example
// while an external ROM drive is connected.
//
// Built into "~/Applications/RetroArch CRT.app" by install.sh.
// Usage: retroarch_crt [--dry-run] [RetroArch arguments...]

import AppKit
import CoreGraphics

let retroArch = URL(fileURLWithPath: "/Applications/RetroArch.app")
let display = CGMainDisplayID()
let nativeFlag: UInt32 = 0x0200_0000  // kDisplayModeNativeFlag

func log(_ message: String) {
    FileHandle.standardError.write(("retroarch_crt: " + message + "\n").data(using: .utf8)!)
}

/// The HiDPI mode that draws one backing pixel per panel pixel, if there is one.
func oneToOneMode() -> CGDisplayMode? {
    let options = [kCGDisplayShowDuplicateLowResolutionModes: kCFBooleanTrue] as CFDictionary
    guard let modes = CGDisplayCopyAllDisplayModes(display, options) as? [CGDisplayMode] else { return nil }
    let native = modes.first { $0.ioFlags & nativeFlag != 0 }
        ?? modes.filter { $0.width == $0.pixelWidth }.max { $0.pixelWidth < $1.pixelWidth }
    guard let native = native else { return nil }
    return modes
        .filter { $0.pixelWidth == native.pixelWidth && $0.pixelHeight == native.pixelHeight
            && $0.width * 2 == $0.pixelWidth && $0.isUsableForDesktopGUI() }
        .max { $0.refreshRate < $1.refreshRate }
}

func describe(_ mode: CGDisplayMode) -> String {
    "\(mode.width)x\(mode.height) points, \(mode.pixelWidth)x\(mode.pixelHeight) pixels"
}

let args = Array(CommandLine.arguments.dropFirst())
let dryRun = args.first == "--dry-run"
let passThrough = dryRun ? Array(args.dropFirst()) : args

if let current = CGDisplayCopyDisplayMode(display), let target = oneToOneMode() {
    log("current mode \(describe(current)); 1:1 mode \(describe(target))")
    if dryRun { exit(0) }
    if current.width != target.width || current.pixelWidth != target.pixelWidth {
        var config: CGDisplayConfigRef?
        if CGBeginDisplayConfiguration(&config) == .success,
           CGConfigureDisplayWithDisplayMode(config, display, target, nil) == .success,
           CGCompleteDisplayConfiguration(config, .forAppOnly) == .success {
            log("switched to \(describe(target)) until RetroArch quits")
        } else {
            CGCancelDisplayConfiguration(config)
            log("could not switch modes; launching RetroArch anyway")
        }
    }
} else {
    log("no 1:1 mode found for the main display; launching RetroArch unchanged")
    if dryRun { exit(0) }
}

// Hide playlist entries whose files are missing (an external drive that is not
// connected). Failing here never stops RetroArch from starting.
if let script = Bundle.main.url(forResource: "sync_playlists", withExtension: "py"),
   FileManager.default.isExecutableFile(atPath: "/usr/bin/python3") {
    let sync = Process()
    sync.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
    sync.arguments = [script.path]
    sync.standardOutput = FileHandle.nullDevice
    if (try? sync.run()) != nil {
        sync.waitUntilExit()
        if sync.terminationStatus != 0 { log("could not update the playlists") }
    }
}

// RetroArch's own process is a child of this one: when it quits, so does the
// launcher, and macOS puts the original display mode back.
let task = Process()
task.executableURL = retroArch.appendingPathComponent("Contents/MacOS/RetroArch")
task.arguments = passThrough
do {
    try task.run()
} catch {
    log("cannot start RetroArch: \(error)")
    exit(1)
}
signal(SIGTERM) { _ in exit(0) }

// Started as a plain child process, RetroArch can open behind the app that
// launched it (ES-DE), and with "pause when focus is lost" a game then waits on
// a black screen. Bring it to the front once its window is up.
DispatchQueue.global().async {
    for _ in 0..<40 {
        usleep(250_000)
        guard let app = NSRunningApplication(processIdentifier: task.processIdentifier),
              app.isFinishedLaunching else { continue }
        if app.isActive { return }
        app.activate(options: [.activateAllWindows])
    }
    log("RetroArch did not come to the front")
}
task.waitUntilExit()
exit(task.terminationStatus)
