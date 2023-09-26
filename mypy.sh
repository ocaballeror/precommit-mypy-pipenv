#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"
reqs=/tmp/reqs-$(basename $PWD)-$(md5sum Pipfile.lock | awk '{print $1}')
if ! [ -f "$reqs" ]; then
  rm -f /tmp/reqs-$(basename $PWD)-*
  pipenv requirements > $reqs
  pip install -r $reqs
fi

mypy "$@"
