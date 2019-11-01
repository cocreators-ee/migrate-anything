#!/usr/bin/env sh
set -e

echo Running migrations
echo

migrate-anything migrations

echo
echo Applying new migration
echo

cp migrations/01-test.py migrations/02-test.py
migrate-anything migrations

echo
echo Undoing old migration
echo

rm -f migrations/02-test.py
migrate-anything migrations
if [ -f "test-file.txt" ]; then
    echo Undo did not work.
    exit 1
fi
