#!/bin/bash
#
# Save a database snapshot for the current git branch.

BRANCH=`git rev-parse --abbrev-ref HEAD`
DATE=`date +%Y-%m-%d-%H-%M-%S`
DUMPFILE="pfi-$BRANCH.$DATE.dump"
DBNAME="trackerdb"
FOLDER="db-snapshots"
OWNER="tracker"

if [ ! -d "$FOLDER" ]; then
  mkdir $FOLDER
fi

docker-compose exec postgresql pg_dump -U $OWNER --format=custom $DBNAME > $FOLDER/$DUMPFILE
