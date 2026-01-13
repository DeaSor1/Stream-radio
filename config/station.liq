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

# Normalization: ensure consistent volume
# target: target RMS amplitude (dB)
# window: window size for measurement
radio = normalize(target=-13., window=5., radio)

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
