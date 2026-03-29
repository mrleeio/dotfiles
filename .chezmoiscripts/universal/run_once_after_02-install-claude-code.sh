#!/bin/bash
set -euo pipefail

if command -v claude &>/dev/null; then
  echo "Claude Code is already installed"
  exit 0
fi

echo "Installing Claude Code..."
curl -fsSL https://claude.ai/install.sh | bash
