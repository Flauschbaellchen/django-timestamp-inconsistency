#!/usr/bin/env bash

set -e # always exit if an error occurs.

ROUNDS=20

MODEL_ID=$(psql --csv -qc "SELECT id FROM timestamps_mymodel ORDER BY random() LIMIT 1" | tail -n 1)
echo "Working on id: ${MODEL_ID}"

OLD_TIMESTAMP=$(psql --csv -qc "SELECT timestamp FROM timestamps_mymodel WHERE id='${MODEL_ID}'" | tail -n 1)

IDX=1
until [ $IDX -gt $ROUNDS ]; do
  TIMESTAMP=$(psql --csv -qc "SELECT timestamp FROM timestamps_mymodel WHERE id='${MODEL_ID}'" | tail -n 1)

  if [ "${OLD_TIMESTAMP}" != "${TIMESTAMP}" ]; then
    echo ""
    echo "Failed iteration ${IDX}: ${OLD_TIMESTAMP} != ${TIMESTAMP}"
    exit 1
  fi;

  psql -qc "UPDATE timestamps_mymodel SET timestamp='${OLD_TIMESTAMP}' WHERE id='${MODEL_ID}'"
  echo -n "."
  IDX=$((IDX+1))
done;
echo ""
