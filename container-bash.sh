#!/bin/bash

echo "Which container do you want to access?"
read -r CONTAINER;

echo "Accessing $CONTAINER..."
docker exec -it "$CONTAINER" bash