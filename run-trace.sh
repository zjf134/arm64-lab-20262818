#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"
if [[ -f "$HOME/.local/arm64-toolchain/env.sh" ]]; then
    source "$HOME/.local/arm64-toolchain/env.sh"
fi
mkdir -p logs
qemu-aarch64 -g 12368 build/week040120262818 >logs/qemu-debug.log 2>&1 &
guest_pid=$!
trap 'kill "$guest_pid" 2>/dev/null || true' EXIT
gdb-multiarch --data-directory=/usr/share/gdb -q -nx -batch \
    -ex 'set logging file logs/gdb-trace.log' \
    -ex 'set logging overwrite on' -ex 'set logging enabled on' \
    -ex 'source trace.py' build/week040120262818
