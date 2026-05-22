package main
import (
    "fmt"
    "os/exec"
    "strings"
)

type Device struct {
    Serial string
    State  string
}

func getDevices() []Device {
    cmd := exec.Command("adb", "devices", "-l")
    out, _ := cmd.Output()
    lines := strings.Split(string(out), "\n")
    var devices []Device
    for _, line := range lines {
        parts := strings.Fields(line)
        if len(parts) >= 2 {
            devices = append(devices, Device{parts[0], parts[1]})
        }
    }
    return devices
}

func getDeviceInfo(serial string) map[string]string {
    props := make(map[string]string)
    cmd := exec.Command("adb", "-s", serial, "shell", "getprop", "ro.product.model")
    out, _ := cmd.Output()
    props["model"] = strings.TrimSpace(string(out))
    return props
}

func main() {
    devices := getDevices()
    fmt.Printf("Found %d devices:\n", len(devices))
    for _, dev := range devices {
        fmt.Printf("  %s [%s]\n", dev.Serial, dev.State)
    }
}
