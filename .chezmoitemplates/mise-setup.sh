{{ if eq .chezmoi.os "darwin" -}}
# Initialize mise for version management
if command -v mise &> /dev/null; then
  eval "$(mise activate bash)"
fi
{{ end -}}
