#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

python3 -m py_compile tools/its_monitor_server.py
exec python3 tools/its_monitor_server.py "$@"
