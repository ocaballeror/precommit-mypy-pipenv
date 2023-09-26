#!/usr/bin/env bash
set -e

tmp="$(dirname $VIRTUAL_ENV)/tmp"
mkdir -p "$tmp"
reqs="$tmp/reqs-$(md5sum Pipfile.lock | awk '{print $1}')"
if ! [ -f "$reqs" ]; then
  pipenv requirements > $reqs
  pip install -r $reqs
fi
mypy "$@"
