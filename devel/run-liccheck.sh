#!/bin/bash

trap 'rm -f "$TMPFILE"' EXIT

set -e

TMPFILE=$(mktemp -t requirements-XXXXXX.txt)

set -x

poetry export --dev -f requirements.txt -o $TMPFILE
# poetry run pip freeze --exclude-editable --isolated > $TMPFILE

poetry run liccheck -r $TMPFILE
