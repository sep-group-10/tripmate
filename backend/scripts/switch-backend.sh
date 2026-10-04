#!/bin/bash
set -euo pipefail

# Rewrites the nginx upstream file to point at the given port, then reloads
# nginx. Must be run with sudo (deploy.sh calls it as "sudo switch-backend.sh").
# Matches the sudoers rule: deploy ALL=(ALL) NOPASSWD: /usr/local/bin/switch-backend.sh *

UPSTREAM_CONF="/etc/nginx/conf.d/upstream.conf"
NEW_PORT="${1:-}"

if [ -z "$NEW_PORT" ]; then
  echo "ERROR: no port given. Usage: switch-backend.sh <port>"
  exit 1
fi

# deploy.sh's find_live_port greps this exact "127.0.0.1:<port>" format.
# If you change this, update that grep too.
printf 'upstream tripmate_backend {\n    server 127.0.0.1:%s;\n}\n' "$NEW_PORT" | tee "$UPSTREAM_CONF" >/dev/null
nginx -t
nginx -s reload

echo "nginx now pointing at port $NEW_PORT"
