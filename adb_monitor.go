package main

import (
	"fmt"
	"os"
	"os/exec"
	"strings"
	"time"
)

// adb_monitor.go — Watch for ADB device connect/disconnect events
// Usage: go run adb_monitor.go
func main() {
	fmt.Println("👁️  ADB Device Monitor — detecting connections/disconnections")
	fmt.Println("Press Ctrl+C to stop\n")

	lastDevices := getDevices()
	for {
		time.Sleep(2 * time.Second)
		current := getDevices()

		// Detect new devices
		for _, dev := range current {
			found := false
			for _, last := range lastDevices {
				if dev == last {
					found = true
					break
				}
			}
			if !found {
				fmt.Printf("✅ [CONNECTED] %s\n", dev)
			}
		}

		// Detect disconnections
		for _, last := range lastDevices {
			found := false
			for _, dev := range current {
				if dev == last {
					found = true
					break
				}
			}
			if !found {
				fmt.Printf("🔌 [DISCONNECTED] %s\n", last)
			}
		}

		lastDevices = current
	}
}

func getDevices() []string {
	cmd := exec.Command("adb", "devices", "-l")
	out, err := cmd.Output()
	if err != nil {
		return []string{}
	}

	var devices []string
	for _, line := range strings.Split(string(out), "\n") {
		if strings.Contains(line, "device") && !strings.HasPrefix(line, "List") {
			fields := strings.Fields(line)
			if len(fields) > 0 {
				devices = append(devices, fields[0])
			}
		}
	}
	return devices
}
