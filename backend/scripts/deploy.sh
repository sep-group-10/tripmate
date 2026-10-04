#!/bin/bash
set -euo pipefail

# set -e: keep checks as `if cmd; then` / `if ! cmd; then`, not `cmd; if [ $? ... ]`
# (the latter lets set -e kill the script before the check runs).

# ---- Settings (fixed values used everywhere in this script) ----
IMAGE_NAME="ghcr.io/sep-group-10/tripmate-api"
PROJECT_DIR="/opt/tripmate"
ENV_FILE="${PROJECT_DIR}/.env.production"
LOCK_FILE="${PROJECT_DIR}/.deploy.lock"
UPSTREAM_CONF="/etc/nginx/conf.d/upstream.conf"
SWITCH_BACKEND_SCRIPT="/usr/local/bin/switch-backend.sh"
CURRENT_TAG_FILE="${PROJECT_DIR}/current_tag.txt"
PREVIOUS_TAG_FILE="${PROJECT_DIR}/previous_tag.txt"
PORT_A=8000
PORT_B=8001
HEALTH_PATH="/health"
HEALTH_RETRY_SECONDS=2
HEALTH_TIMEOUT_SECONDS=120
DRAIN_SECONDS=10
IMAGES_TO_KEEP=5

# ---- Input ----
NEW_TAG="${1:-}"

main() {
  acquire_lock
  find_live_port
  remove_stale_containers
  pull_image
  pick_target_port
  start_new_container
  health_check_new_container
  switch_traffic
  drain_and_remove_old_container
  cleanup_old_images
}

acquire_lock() {
  echo "[1/10] Acquiring lock..."
  exec 200>"$LOCK_FILE"
  if ! flock -n 200; then
    echo "ERROR: another deploy is already running (lock: $LOCK_FILE). Exiting."
    exit 1
  fi
  echo "Lock acquired."
}

find_live_port() {
  echo "[2/10] Finding live port from nginx config..."
  if [ ! -f "$UPSTREAM_CONF" ]; then
    echo "No upstream config found yet. Treating as first-ever deploy."
    LIVE_PORT=""
    return
  fi

  # This parsing expects the exact format switch-backend.sh writes. If you
  # change the output format there, update this grep too.
  LIVE_PORT="$(grep -oE '127\.0\.0\.1:[0-9]+' "$UPSTREAM_CONF" | head -n1 | grep -oE '[0-9]+$')"

  if [ "$LIVE_PORT" != "$PORT_A" ] && [ "$LIVE_PORT" != "$PORT_B" ]; then
    echo "ERROR: upstream config has an unexpected port: '$LIVE_PORT'. Refusing to guess."
    exit 1
  fi

  echo "Live port is currently: $LIVE_PORT"
}

remove_stale_containers() {
  echo "[3/10] Checking for stale containers..."
  for port in "$PORT_A" "$PORT_B"; do
    container_name="tripmate-${port}"

    if ! docker inspect "$container_name" >/dev/null 2>&1; then
      continue
    fi

    if [ "$port" != "$LIVE_PORT" ]; then
      echo "Removing stale container: $container_name (port $port != live port $LIVE_PORT)"
      docker rm -f "$container_name" >/dev/null
    fi
  done
}

pull_image() {
  if [ -z "$NEW_TAG" ]; then
    echo "ERROR: no image tag given. Usage: deploy.sh <commit-sha>"
    exit 1
  fi

  if ! [[ "$NEW_TAG" =~ ^[0-9a-f]{7,40}$ ]]; then
    echo "ERROR: '$NEW_TAG' doesn't look like a commit SHA. Usage: deploy.sh <commit-sha>"
    exit 1
  fi

  FULL_IMAGE="${IMAGE_NAME}:${NEW_TAG}"
  echo "[4/10] Pulling image: $FULL_IMAGE"
  docker pull "$FULL_IMAGE"
}

