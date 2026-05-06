# Set Up the Search Box Keyboard Shortcut

Do this ONCE to bind Super+Space to the wiki search box:

## In XFCE:
1. Open: Settings Manager → Keyboard → Application Shortcuts tab
2. Click [+ Add]
3. Command: `/home/sourov/Documents/wiki-linux/wiki-linux/bin/wiki-search-dialog`
4. Press the key: `Super + Space` (or any key you prefer)
5. Click OK

## Result:
Press `Super+Space` anywhere → the dashboard menu pops up → search, ask Ollama, open browsers, or trim services.

---

## Set Up the Panel Status Bar (xfce4-genmon):

The `xfce4-genmon-plugin` is already installed.

1. Right-click your XFCE panel → Panel → Add New Items
2. Select "Generic Monitor" (genmon)
3. Right-click the new item → Properties
4. Command: `/home/sourov/.local/bin/wiki-panel`
5. Period: 60 (refresh every minute)
6. Click OK

You'll see: `◆ mistral | 42p | ✓ wiki` in your panel.

---

## Install HDD Backup Popup (needs sudo once):

```bash
sudo bash /home/sourov/Documents/wiki-linux/wiki-linux/etc/install-udev.sh
```

After that, plug in any USB drive → popup appears → click "Backup Now".
