#!/bin/bash
echo "Accessing Cassandra QL Manager..."
echo "What is the version of CQL?"
read -r CQL_VERSION

docker exec -it cassandra bash "cqlsh --cqlversion=$CQL_VERSION 127.0.0.1"