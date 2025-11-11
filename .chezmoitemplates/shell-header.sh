set -eufo pipefail

{{ if eq .chezmoi.os "darwin" -}}
# macOS-specific PATH setup
if [ -d "/opt/homebrew/bin" ]; then
  PATH="/opt/homebrew/bin:$PATH"
fi
{{ end -}}
