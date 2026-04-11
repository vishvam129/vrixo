#!/usr/bin/env bash
# Launch Vrixo Streamlit app
# Usage: ./run.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure venv exists
if [ ! -d "venv" ]; then
    echo "❌ venv/ not found. Run: python3 -m venv venv && ./venv/bin/pip install -r ai/requirements.txt"
    exit 1
fi

# Set PYTHONPATH so `ai` and `web` packages are importable
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Launch Streamlit
exec ./venv/bin/streamlit run web/app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false
