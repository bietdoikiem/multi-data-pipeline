from datetime import datetime
import time
import os
from aiokafka import AIOKafkaProducer
import sys
import ujson
from src.types import CryptoPanicResponse, CryptoPanicSchema
from src.utils.fetch_utils import batch_async_fetch
import configparser
import asyncio

KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
TOPIC_NAME = os.environ.get("TOPIC_NAME") if os.environ.get(
    "TOPIC_NAME") else "cryptopanic"
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 30))

# CryptoPanic API Key
config = configparser.ConfigParser()
config.read('cryptopanic_service.cfg')
cryptopanic_api_credential = config['cryptopanic_api_credential']
CRYPTOPANIC_API_KEY = cryptopanic_api_credential['api_key']


async def main():
  print("Setting up Kafka Producer at : {}".format(KAFKA_BROKER_URL))
  producer = AIOKafkaProducer(
      bootstrap_servers=[KAFKA_BROKER_URL],
      value_serializer=lambda x: ujson.dumps(x).encode('utf-8'),
      enable_idempotence=True)
  retry = 0
  limit = 50
  while True:
    try:
      res = await producer.start()
      if (res):
        break
    except Exception as error:
      retry += 1
      if (retry <= limit):
        print("Retrying Kafka Producer...")
        retry += 1
        time.sleep(5)
      else:
        print("Kafka Producer failed to start (%s)" % error)
        await producer.stop()
        sys.exit(1)

  fetch_urls = [
      f"https://cryptopanic.com/api/v1/posts/?auth_token={CRYPTOPANIC_API_KEY}&page={page}"
      for page in range(10, 0, -1)
  ]
  print("Fetching posts from CryptoPanic API...")
  fetch_list = await batch_async_fetch(fetch_urls)
  JSON_responses = [
      CryptoPanicResponse(count=res['count'],
                          next=res['next'],
                          previous=res['previous'],
                          results=res['results']) for res in fetch_list
  ]
  iterator = 0
  print("Sending CryptoPanic News data...")
  for response in JSON_responses:
    for news in response.results:
      iterator += 1
      # print(news['kind'])
      data = CryptoPanicSchema(news['kind'], news['source']['title'],
                               news['source']['domain'], news['title'],
                               news['published_at'], news['url'])
      try:
        await producer.send_and_wait(TOPIC_NAME, value=news)
      except Exception as error:
        print("Producer failed to send! (%s)" % error)
      print("=> News no.", iterator, "sent")
      print(ujson.dumps(data.__dict__))
      time.sleep(0.5)
  await producer.stop()


if __name__ == "__main__":
  asyncio.run(main())