pick_target_port() {
  if [ -z "$LIVE_PORT" ]; then
    echo "[5/10] No container is live yet. Bootstrapping on port $PORT_A."
    TARGET_PORT="$PORT_A"
  elif [ "$LIVE_PORT" = "$PORT_A" ]; then
    TARGET_PORT="$PORT_B"
  else
    TARGET_PORT="$PORT_A"
  fi
  echo "[5/10] New container will start on port: $TARGET_PORT"
}

start_new_container() {
  NEW_CONTAINER_NAME="tripmate-${TARGET_PORT}"
  echo "[6/10] Starting $NEW_CONTAINER_NAME on port $TARGET_PORT..."

  docker rm -f "$NEW_CONTAINER_NAME" >/dev/null 2>&1 || true

  docker run -d \
    --name "$NEW_CONTAINER_NAME" \
    --env-file "$ENV_FILE" \
    -p "127.0.0.1:${TARGET_PORT}:8000" \
    "$FULL_IMAGE"
}

health_check_new_container() {
  echo "[7/10] Health checking $NEW_CONTAINER_NAME on port $TARGET_PORT..."
  local waited=0
  local url="http://127.0.0.1:${TARGET_PORT}${HEALTH_PATH}"

  while [ "$waited" -lt "$HEALTH_TIMEOUT_SECONDS" ]; do
    if curl -fs "$url" >/dev/null 2>&1; then
      echo "Healthy after ${waited}s."
      return 0
    fi
    sleep "$HEALTH_RETRY_SECONDS"
    waited=$((waited + HEALTH_RETRY_SECONDS))
  done

  echo "ERROR: $NEW_CONTAINER_NAME did not become healthy within ${HEALTH_TIMEOUT_SECONDS}s."
  echo "--- Last container logs ---"
  docker logs "$NEW_CONTAINER_NAME" --tail 50 || true
  echo "Stopping and removing the failed container. Old container is untouched."
  docker rm -f "$NEW_CONTAINER_NAME" >/dev/null 2>&1 || true
  exit 1
}

switch_traffic() {
  echo "[8/10] Switching traffic to port $TARGET_PORT..."

  if [ -f "$CURRENT_TAG_FILE" ]; then
    cp "$CURRENT_TAG_FILE" "$PREVIOUS_TAG_FILE"
  fi

  sudo "$SWITCH_BACKEND_SCRIPT" "$TARGET_PORT"

  echo "$NEW_TAG" > "$CURRENT_TAG_FILE"
}

drain_and_remove_old_container() {
  if [ -z "$LIVE_PORT" ]; then
    echo "[9/10] No old container to remove (this was the first-ever deploy)."
    return
  fi

  old_container_name="tripmate-${LIVE_PORT}"
  echo "[9/10] Draining for ${DRAIN_SECONDS}s before stopping $old_container_name..."
  sleep "$DRAIN_SECONDS"

  docker rm -f "$old_container_name" >/dev/null 2>&1 || true
  echo "Old container ($old_container_name) stopped and removed."
}

cleanup_old_images() {
  echo "[10/10] Cleaning up old images (keeping newest $IMAGES_TO_KEEP)..."

  mapfile -t old_images < <(
    docker images "$IMAGE_NAME" --format '{{.CreatedAt}}|{{.ID}}' |
      sort -r |
      cut -d'|' -f2 |
      tail -n "+$((IMAGES_TO_KEEP + 1))"
  )

  if [ "${#old_images[@]}" -eq 0 ]; then
    echo "Nothing to clean up."
    return
  fi

  for image_id in "${old_images[@]}"; do
    if [ "$image_id" = "$(docker inspect -f '{{.Id}}' "$FULL_IMAGE" 2>/dev/null | cut -c8-19)" ]; then
      echo "Skipping $image_id - currently in use."
      continue
    fi
    echo "Removing old image: $image_id"
    docker rmi "$image_id" >/dev/null 2>&1 || true
  done
}

main
