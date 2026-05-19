package main

import (
	"fmt"
	"net"
	"os/exec"
	"strings"
	"sync"
	"time"
	"flag"
)

// network_scan.go — Scan local network for ADB-enabled Android devices
// Usage: go run network_scan.go [--subnet 192.168.1] [--port 5555] [--timeout 500]

type Device struct {
	IP      string
	Port    int
	Model   string
	Android string
}

func probeADB(ip string, port int, timeout time.Duration, wg *sync.WaitGroup, results chan<- Device) {
	defer wg.Done()
	addr := fmt.Sprintf("%s:%d", ip, port)
	conn, err := net.DialTimeout("tcp", addr, timeout)
	if err != nil {
		return
	}
	conn.Close()

	// Try to connect and get device info
	cmd := exec.Command("adb", "connect", addr)
	cmd.Run()
	time.Sleep(300 * time.Millisecond)

	out, err := exec.Command("adb", "-s", addr, "shell", "getprop ro.product.model").Output()
	if err != nil {
		return
	}
	model := strings.TrimSpace(string(out))

	ver, _ := exec.Command("adb", "-s", addr, "shell", "getprop ro.build.version.release").Output()
	android := strings.TrimSpace(string(ver))

	if model != "" {
		results <- Device{IP: ip, Port: port, Model: model, Android: android}
	}
}

func main() {
	subnet := flag.String("subnet", "192.168.1", "Subnet to scan (e.g. 192.168.1)")
	port := flag.Int("port", 5555, "ADB port to probe")
	timeout := flag.Int("timeout", 500, "Connection timeout in ms")
	flag.Parse()

	fmt.Printf("🔍 Scanning %s.1-254:%d for ADB devices...\n\n", *subnet, *port)

	results := make(chan Device, 20)
	var wg sync.WaitGroup

	for i := 1; i <= 254; i++ {
		ip := fmt.Sprintf("%s.%d", *subnet, i)
		wg.Add(1)
		go probeADB(ip, *port, time.Duration(*timeout)*time.Millisecond, &wg, results)
	}

	go func() {
		wg.Wait()
		close(results)
	}()

	found := 0
	for d := range results {
		fmt.Printf("✅ %s:%d — %s (Android %s)\n", d.IP, d.Port, d.Model, d.Android)
		found++
	}

	if found == 0 {
		fmt.Println("No ADB devices found on network.")
	} else {
		fmt.Printf("\nFound %d device(s)\n", found)
	}
}
