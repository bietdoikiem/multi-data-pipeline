#!/bin/bash

#! Initialize network
echo "Do you want to create the required networks? (y/n)"
read -r NETWORK_OPTION

if [ "$NETWORK_OPTION" == "y" ]
then
  docker network create kafka-network
  docker network create cassandra-network
fi

# -- Run Cassandra container
docker-compose -f cassandra/docker-compose.yml up -d

# -- Run Kafka container
docker-compose -f kafka/docker-compose.yml up -d

# Manually activate kafka-connect ./start-and-wait.sh script
echo "Loading kafka-connect start-and-wait script..."
sleep 2
docker exec -d kafka-connect "./start-and-wait.sh"

# -- Producers initialization of containers
# OpenWeatherMap API
echo "Do you want to start OpenWeatherMap Producer? (y/n)"
read -r OWM_OPTION

if [ "$OWM_OPTION" == "y" ]
then
  echo "Initializing OpenWeatherMap producer service..."
  docker-compose -f owm-producer/docker-compose.yml up -d
fi

# Twitter API
echo "Do you want to start Twitter Producer? (y/n)"
read -r TWITTER_OPTION

if [ "$TWITTER_OPTION" == "y" ]
then
  echo "Initializing Twitter producer service..."
  docker-compose -f twitter-producer/docker-compose.yml up -d
fi

# Faker API
echo "Do you want to start Faker Producer? (y/n)"
read -r FAKER_OPTION

if [ "$FAKER_OPTION" == "y" ]
then
  echo "Initializing Faker producer service..."
  docker-compose -f faker-producer/docker-compose.yml up -d
fi

# -- Run consumer containers
echo "Do you want to start Consumer containers? (y/n)"
read -r CONSUMER_OPTION

if [ "$CONSUMER_OPTION" == "y" ]
then
  echo "Initializing consumer services..."
  docker-compose -f consumers/docker-compose.yml up -d
fi

# -- Data visualization container
echo "Do you want to start Data Visualization container? (y/n)"
read -r VIS_OPTION

if [ "$VIS_OPTION" == "y" ]
then
  echo "Initializing Data-Vis service..."
  docker-compose -f data-vis/docker-compose.yml up -d
fi

echo "Done."