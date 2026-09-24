#!/bin/bash
# Copy this case's fixture folder into the agent's working directory.
# (Folders shared via add_dirs are readable only by the Read tool, which cannot open .xlsx.)
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
cp -R "$here/input" ./input
