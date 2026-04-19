#!/usr/bin/env python3
"""
Android Device Scanner — Discover all connected ADB devices with full specs
Usage: python3 scanner.py [--json] [--watch]
"""
import subprocess, json, sys, time, argparse

def adb(cmd, serial=""):
    prefix = f"adb -s {serial}" if serial else "adb"
    r = subprocess.run(f"{prefix} shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_devices():
    r = subprocess.run("adb devices", shell=True, capture_output=True, text=True)
    lines = r.stdout.splitlines()[1:]  # Skip header
    return [l.split()[0] for l in lines if l.strip() and "\t" in l]

def scan_device(serial):
    return {
        "serial": serial,
        "model": adb("getprop ro.product.model", serial),
        "brand": adb("getprop ro.product.brand", serial),
        "android": adb("getprop ro.build.version.release", serial),
        "api": int(adb("getprop ro.build.version.sdk", serial) or "0"),
        "cpu_abi": adb("getprop ro.product.cpu.abi", serial),
        "rom": adb("getprop ro.build.fingerprint", serial),
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--watch", action="store_true", help="Watch for device changes")
    args = parser.parse_args()

    devices = get_devices()
    if not devices:
        print("No devices found.")
        sys.exit(1)

    print(f"Found {len(devices)} device(s)\n")

    scanned = [scan_device(d) for d in devices]

    if args.json:
        print(json.dumps(scanned, indent=2))
    else:
        print(f"{'Serial':<20} {'Model':<25} {'Android':<10} {'CPU'}")
        print("─" * 80)
        for d in scanned:
            print(f"{d['serial']:<20} {d['model']:<25} {d['android']:<10} {d['cpu_abi']}")

    if args.watch:
        print("\nWatching for changes... (Ctrl+C to stop)")
        while True:
            time.sleep(2)
            new_devices = get_devices()
            if new_devices != devices:
                print(f"\n[{time.strftime('%H:%M:%S')}] Device change detected")
                devices = new_devices

if __name__ == "__main__":
    main()
