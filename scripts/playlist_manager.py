#!/usr/bin/env python3
import os
import random
import sys
import json
from pathlib import Path

# Try to import mutagen for bitrate detection
try:
    from mutagen.mp3 import MP3
    from mutagen.oggvorbis import OggVorbis
    from mutagen.flac import FLAC
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False

HISTORY_FILE = Path('data/history.json')
HISTORY_LIMIT = 10 # Number of tracks to remember

def get_bitrate(filepath):
    """Returns bitrate in bps, or 0 if unknown."""
    if not HAS_MUTAGEN:
        return 0
    try:
        ext = filepath.suffix.lower()
        if ext == '.mp3':
            audio = MP3(filepath)
            return audio.info.bitrate
        elif ext == '.ogg':
            audio = OggVorbis(filepath)
            return audio.info.bitrate
        elif ext == '.flac':
            audio = FLAC(filepath)
            # Rough estimate for lossless
            return 1411000 
    except Exception:
        pass
    return 0

def load_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

def main():
    # Force better randomness seed
    random.seed()
    
    music_dir = Path('./music').resolve()
    if not music_dir.exists():
        sys.exit(1)

    extensions = {'.mp3', '.ogg', '.wav', '.flac', '.m4a'}
    all_tracks = [str(p) for p in music_dir.rglob('*') if p.suffix.lower() in extensions]

    if not all_tracks:
        sys.exit(1)

    history = load_history()
    
    # Adaptive history limit: don't block everything if there are few tracks
    actual_limit = min(len(all_tracks) // 2, HISTORY_LIMIT)
    
    # Filter out recently played tracks
    available_tracks = [t for t in all_tracks if t not in history[-actual_limit:]]
    
    if not available_tracks:
        available_tracks = all_tracks # Fallback if history blocking is too aggressive

    scored_tracks = []
    for t_path in available_tracks:
        br = get_bitrate(Path(t_path))
        # Weight formula: min weight 1, plus 1 for every 64kbps
        # Lowered impact of bitrate to increase variety
        weight = 1 + (br // 128000) 
        scored_tracks.append((t_path, weight))

    # Weighted random selection
    total_weight = sum(w for t, w in scored_tracks)
    r = random.uniform(0, total_weight)
    upto = 0
    selected = available_tracks[0]
    for t, w in scored_tracks:
        if upto + w >= r:
            selected = t
            break
        upto += w
    
    # Update history
    history.append(selected)
    save_history(history[-20:]) # Keep last 20 in file for safety
    
    print(selected)

if __name__ == "__main__":
    main()
