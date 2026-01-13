#!/usr/bin/env liquidsoap

# --- Configuration ---
# Set the rigorous error checking
settings.init.allow_root.set(true)

# Function to get the next track from Python script
def get_next_track() =
  # Use the python binary from the virtual environment
  cmd = ".venv/bin/python3 scripts/playlist_manager.py"
  result = process.read.lines(cmd)
  if list.length(result) > 0 then
    uri = list.nth(result, 0)
    # Return a request object, not just a string
    request.create(uri)
  else
    # Fallback if python script fails
    request.create("") 
  end
end

# Define the dynamic source
radio = request.dynamic(id="dynamic_playlist", get_next_track)

# --- Audio Processing ---

# Step 1: Compress dynamic range to reduce volume differences
# This makes loud parts quieter and quiet parts louder
# ratio: compression ratio (3.0 means 3:1 compression)
# threshold: level above which compression starts (in dB)
# gain: makeup gain after compression
radio = compress.exponential(
  ratio=3.0,
  threshold=-15.,
  gain=3.,
  radio
)

# Step 2: LUFS-based loudness normalization
# This is more accurate than simple RMS normalization
# target: -14 LUFS is the standard for streaming services
# window: measurement window in seconds
radio = loudness(
  target=-14.,
  window=3.,
  radio
)

# Step 3: Limiter to prevent clipping and peaks
# This ensures no audio goes above 0 dB
radio = limit(
  threshold=-1.,
  radio
)

# Crossfade logic
# simple crossfade
radio = crossfade(fade_out=2., fade_in=2., duration=3., radio)

# Safe fallback (silence) to prevent stream crashes if playlist fails
# mksafe ensures the source is always available
radio = mksafe(radio)

# --- Output ---

# Stream to local Icecast
output.icecast(
  %mp3(bitrate=192),
  host = "localhost",
  port = 8000,
  password = "hackme",
  mount = "/radio",
  name = "My Automated Radio",
  description = "Powered by Liquidsoap and Arch Linux",
  url = "http://localhost:8000/radio",
  radio
)

# Output to speakers for debugging (optional, can be commented out)
# output.audio(radio)
