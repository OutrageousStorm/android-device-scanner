#!/usr/bin/env python3
"""
scan.py -- Scan connected Android devices and show detailed info
Usage: python3 scan.py
"""
import subprocess, json

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

# Get devices
devices_out = subprocess.run("adb devices", shell=True, capture_output=True, text=True).stdout
devices = [l.split("\t")[0] for l in devices_out.split("\n") if "device" in l and not l.startswith("List")]

if not devices:
    print("❌ No devices connected")
    exit(1)

print(f"\n📱 Found {len(devices)} device(s)\n")

for device in devices:
    # Build info
    model = adb(f"-s {device} shell getprop ro.product.model")
    android = adb(f"-s {device} shell getprop ro.build.version.release")
    cores = adb(f"-s {device} shell nproc")
    
    print(f"Device: {device}")
    print(f"  Model:   {model}")
    print(f"  Android: {android}")
    print(f"  CPU cores: {cores}")
    print()
