set -eufo pipefail

{{ if eq .chezmoi.os "darwin" -}}
if [ -d "/opt/homebrew/bin" ]; then
  PATH="/opt/homebrew/bin:$PATH"
fi
{{ end -}}

{{ if eq .machine_name "work" -}}
export NODE_EXTRA_CA_CERTS="${HOME}/.ssl/zscaler_root_ca.pem"
{{ end -}}
