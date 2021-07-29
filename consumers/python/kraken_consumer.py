import asyncio
import sys
from typing import final
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
# import pandas as pd
import os
import ujson
from datetime import datetime
import time

TOPIC_NAME = os.environ.get("TOPIC_NAME") if os.environ.get(
    "TOPIC_NAME") else "kraken"
SINK_TOPIC_NAME = os.environ.get("SINK_TOPIC_NAME") if os.environ.get(
    "SINK_TOPIC_NAME") else "krakensink"
KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL", "localhost:9092")


def reformat_msg(msg):
  value_info = msg['result'][1]
  # datetime.utcnow().isoformat(sep=' ', timespec='milliseconds')
  tick_datetime_str: str = datetime.fromtimestamp(float(
      msg['timestamp'])).isoformat(sep=' ', timespec='milliseconds')
  return {
      "datetime": tick_datetime_str,
      "ask_value": value_info['a'][0],
      "ask_volume": value_info['a'][2],
      "bid_value": value_info['b'][0],
      "bid_volume": value_info['b'][2],
      "closed_value": value_info['c'][0],
      "closed_volume": value_info['c'][1],
      "pair": msg['result'][3]
  }


async def init_producer(broker_url):
  print("Setting up Kraken producer at {}".format(broker_url))
  producer = AIOKafkaProducer(
      bootstrap_servers=[broker_url],
    # Encode all values as JSON
      value_serializer=lambda x: ujson.dumps(x).encode('utf-8'),
  )
  # Retry connection to producer
  maxReconnections = 20
  isConnected = False
  while (isConnected != True and maxReconnections > 0):
    try:
      await producer.start()
      isConnected = True
    except Exception as error:
      print(
          "Failed to connect Kafka Producer (%s) \nRetrying Kafka Producer..." %
          error)
      time.sleep(5)
      maxReconnections -= 1

    # If failed to reconnect
    print(isConnected)
    if (isConnected == False):
      print("Kafka Producer failed to start! Exitting application...")
      await producer.stop()
      sys.exit(1)
  return producer


async def init_consumer(topic, broker_url):
  print("Setting up Kafka consumer at {}".format(broker_url))
  consumer = AIOKafkaConsumer(topic, bootstrap_servers=[broker_url])
  await consumer.start()
  return consumer


async def consume_and_produce_sink():
  # CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST", "localhost")
  # CASSANDRA_KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE", "kafkapipeline")
  print("Starting Kraken Consumer and Producer")
  producer = await init_producer(KAFKA_BROKER_URL)
  consumer = await init_consumer(TOPIC_NAME, KAFKA_BROKER_URL)

  print("Waiting for Kraken msg...")
  try:
    async for msg in consumer:
      msg = msg.value.decode('utf-8')
      msg = ujson.loads(msg)
      await producer.send_and_wait(SINK_TOPIC_NAME, value=reformat_msg(msg))
      # add print for checking
      print(f"=> Tick at {msg['timestamp']} sent successfully!")
  finally:
    print("Finally Done with Producer & Consumer!")
    await consumer.stop()
    await producer.stop()


if __name__ == "__main__":
  asyncio.run(consume_and_produce_sink())