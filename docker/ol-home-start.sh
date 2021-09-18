#!/bin/bash

# quick method to start all ol services from one script
# inside an container, bypass all upstart/services

python --version

echo "Waiting for postgres..."
until pg_isready --host db; do sleep 5; done
start=$SECONDS
make reindex-solr
duration=$(( SECONDS - start ))
echo "reindex-solr took $duration seconds"
echo "You may now open to localhost:8080"
