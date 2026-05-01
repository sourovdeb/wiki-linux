#!/usr/bin/env bash
# Audio recording + whisper transcription -> wiki page.
set -euo pipefail

# Ensure arecord exists; it ships with alsa-utils.
if ! command -v arecord >/dev/null; then
  sudo pacman -S --noconfirm --needed alsa-utils
fi

cat > ~/.local/bin/wiki-transcribe <<'BASH'
#!/usr/bin/env bash
# Record audio with arecord, transcribe with whisper, save as wiki page.
set -euo pipefail
TS=$(date +%Y%m%d-%H%M%S)
TMP=/tmp/wiki-rec-$TS.wav
echo "🎙  Recording — press Ctrl+C to stop..."
arecord -f cd -t wav "$TMP" || true   # arecord exits 1 on Ctrl+C; that's fine
echo
echo "📝 Transcribing with whisper (this may take a minute)..."
OUTDIR=$(mktemp -d)
whisper "$TMP" --model base --output_dir "$OUTDIR" --output_format txt --language en >/dev/null 2>&1
TXT=$(cat "$OUTDIR"/*.txt)

DEST="$HOME/wiki/user/transcripts/transcript-$TS.md"
mkdir -p "$(dirname "$DEST")"
cat > "$DEST" <<EOF
---
title: Transcript $TS
updated: $(date +%Y-%m-%d)
tags: [transcript, audio]
source: $TMP
---

# Transcript — $(date)

$TXT
EOF
rm -f "$TMP"
rm -rf "$OUTDIR"
echo "✓ Saved: $DEST"
command -v obsidian >/dev/null && obsidian "obsidian://open?path=$DEST" &
BASH
chmod +x ~/.local/bin/wiki-transcribe

cat > ~/Desktop/WIKI-TOOLS/RECORD-AUDIO.desktop <<EOF
[Desktop Entry]
Type=Application
Name=Record + Transcribe
Comment=Record audio, transcribe with whisper, save to wiki
Exec=xfce4-terminal -e $HOME/.local/bin/wiki-transcribe
Icon=audio-input-microphone
Terminal=false
EOF
chmod +x ~/Desktop/WIKI-TOOLS/RECORD-AUDIO.desktop

echo "✓ wiki-transcribe ready at ~/.local/bin/wiki-transcribe"
echo "  Pre-download whisper 'base' model on first run (~140MB)."
