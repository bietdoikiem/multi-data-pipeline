from asyncio.queues import Queue
from datetime import datetime
import time
import os
from aiokafka import AIOKafkaProducer
from requests.models import Response
import ujson
import requests
from src.types import CryptoPanicResponse, CryptoPanicSchema
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


async def producer(queue: Queue, arg, callback):
  result: Response
  try:
    result = await callback(arg)
    await asyncio.sleep(0.2)
    await queue.put(result.json())
  except Exception as error:
    print("Producer failed (%s)" % error)
  return result


async def consumer(queue: Queue, agg_result: list):
  result = await queue.get()
  queue.task_done()
  agg_result.append(result)


async def fetch(url):
  try:
    r = requests.get(url)
    return r
  except Exception as error:
    print("Request to CryptoPanic failed (%s)" % error)
  return None


async def batch_async_fetch(url_list):
  agg_result = []
  queue = asyncio.Queue()

  # fire up both producers and consumers
  producers = [
      asyncio.create_task(producer(queue, url, fetch)) for url in url_list
  ]
  consumers = [
      asyncio.create_task(consumer(queue, agg_result))
      for _ in range(len(url_list))
  ]

  # with both producers and consumers running, wait for
  # the producers to finish
  await asyncio.gather(*producers)

  # wait for the remaining tasks to be processed
  await queue.join()

  # cancel the consumers, which are idle
  for c in consumers:
    c.cancel()

  return agg_result


async def main():
  print("Setting up Kafka Producer at : {}".format(KAFKA_BROKER_URL))
  try:
    producer = AIOKafkaProducer(
        bootstrap_servers=[KAFKA_BROKER_URL],
        value_serializer=lambda x: ujson.dumps(x).encode('utf-8'),
    )
    await producer.start()
  except Exception as error:
    print("Kafka Producer failed to start (%s)" % error)
    await producer.stop()

  fetch_urls = [
      f"https://cryptopanic.com/api/v1/posts/?auth_token={CRYPTOPANIC_API_KEY}&page={page}"
      for page in range(10, 0, -1)
  ]
  fetch_list = await batch_async_fetch(fetch_urls)
  JSON_responses = [
      CryptoPanicResponse(count=res['count'],
                          next=res['next'],
                          previous=res['previous'],
                          results=res['results']) for res in fetch_list
  ]
  iterator = 0
  print("Starting CryptoPanic News API...")
  for response in JSON_responses:
    for news in response.results:
      iterator += 1
      print("++News sent++", iterator)
      print(news)
      # print(news['kind'])
      data = CryptoPanicSchema(news['kind'], news['source']['title'],
                               news['source']['domain'], news['title'],
                               news['published_at'], news['url'])
    # producer.send(TOPIC_NAME, value=news)
    print(ujson.dumps(data.__dict__))
    time.sleep(0.5)


if __name__ == "__main__":
  asyncio.run(main())