#!/bin/bash
set -eufo pipefail

KEY_PATH="${HOME}/.config/chezmoi/key.txt"

if [ ! -f "$KEY_PATH" ]; then
    echo ""
    echo "ERROR: Age encryption key not found at ${KEY_PATH}"
    echo ""
    echo "This key is required to decrypt sensitive files (SSH config, GitHub hosts)."
    echo "Copy it from an existing machine:"
    echo ""
    echo "  scp other-machine:~/.config/chezmoi/key.txt ${KEY_PATH}"
    echo ""
    exit 1
fi
