import requests
from requests.models import Response
from asyncio.queues import Queue
import asyncio


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
