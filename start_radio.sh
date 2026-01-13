#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# 0. Initialize opam environment (Liquidsoap engine)
if command -v opam > /dev/null 2>&1; then
    echo ">>> Initializing opam..."
    eval $(opam env)
fi

echo ">>> Starting Automated Radio Station..."

# 1. Setup Virtual Environment (Python logic)
if [ ! -d ".venv" ]; then
    echo ">>> Creating .venv..."
    python3 -m venv .venv
fi
source .venv/bin/activate

# 2. Install/Update Python dependencies
echo ">>> Checking Python dependencies..."
if [ -f "requirements.txt" ]; then
    # Install dependencies quietly, only show output if there are errors
    pip install -q -r requirements.txt || {
        echo "⚠️  Warning: Some dependencies failed to install"
        echo "    Continuing anyway..."
    }
fi

# 3. Cleanup existing instances
echo ">>> Cleaning up old processes..."
pkill -f "liquidsoap.*config/station.liq" || true
pkill -f "icecast.*config/icecast.xml" || true
sleep 1

# 4. Running
echo ">>> Booting servers..."
mkdir -p logs data music

# Start Icecast
icecast -c config/icecast.xml -b > logs/icecast_startup.log 2>&1
sleep 2

# Start Liquidsoap
liquidsoap config/station.liq
