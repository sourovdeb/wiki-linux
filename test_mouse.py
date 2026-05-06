#!/usr/bin/env python3

import evdev
from evdev import ecodes

print("Looking for mouse devices...")
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

mouse_device = None
for device in devices:
    if 'mouse' in device.name.lower() or 'elan' in device.name.lower():
        mouse_device = device
        print(f"Found mouse device: {device.name} at {device.path}")
        break

if not mouse_device:
    print("No mouse device found")
    exit(1)

print(f"Monitoring {mouse_device.name} for button events...")
print("Press Ctrl+C to stop")

try:
    for event in mouse_device.read_loop():
        if event.type == ecodes.EV_KEY:
            print(f"Button {event.code}: {'pressed' if event.value == 1 else 'released'}")
            if event.code == ecodes.BTN_RIGHT:
                print("  -> RIGHT CLICK DETECTED!")
except KeyboardInterrupt:
    print("\nMonitoring stopped")