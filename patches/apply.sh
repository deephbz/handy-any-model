#!/usr/bin/env bash
# Clone upstream Handy at the tested commit and apply the Handy Local patch.
set -euo pipefail
BASE=b38987a9075e62baafef11263cf8b7448dc38b51
REPO="${HANDY_REPO:-https://github.com/cjpais/Handy.git}"
DEST="${1:-handy}"
HERE="$(cd "$(dirname "$0")" && pwd)"
git clone "$REPO" "$DEST"
git -C "$DEST" checkout --detach "$BASE"
git -C "$DEST" apply "$HERE/handy-local.patch"
echo "Patched Handy in $DEST. Next: docs/playbook.md, step 2."
