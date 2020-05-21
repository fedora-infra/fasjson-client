#!/bin/sh

set -e

here=`dirname $0`
output="${here}/requirements.txt"

set -x

poetry export -f requirements.txt -o "${output}"

# Remove the GSSAPI module because ReadTheDocs does not install C-based modules
sed -i -e '/^gssapi==/d' "${output}"
