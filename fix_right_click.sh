#!/bin/bash

echo "Attempting to fix right-click issue..."

# Reset button mapping to default
echo "Resetting mouse button mapping..."
xinput set-button-map 11 1 2 3 4 5 6 7

# Try to reload input devices
echo "Reloading input devices..."
sudo udevadm trigger --subsystem-match=input --action=change

# Check if the device is still detected
echo "Checking mouse detection..."
xinput list | grep -i mouse

# Provide alternative methods
echo ""
echo "If right-click still doesn't work, try these alternatives:"
echo "1. Use Shift+F10 as a keyboard alternative to right-click"
echo "2. Try the menu key (usually near the right Ctrl key) on your keyboard"
echo "3. Hold down left-click for a few seconds to see if it brings up a context menu"
echo "4. Try right-clicking in different applications to see if it's app-specific"
echo "5. Try connecting an external USB mouse to test if the issue is hardware-related"

echo ""
echo "Right-click troubleshooting completed."