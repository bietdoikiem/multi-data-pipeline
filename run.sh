#!/bin/bash

# Start process
start() {
  #! Initialize network
  echo "Do you want to create the required networks? (y/N)"
  read -r NETWORK_OPTION

  if [ "$NETWORK_OPTION" == "y" ]
  then
    docker network create kafka-network
    docker network create cassandra-network
  fi

  # -- Run Cassandra container
  echo "Setting up Cassandra service... ⏳︎"
  docker-compose -f cassandra/docker-compose.yml up -d
  progress-bar 5
  echo "=> Cassandra launched! ✅"

  # -- Run Kafka container
  echo "Setting up Kafka services... ⏳︎"
  docker-compose -f kafka/docker-compose.yml up -d
  progress-bar 5
  echo "=> Kafka launched! ✅"

  # Manually activate kafka-connect ./start-and-wait.sh script
  # echo "Loading kafka-connect start-and-wait script..."

  # -- Producers initialization of containers
  # OpenWeatherMap API
  echo -n "Do you want to start OpenWeatherMap Producer? (y/N) > "
  read -r OWM_OPTION

  if [ "$OWM_OPTION" == "y" ]
  then
    echo "Initializing OpenWeatherMap producer service... ⏳︎"
    docker-compose -f owm-producer/docker-compose.yml up -d
    echo "=> OWM service launched! ✅"
  fi

  # Twitter API
  echo -n "Do you want to start Twitter Producer? (y/N) > "
  read -r TWITTER_OPTION

  if [ "$TWITTER_OPTION" == "y" ]
  then
    echo "Initializing Twitter producer service... ⏳︎"
    docker-compose -f twitter-producer/docker-compose.yml up -d
    echo "=> Twitter service launched! ✅"
  fi

  # Faker API
  echo -n "Do you want to start Faker Producer? (y/N) > "
  read -r FAKER_OPTION

  if [ "$FAKER_OPTION" == "y" ]
  then
    echo "Initializing Faker producer service... ⏳︎"
    docker-compose -f faker-producer/docker-compose.yml up -d
    echo "=> Faker service launched! ✅"
  fi

    # Faker API
  echo -n "Do you want to start Kraken Producer? (y/N) > "
  read -r KRAKEN_OPTION

  if [ "$KRAKEN_OPTION" == "y" ]
  then
    echo "Initializing Kraken producer service... ⏳︎"
    docker-compose -f kraken-producer/docker-compose.yml up -d
    echo "=> Kraken service launched! ✅"
  fi


  # -- Run consumer containers
  echo -n "Do you want to start Consumer containers? (y/N) > "
  read -r CONSUMER_OPTION

  if [ "$CONSUMER_OPTION" == "y" ]
  then
    echo "Initializing consumer services... ⏳︎"
    docker-compose -f consumers/docker-compose.yml up -d
    echo "=> Consumer services launched! ✅"
  fi

  # -- Data visualization container
  echo -n "Do you want to start Data Visualization container? (y/N) > "
  read -r VIS_OPTION

  if [ "$VIS_OPTION" == "y" ]
  then
    echo "Initializing Data-Vis service... ⏳︎"
    docker-compose -f data-vis/docker-compose.yml up -d
    echo "=> Data-vis service launched! ✅"
  fi

  # docker exec -d kafka-connect "./start-and-wait.sh"
  echo "Done."
}

# Build images processs
build() {
  # Cassandra
  echo -n "Do you want to build the image for bootstrapcassandra? (y/N) > "
  read -r CASS_OPTION

  if [ "$CASS_OPTION" == "y" ]
  then
    docker build -f cassandra/Dockerfile -t bootstrapcassandra:latest ./cassandra
  fi

  # kafka_connect
  echo -n "Do you want to build the image for kafka_connect? (y/N) > "
  read -r KAFKA_OPTION

  if [ "$KAFKA_OPTION" == "y" ]
  then
    docker build -f kafka/connect.Dockerfile -t kafka_connect:latest ./kafka
  fi

  # owm-producer_openweathermap
  echo -n "Do you want to build the image for owm-producer_openweathermap? (y/N) > "
  read -r OWM_OPTION

  if [ "$OWM_OPTION" == "y" ]
  then
    docker build -f owm-producer/Dockerfile -t owm-producer_openweathermap:latest ./owm-producer
  fi

  # twitter-producer_twitter_service
  echo -n "Do you want to build the image for twitter-producer_twitter_service? (y/N) > "
  read -r TWITTER_OPTION

  if [ "$TWITTER_OPTION" == "y" ]
  then
    docker build -f twitter-producer/Dockerfile -t twitter-producer_twitter_service:latest ./twitter-producer
  fi

  # faker-producer_faker
  echo -n "Do you want to build the image for faker-producer_faker? (y/N) > "
  read -r KRAKEN_OPTION

  if [ "$KRAKEN_OPTION" == "y" ]
  then
    docker build -f kraken-producer/Dockerfile -t kraken-producer_kraken:latest ./kraken-producer
  fi

    # faker-producer_faker
  echo -n "Do you want to build the image for kraken-producer_kraken? (y/N) > "
  read -r FAKER_OPTION

  if [ "$FAKER_OPTION" == "y" ]
  then
    docker build -f faker-producer/Dockerfile -t faker-producer_faker:latest ./faker-producer
  fi
  
  # twitterconsumer
  echo -n "Do you want to build the image for consumer? (y/N) > "
  read -r CONSUMER_OPTION

  if [ "$CONSUMER_OPTION" == "y" ]
  then
    docker build -f consumers/Dockerfile -t consumer:latest ./consumers
  fi

  # data-vis
  echo -n "Do you want to build the image for datavis? (y/N) > "
  read -r VIS_OPTION

  if [ "$VIS_OPTION" == "y" ]
  then
    docker build -f data-vis/Dockerfile -t datavis:laterst ./data-vis
  fi

  # Cleaning up dangling images after build
  echo "Cleaning up dangling images after build..."
  docker image prune
  echo "Build DONE."
}

# Clean process
clean() {
  # shellcheck disable=SC2046
  docker stop $(docker ps -a -q)  
  # shellcheck disable=SC2046 
  docker rm $(docker ps -a -q)
  docker container prune
  docker volume prune
  echo "Clean DONE."
}

execute() {
  local task=${1}
  case "${task}" in
    start)
      start
      ;;
    build)
      build
      ;;
    clean)
      clean
      ;;
    *)
      err "invalid task: ${task}"
      usage
      exit 1
      ;;
  esac
}

err() {
    echo "$*" >&2
}

usage() {
    err "$(basename "$0"): [start|build|clean]"
}

# import progress-bar function
# shellcheck disable=SC1091
source ./progress-bar.sh

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