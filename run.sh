#!/bin/bash

start_docker_compose() {
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
  echo "Cassandra launched!"
  docker-compose -f kafka/docker-compose.yml up -d

  # Manually activate kafka-connect ./start-and-wait.sh script
  echo "Loading kafka-connect start-and-wait script..."
  docker exec -d kafka-connect "./start-and-wait.sh"

  # -- Producers initialization of containers
  # OpenWeatherMap API
  echo -n "Do you want to start OpenWeatherMap Producer? (y/n) > "
  read -r OWM_OPTION

  if [ "$OWM_OPTION" == "y" ]
  then
    echo "Initializing OpenWeatherMap producer service..."
    docker-compose -f owm-producer/docker-compose.yml up -d
  fi

  # Twitter API
  echo -n "Do you want to start Twitter Producer? (y/n) > "
  read -r TWITTER_OPTION

  if [ "$TWITTER_OPTION" == "y" ]
  then
    echo "Initializing Twitter producer service..."
    docker-compose -f twitter-producer/docker-compose.yml up -d
  fi

  # Faker API
  echo -n "Do you want to start Faker Producer? (y/n) > "
  read -r FAKER_OPTION

  if [ "$FAKER_OPTION" == "y" ]
  then
    echo "Initializing Faker producer service..."
    docker-compose -f faker-producer/docker-compose.yml up -d
  fi


  # -- Run consumer containers
  echo -n "Do you want to start Consumer containers? (y/n) > "
  read -r CONSUMER_OPTION

  if [ "$CONSUMER_OPTION" == "y" ]
  then
    echo "Initializing consumer services..."
    docker-compose -f consumers/docker-compose.yml up -d
  fi

  # -- Data visualization container
  echo -n "Do you want to start Data Visualization container? (y/n) > "
  read -r VIS_OPTION

  if [ "$VIS_OPTION" == "y" ]
  then
    echo "Initializing Data-Vis service..."
    docker-compose -f data-vis/docker-compose.yml up -d
  fi

  echo "Done."
}

build_optional() {
  # Cassandra
  echo "Do you want to build the image for bootstrapcassandra? (y/n)"
  read -r CASS_OPTION

  if [ "$CASS_OPTION" == "y" ]
  then
    docker build -f cassandra/Dockerfile -t bootstrapcassandra:latest ./cassandra
  fi

  # kafka_connect
  echo "Do you want to build the image for kafka_connect? (y/n)"
  read -r KAFKA_OPTION

  if [ "$KAFKA_OPTION" == "y" ]
  then
    docker build -f kafka/connect.Dockerfile -t kafka_connect:latest ./kafka
  fi

  # owm-producer_openweathermap
  echo "Do you want to build the image for owm-producer_openweathermap? (y/n)"
  read -r OWM_OPTION

  if [ "$OWM_OPTION" == "y" ]
  then
    docker build -f owm-producer/Dockerfile -t owm-producer_openweathermap:latest ./owm-producer
  fi

  # twitter-producer_twitter_service
  echo "Do you want to build the image for twitter-producer_twitter_service? (y/n)"
  read -r TWITTER_OPTION

  if [ "$TWITTER_OPTION" == "y" ]
  then
    docker build -f twitter-producer/Dockerfile -t twitter-producer_twitter_service:latest ./twitter-producer
  fi

  # faker-producer_faker
  echo "Do you want to build the image for faker-producer_faker? (y/n)"
  read -r FAKER_OPTION

  if [ "$FAKER_OPTION" == "y" ]
  then
    docker build -f faker-producer/Dockerfile -t faker-producer_faker:latest ./faker-producer
  fi

  # faker-producer_faker
  echo "Do you want to build the image for faker-producer_faker? (y/n)"
  read -r FAKER_OPTION

  if [ "$FAKER_OPTION" == "y" ]
  then
    docker build -f faker-producer/Dockerfile -t faker-producer_faker:latest ./faker-producer
  fi

  
  # twitterconsumer
  echo "Do you want to build the image for consumer? (y/n)"
  read -r FAKER_OPTION

  if [ "$FAKER_OPTION" == "y" ]
  then
    docker build -f faker-producer/Dockerfile -t faker-producer_faker:latest ./faker-producer
  fi
}

execute() {
  local task=${1}
  case "${task}" in
    start)
      start_docker_compose
      ;;
  esac

}

err() {
    echo "$*" >&2
}

usage() {
    err "$(basename "$0"): [build|start|clean]"
}


main() {
  if [ $# -ne 1 ]
  then
    usage; 
    exit 1; 
  fi
  local task=${1}
  execute "${task}"
}

main "$@"