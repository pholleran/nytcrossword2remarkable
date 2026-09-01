#!/bin/bash
set -euo pipefail

export APP_ROOT="${APP_ROOT:-/usr/src/app}"
export PYTHONPATH="$APP_ROOT:${PYTHONPATH:-}"

setup_rmapi_config() {
    if [[ -z "${DEVICE_TOKEN:-}" ]]; then
        echo "DEVICE_TOKEN is not set; rmapi authentication will fail unless --no-upload is used"
        return 0
    fi

    local config_file="$HOME/.config/rmapi/rmapi.conf"
    mkdir -p "$(dirname "$config_file")"

    cat > "$config_file" <<EOF
devicetoken: $DEVICE_TOKEN
usertoken:
EOF
    chmod 600 "$config_file"
    echo "rmapi configuration written to $config_file"
}

setup_rmapi_config
exec "$@"
