#!/usr/bin/env bash
# Prefix+Q: open the spaced flashcard quiz in a session-scoped popup.
#
# Reuse the existing scoped mouse lease and restoration, so drag-to-copy
# also works when the invoking session inherits mouse=on. Global options
# and unrelated sessions remain untouched.
set -uo pipefail
exec bash "${BASH_SOURCE[0]%/*}/vim-drill-popup-force.sh" --quiz
