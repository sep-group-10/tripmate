#!/bin/bash
set -euo pipefail

SSM_PATH="/tripmate/prod/"
REGION="ap-south-1"
OUT_FILE=".env.production"

TMP_FILE="$(mktemp)"
trap 'rm -f "$TMP_FILE"' EXIT

aws ssm get-parameters-by-path \
  --path "$SSM_PATH" \
  --with-decryption \
  --query "Parameters[*].[Name,Value]" \
  --output json \
  --region "$REGION" |
  python3 -c '
import json, sys

params = json.load(sys.stdin)
if not params:
    sys.exit("No parameters found under the given SSM path")

for name, value in params:
    key = name.rsplit("/", 1)[-1]
    value = value.replace("\\", "\\\\").replace("\n", "\\n")
    print(f"{key}={value}")
' > "$TMP_FILE"

mv "$TMP_FILE" "$OUT_FILE"
chmod 600 "$OUT_FILE"

echo "Wrote $(wc -l < "$OUT_FILE") secrets to $OUT_FILE"
