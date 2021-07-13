#!/bin/bash -i

echo -n "Which container do you want to access? > "
read -r CONTAINER

echo "Accessing $CONTAINER container..."
if [ "$CONTAINER" == "cassandra" ]
then
  echo -n "Do you want to access CQLSH? (y/N) > "
  read -r CQLSH_OPTION
  if [ "$CQLSH_OPTION" == "y" ]
  then
    docker exec -it "$CONTAINER" "./cql.sh"
  else
    docker exec -it "$CONTAINER" bash
  fi
else 
  docker exec -it "$CONTAINER" bash
fi