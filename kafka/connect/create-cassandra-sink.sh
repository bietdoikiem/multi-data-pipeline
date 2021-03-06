#!/bin/sh


echo "Starting Twitter Sink"
curl -s \
     -X POST http://localhost:8083/connectors \
     -H "Content-Type: application/json" \
     -d '{
  "name": "twittersink",
  "config":{
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",  
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable":"false",
    "tasks.max": "10",
    "topics": "twittersink",
    "contactPoints": "cassandradb",
    "loadBalancing.localDc": "datacenter1",
    "topic.twittersink.kafkapipeline.twitterdata.mapping": "location=value.location, tweet_date=value.datetime, tweet=value.tweet, classification=value.classification",
    "topic.twittersink.kafkapipeline.twitterdata.consistencyLevel": "LOCAL_QUORUM"
  }
}'
echo "Starting Weather Sink"
curl -s \
     -X POST http://localhost:8083/connectors \
     -H "Content-Type: application/json" \
     -d '{
  "name": "weathersink",
  "config": {
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",  
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable":"false",
    "tasks.max": "10",
    "topics": "weather",
    "contactPoints": "cassandradb",
    "loadBalancing.localDc": "datacenter1",
    "topic.weather.kafkapipeline.weatherreport.mapping": "location=value.location, forecastdate=value.report_time, description=value.description, temp=value.temp, feels_like=value.feels_like, temp_min=value.temp_min, temp_max=value.temp_max, pressure=value.pressure, humidity=value.humidity, wind=value.wind, sunrise=value.sunrise, sunset=value.sunset",
    "topic.weather.kafkapipeline.weatherreport.consistencyLevel": "LOCAL_QUORUM"
  }
}'
echo "Starting Faker Sink"
curl -s \
     -X POST http://localhost:8083/connectors \
     -H "Content-Type: application/json" \
     -d '{
  "name": "fakersink",
  "config": {
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",  
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable":"false",
    "tasks.max": "10",
    "topics": "faker",
    "contactPoints": "cassandradb",
    "loadBalancing.localDc": "datacenter1",
    "topic.faker.kafkapipeline.fakerdata.mapping": "username=value.username, name=value.name, address=value.address, year=value.year, company=value.company, email=value.email, job=value.job, phone_number=value.phone_number, license_plate=value.license_plate, image_url=value.image_url",
    "topic.faker.kafkapipeline.fakerdata.consistencyLevel": "LOCAL_QUORUM"
  }
}'

echo "Starting CryptoPanic Sink"
curl -s \
     -X POST http://localhost:8083/connectors \
     -H "Content-Type: application/json" \
     -d '{
  "name": "cryptopanicsink",
  "config": {
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",  
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable":"false",
    "tasks.max": "10",
    "topics": "cryptopanic",
    "contactPoints": "cassandradb",
    "loadBalancing.localDc": "datacenter1",
    "topic.cryptopanic.kafkapipeline.cryptopanic_news.mapping": "kind=value.kind, source_title=value.source_title, source_domain=value.source_domain, title=value.title, published_at=value.published_at, url=value.url",
    "topic.cryptopanic.kafkapipeline.cryptopanic_news.consistencyLevel": "LOCAL_QUORUM"
  }
}'

echo "Starting Kraken XBT/USD Sink"
curl -s \
     -X POST http://localhost:8083/connectors \
     -H "Content-Type: application/json" \
     -d '{
  "name": "krakensink",
  "config": {
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",  
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable":"false",
    "tasks.max": "10",
    "topics": "krakensink",
    "contactPoints": "cassandradb",
    "loadBalancing.localDc": "datacenter1",
    "topic.krakensink.kafkapipeline.kraken_tick_data.mapping": "datetime=value.datetime, ask_value=value.ask_value, ask_volume=value.ask_volume, bid_value=value.bid_value, bid_volume=value.bid_volume, closed_value=value.closed_value, closed_volume=value.closed_volume, pair=value.pair",
    "topic.krakensink.kafkapipeline.kraken_tick_data.consistencyLevel": "LOCAL_QUORUM"
  }
}'
echo "Done."
