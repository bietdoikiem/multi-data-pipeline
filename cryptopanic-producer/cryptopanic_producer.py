import time
import os
from typing import List
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
SLEEP_TIME = int(os.environ.get("SLEEP_TIME"))

# CryptoPanic API Key
config = configparser.ConfigParser()
config.read('cryptopanic_service.cfg')
cryptopanic_api_credential = config['cryptopanic_api_credential']
CRYPTOPANIC_API_KEY = cryptopanic_api_credential['api_key']


async def send_many(producer: AIOKafkaProducer,
                    json: List[CryptoPanicResponse]):
  iterator = 0
  for response in json:
    for news in response.results:
      iterator += 1
      data = CryptoPanicSchema(news['kind'], news['source']['title'],
                               news['source']['domain'], news['title'],
                               news['published_at'],
                               news['url'].replace("\/", "/"))
      data_dict = vars(data)
      await producer.send_and_wait(TOPIC_NAME, value=data_dict)
      print("=> News no.", iterator, "sent")
      await asyncio.sleep(0.8)


async def main():
  print("Setting up Kafka Producer at : {}".format(KAFKA_BROKER_URL))
  producer = AIOKafkaProducer(
      bootstrap_servers=[KAFKA_BROKER_URL],
      value_serializer=lambda x: ujson.dumps(x).encode('utf-8'),
  )
  maxReconnections = 20
  isSuccess = False
  while (isSuccess == False and maxReconnections > 0):
    try:
      await producer.start()
      isSuccess = True
    except Exception as error:
      print(
          "Failed to connect Kafka Producer (%s) \nRetrying Kafka Producer..." %
          error)
      time.sleep(5)
      maxReconnections -= 1

  print(isSuccess)
  if (isSuccess == False):
    print("Kafka Producer failed to start! Exitting application...")
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
  print("Sending CryptoPanic News data...")
  try:
    await send_many(producer, JSON_responses)
    print("All Done.")
  finally:
    await producer.stop()


def main_run_forever():
  while True:
    try:
      asyncio.run(main())
      print("Finished! Sleeping and waiting for another call!")
      time.sleep(SLEEP_TIME)
    except Exception:
      break


if __name__ == "__main__":
  main_run_forever()