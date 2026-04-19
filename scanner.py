#!/usr/bin/env python3
"""
scanner.py -- Find ADB-enabled Android devices on local network
Uses direct ADB discovery or network scanning to locate devices.
Usage: python3 scanner.py                      # scan network
       python3 scanner.py --range 192.168.1.0/24
       python3 scanner.py --host 192.168.1.100
"""
import socket, subprocess, argparse, threading, time, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from ipaddress import ip_network, IPv4Network

def adb(cmd):
    r = subprocess.run(f"adb {cmd}", shell=True, capture_output=True, text=True, timeout=2)
    return r.returncode == 0, r.stdout.strip()

def get_local_network():
    """Infer local network from device IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        # Assume /24 network
        parts = ip.split('.')
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
    except Exception:
        return "192.168.1.0/24"

def scan_host(host, port=5555):
    """Try to connect to ADB on a single host"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def get_device_info(host):
    """Get device info via ADB"""
    try:
        ok, out = adb(f"connect {host}:5555")
        if ok:
            ok, model = adb(f"-s {host}:5555 shell getprop ro.product.model")
            ok, android = adb(f"-s {host}:5555 shell getprop ro.build.version.release")
            ok, api = adb(f"-s {host}:5555 shell getprop ro.build.version.sdk")
            return {
                'host': host,
                'model': model if ok else '?',
                'android': android if ok else '?',
                'api': api if ok else '?'
            }
    except Exception:
        pass
    return None

def scan_network(cidr, timeout=30):
    """Scan CIDR range for ADB devices"""
    try:
        net = ip_network(cidr, strict=False)
    except ValueError:
        print(f"Invalid CIDR: {cidr}")
        return []

    print(f"\n🔎 Scanning {cidr} for ADB devices (timeout: {timeout}s)...\n")
    found = []

    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = {}
        for host in net.hosts():
            host_str = str(host)
            future = executor.submit(scan_host, host_str)
            futures[future] = host_str

        for future in as_completed(futures, timeout=timeout):
            host = futures[future]
            if future.result():
                info = get_device_info(host)
                if info:
                    found.append(info)
                    print(f"  ✓ {host}")

    return found

def main():
    parser = argparse.ArgumentParser(description="Scan for ADB-enabled Android devices")
    parser.add_argument("--range", help="CIDR range (default: local /24)")
    parser.add_argument("--host", help="Single host to check")
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    if args.host:
        print(f"\n🔎 Checking {args.host}:5555...")
        if scan_host(args.host):
            info = get_device_info(args.host)
            if info:
                print(f"  ✓ Found! Model: {info['model']}, Android {info['android']}")
        else:
            print(f"  ✗ No ADB service on {args.host}")
        return

    cidr = args.range or get_local_network()
    devices = scan_network(cidr, timeout=args.timeout)

    if not devices:
        print("  No ADB devices found.")
        return

    print(f"\n{'Host':<18} {'Model':<25} {'Android':<10} {'API'}")
    print("─" * 60)
    for d in devices:
        print(f"{d['host']:<18} {d['model']:<25} {d['android']:<10} {d['api']}")

    print(f"\n✅ Found {len(devices)} device(s)")
    print("\nConnect: adb connect <host>:5555")

if __name__ == "__main__":
    main()
