#!/bin/bash
set -euo pipefail

# REFERENCE ONLY - the real, running copy is /usr/local/bin/switch-backend.sh
# on the server (sudoers points there). Update both if you change this.
#
# Points nginx at the given port and reloads it. Separate script because
# this needs sudo; deploy.sh itself does not.
#
# Needs a sudoers rule granting NOPASSWD for the 3 exact commands below.
# Add via `sudo visudo -f /etc/sudoers.d/tripmate-deploy` (confirm nginx's
# real path with `which nginx` first - this assumes /usr/sbin/nginx):
#   deploy_user ALL=(root) NOPASSWD: /usr/bin/tee /etc/nginx/conf.d/upstream.conf
#   deploy_user ALL=(root) NOPASSWD: /usr/sbin/nginx -t
#   deploy_user ALL=(root) NOPASSWD: /usr/sbin/nginx -s reload

UPSTREAM_CONF="/etc/nginx/conf.d/upstream.conf"
NEW_PORT="${1:-}"

if [ -z "$NEW_PORT" ]; then
  echo "ERROR: no port given. Usage: switch-backend.sh <port>"
  exit 1
fi

# deploy.sh's find_live_port greps this exact "127.0.0.1:<port>" format.
# If you change this, update that grep too.
printf 'upstream tripmate_backend {\n    server 127.0.0.1:%s;\n}\n' "$NEW_PORT" | sudo tee "$UPSTREAM_CONF" >/dev/null
sudo nginx -t
sudo nginx -s reload

echo "nginx now pointing at port $NEW_PORT"
