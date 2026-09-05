#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "=== OmniClaim AI: Installing Backend Dependencies ==="
python -m pip install --upgrade pip
pip install -r backend/requirements.txt

echo "=== OmniClaim AI: Building Frontend Assets ==="
if command -v npm &> /dev/null; then
  cd frontend
  npm install
  npm run build
  cd ..
else
  echo "Warning: npm command not found. Utilizing tracked frontend/dist bundle."
fi

echo "=== OmniClaim AI: Build Process Complete ==="
