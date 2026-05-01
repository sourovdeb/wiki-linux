#!/bin/bash
# 03-whisper-pipeline.sh
# Audio recording → whisper → wiki page pipeline

set -euo pipefail

echo "🎤 Setting up whisper pipeline..."

# Install whisper.cpp if not available
if ! command -v whisper.cpp &> /dev/null; then
    echo "📦 Installing whisper.cpp..."
    cd /tmp
    git clone https://github.com/ggerganov/whisper.cpp.git
    cd whisper.cpp
    make
    sudo make install
    cd ..
    rm -rf whisper.cpp
else
    echo "✅ whisper.cpp already installed"
fi

# Create recording script
RECORD_SCRIPT=~/bin/record-to-wiki
cat > "$RECORD_SCRIPT" << 'EOF'
#!/bin/bash
# record-to-wiki - Record audio, transcribe with whisper, create wiki page

set -euo pipefail

# Check for required tools
for cmd in arecord whisper.cpp; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "❌ Missing dependency: $cmd"
        exit 1
    fi
done

# Get recording title
TITLE=$(zenity --entry \
    --title="🎤 New Audio Note" \
    --text="Enter a title for this recording:" \
    --width=400 \
    2>/dev/null) || exit 0

if [[ -z "$TITLE" ]]; then
    zenity --info --text="No title provided. Recording cancelled." --width=300 2>/dev/null
    exit 0
fi

# Create slug for filename
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-')
DATE=$(date +%Y-%m-%d)
AUDIO_FILE=~/wiki/_tmp/${DATE}-${SLUG}.wav
TEXT_FILE=~/wiki/user/notes/${DATE}-${SLUG}.md

# Show recording dialog
zenity --info \
    --title="🎤 Recording" \
    --text="Speak now... Press OK when finished." \
    --width=300 \
    2>/dev/null || true

# Record audio (5 second buffer)
echo "🎤 Recording audio..."
mkdir -p ~/wiki/_tmp
arecord -f cd -d 300 "$AUDIO_FILE" 2>/dev/null || true

# Transcribe with whisper
echo "🤖 Transcribing with whisper..."
mkdir -p ~/wiki/user/notes
whisper.cpp -m /usr/local/share/whisper.cpp/models/ggml-base.en.bin -f "$AUDIO_FILE" -otxt > "${TEXT_FILE%.md}.txt" 2>/dev/null || true

# Create wiki page
echo "📝 Creating wiki page..."
cat > "$TEXT_FILE" << WIKI
---
title: $TITLE
created: $(date -u +%Y-%m-%dT%H:%M:%SZ)
tags: [audio, transcription]
---

# $TITLE

## 🎤 Audio Recording
[Listen to original]($AUDIO_FILE)

## 📝 Transcription
$(cat "${TEXT_FILE%.md}.txt")

## 💡 Notes
- Recorded on: $(date)
- Duration: $(soxi -D "$AUDIO_FILE" 2>/dev/null || echo "unknown") seconds
- Model: whisper.cpp base.en

WIKI

# Clean up temporary files
rm -f "${TEXT_FILE%.md}.txt"

# Show completion
zenity --info \
    --title="✅ Recording Complete" \
    --text="Audio note created:\n\n$TITLE\n\nFile: $TEXT_FILE\n\nThe transcription is now in your wiki!" \
    --width=400 \
    2>/dev/null || true

echo "🎉 Created: $TEXT_FILE"
EOF

chmod +x "$RECORD_SCRIPT"

# Create desktop entry for easy access
cat > ~/.local/share/applications/record-to-wiki.desktop << EOF
[Desktop Entry]
Name=Record to Wiki
Comment=Record audio and transcribe to wiki
Exec=/home/sourov/bin/record-to-wiki
Icon=audio-x-generic
Terminal=false
Type=Application
Categories=AudioVideo;Utility;
StartupWMClass=RecordToWiki
EOF

# Create Thunar custom action for audio files
THUNAR_UCA=~/.config/Thunar/uca.xml
if [[ ! -f "$THUNAR_UCA" ]]; then
    echo "⚠️  Thunar UCA not found, creating..."
    mkdir -p ~/.config/Thunar
    echo '<?xml version="1.0" encoding="UTF-8"?><actions/>' > "$THUNAR_UCA"
fi

# Add audio transcription action if not present
if ! grep -q "Transcribe to Wiki" "$THUNAR_UCA"; then
    echo "📝 Adding audio transcription action to Thunar..."
    sed -i '/<\/actions>/d' "$THUNAR_UCA"
    cat >> "$THUNAR_UCA" << 'ACTIONS'
  <action>
    <icon>audio-x-generic</icon>
    <name>Transcribe to Wiki</name>
    <command>/home/sourov/bin/record-to-wiki --transcribe "%f"</command>
    <description>Transcribe this audio file to wiki</description>
    <patterns>*.wav;*.mp3;*.ogg;*.m4a</patterns>
    <audio-files/>
  </action>
</actions>
ACTIONS
fi

echo "✅ Whisper pipeline configured!"
echo ""
echo "Usage:"
echo "  record-to-wiki  # Start new recording"
echo "  # Or right-click audio files in Thunar → Transcribe to Wiki"