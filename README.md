# How to Build a Distributed Big Data Pipeline Using Kafka and Docker

This is based on the repo https://github.com/salcaino/sfucmpt733/tree/main/foobar-kafka.
Substantial changes and bug fixes have been made. Tested on Windows 10. 

# Quickstart instructions

#Create docker networks
```bash
$ docker network create kafka-network                         # create a new docker network for kafka cluster (zookeeper, broker, kafka-manager services, and kafka connect sink services)
$ docker network create cassandra-network                     # create a new docker network for cassandra. (kafka connect will exist on this network as well in addition to kafka-network)
```
## Starting Cassandra

Cassandra is setup so it runs keyspace and schema creation scripts at first setup so it is ready to use.
```bash
$ docker-compose -f cassandra/docker-compose.yml --env-file .env up -d
```

## Starting kafka on docker
```bash
$ docker-compose -f kafka/docker-compose.yml --env-file .env up -d            # start single zookeeper, broker, kafka-manager and kafka-connect services
$ docker ps -a                                                # sanity check to make sure services are up: kafka_broker_1, kafka-manager, zookeeper, kafka-connect service
```

> **Note:** 
Kafka front end is available at http://localhost:9000

> Kafka-Connect REST interface is available at http://localhost:8083

IMPORTANT: There is a bug that I don't know how to fix yet. You have to manually go to CLI of the "kafka-connect" container and run the below comment to start the Cassandra sinks.
```
./start-and-wait.sh
```

## Starting Producers
```bash
$ docker-compose -f owm-producer/docker-compose.yml --env-file .env up -d     # start the producer that retrieves open weather map
$ docker-compose -f twitter-producer/docker-compose.yml --env-file .env up -d # start the producer for twitter
```
## Starting Twitter classifier (plus Weather consumer)

Start consumers:
```bash
$ docker-compose -f consumers/docker-compose.yml --env-file .env up -d        # start the consumers
```

## Check that data is arriving to Cassandra

First login into Cassandra's container with the following command or open a new CLI from Docker Desktop if you use that.
```bash
$ docker exec -it cassandra bash
```
Once loged in, bring up cqlsh with this command and query twitterdata and weatherreport tables like this:
```bash
$ cqlsh --cqlversion=3.4.4 127.0.0.1 #make sure you use the correct cqlversion

cqlsh> use kafkapipeline; #keyspace name

cqlsh:kafkapipeline> select * from twitterdata;

cqlsh:kafkapipeline> select * from weatherreport;
```

And that's it! you should be seeing records coming in to Cassandra. Feel free to play around with it by bringing down containers and then up again to see the magic of fault tolerance!


## Visualization
```
docker-compose -f data-vis/docker-compose.yml --env-file .env up -d
```

## Teardown

To stop all running kakfa cluster services

```bash
$ docker-compose -f consumers/docker-compose.yml down          # stop the consumers

$ docker-compose -f owm-producer/docker-compose.yml down       # stop open weather map producer

$ docker-compose -f twitter-producer/docker-compose.yml down   # stop twitter producer

$ docker-compose -f kafka/docker-compose.yml down              # stop zookeeper, broker, kafka-manager and kafka-connect services

$ docker-compose -f cassandra/docker-compose.yml down          # stop Cassandra
```

To remove the kafka-network network:

```bash
$ docker network rm kafka-network
$ docker network rm cassandra-network
```




