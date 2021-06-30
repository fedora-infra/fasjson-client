#!/bin/sh

set -e

here=$(realpath $(dirname $0))
output="${here}/requirements.txt"

set -x

poetry export -f requirements.txt --without-hashes -o "${output}"

# Remove the python versions annotations
sed -i -e 's/; .\+$//' "${output}"

# Remove the GSSAPI module because ReadTheDocs does not install C-based modules
sed -i -e '/^gssapi==/d ; /^requests-gssapi==/d' "${output}"
