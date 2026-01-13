#!/usr/bin/env python3
"""
Normalize all audio files in the music directory to consistent loudness.
Uses ffmpeg-normalize with EBU R128 standard (-16 LUFS).
"""

import os
import subprocess
import sys
from pathlib import Path

# Configuration
MUSIC_DIR = Path(__file__).parent.parent / "music"
TARGET_LOUDNESS = -16  # LUFS (Loudness Units Full Scale)
AUDIO_EXTENSIONS = [".mp3", ".flac", ".wav", ".m4a", ".ogg"]


def check_ffmpeg_normalize():
    """Check if ffmpeg-normalize is installed."""
    try:
        subprocess.run(
            ["ffmpeg-normalize", "--version"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def normalize_file(file_path: Path, backup: bool = True):
    """
    Normalize a single audio file.
    
    Args:
        file_path: Path to the audio file
        backup: Whether to create a backup of the original file
    """
    print(f"📊 Normalizing: {file_path.name}")
    
    # Create backup if requested
    if backup:
        backup_path = file_path.with_suffix(file_path.suffix + ".backup")
        if not backup_path.exists():
            import shutil
            shutil.copy2(file_path, backup_path)
            print(f"   💾 Backup created: {backup_path.name}")
    
    try:
        # Run ffmpeg-normalize
        # -nt peak: normalization type (peak normalization)
        # -t: target level in LUFS
        # -c:a libmp3lame: audio codec for MP3
        # -b:a 320k: bitrate
        # -ar 44100: sample rate
        # -f: force overwrite
        
        cmd = [
            "ffmpeg-normalize",
            str(file_path),
            "-nt", "ebu",  # EBU R128 normalization
            "-t", str(TARGET_LOUDNESS),  # Target loudness
            "-c:a", "libmp3lame",  # MP3 codec
            "-b:a", "320k",  # Bitrate
            "-ar", "44100",  # Sample rate
            "-f",  # Force overwrite
            "-o", str(file_path)  # Output to same file
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"   ✅ Normalized successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error normalizing file: {e}")
        print(f"   Error output: {e.stderr}")
        return False


def main():
    """Main function to normalize all audio files."""
    
    # Check if ffmpeg-normalize is installed
    if not check_ffmpeg_normalize():
        print("❌ ffmpeg-normalize is not installed!")
        print("\nTo install it, run:")
        print("  pip install ffmpeg-normalize")
        print("\nOr with the virtual environment:")
        print("  source .venv/bin/activate")
        print("  pip install ffmpeg-normalize")
        sys.exit(1)
    
    # Find all audio files
    audio_files = []
    for ext in AUDIO_EXTENSIONS:
        audio_files.extend(MUSIC_DIR.glob(f"*{ext}"))
    
    if not audio_files:
        print(f"⚠️  No audio files found in {MUSIC_DIR}")
        sys.exit(0)
    
    print(f"🎵 Found {len(audio_files)} audio files")
    print(f"🎯 Target loudness: {TARGET_LOUDNESS} LUFS")
    print(f"📁 Music directory: {MUSIC_DIR}")
    print()
    
    # Ask for confirmation
    response = input("Do you want to normalize all files? (y/n): ")
    if response.lower() != 'y':
        print("❌ Cancelled")
        sys.exit(0)
    
    # Normalize each file
    success_count = 0
    fail_count = 0
    
    for i, file_path in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}]")
        if normalize_file(file_path, backup=True):
            success_count += 1
        else:
            fail_count += 1
    
    # Summary
    print("\n" + "="*50)
    print(f"✅ Successfully normalized: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📊 Total: {len(audio_files)}")
    print("="*50)
    
    if success_count > 0:
        print("\n🎉 Normalization complete!")
        print("💡 Tip: You can now remove the .backup files if everything sounds good:")
        print(f"   rm {MUSIC_DIR}/*.backup")


if __name__ == "__main__":
    main()
