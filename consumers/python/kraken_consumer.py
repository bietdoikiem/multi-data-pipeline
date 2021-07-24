import asyncio
from typing import final
from aiokafka import AIOKafkaConsumer
# import pandas as pd
import os, json


async def consume():
  print("Starting Kraken Consumer")
  TOPIC_NAME = os.environ.get("TOPIC_NAME") if os.environ.get(
      "TOPIC_NAME") else "kraken_btc"
  KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL", "localhost:9092")
  # CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST", "localhost")
  # CASSANDRA_KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE", "kafkapipeline")

  print("Setting up Kafka consumer at {}".format(KAFKA_BROKER_URL))
  consumer = AIOKafkaConsumer(TOPIC_NAME, bootstrap_servers=[KAFKA_BROKER_URL])
  await consumer.start()

  print("Waiting for Kraken msg...")
  try:
    async for msg in consumer:
      msg = msg.value.decode('utf-8')
      jsonData = json.loads(msg)
      # add print for checking
      print("=> Tick received")
      print(jsonData)
  finally:
    print("Finally Done!")
    await consumer.stop()


if __name__ == "__main__":
  asyncio.run(consume())