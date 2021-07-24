import asyncio
from datetime import date, datetime
import sys
import os
from aiokafka import AIOKafkaProducer
import ujson
from websocket import create_connection
import time
import aiohttp

KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 30))


def reformat_response(res):
  value_info = res[1]['c']
  return {
      "datetime": datetime.utcnow().isoformat(sep=' ', timespec='milliseconds'),
      "last_trade_value": value_info[0],
      "volume": value_info[1],
      "pair": res[3]
  }


def in_range(number, low, high):
  return low <= number <= high


async def run(pair: list):
  print("Setting up Kraken producer at {}".format(KAFKA_BROKER_URL))
  producer = AIOKafkaProducer(
      bootstrap_servers=[KAFKA_BROKER_URL],
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
  # Open websocket connection and subscribe to ticker feed for XBT/USD
  session = aiohttp.ClientSession()

  async with session.ws_connect("wss://ws.kraken.com") as ws:
    # Send websocket subscription to XBT/USD
    print("Setting subscription to Ticker XBT/uSD")
    try:
      await ws.send_json(
          {
              "event": "subscribe",
              "pair": pair,
              "subscription": {
                  "name": "ticker"
              }
          },
          dumps=ujson.dumps)
      await asyncio.sleep(1)
    except Exception as error:
      print("WebSocket subscription/request failed!")
      print(error)
      ws.close()
      sys.exit(1)
    # Keep connection to retrieve data from ticker Kraken API
    try:
      async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
          current_timestamp = datetime.utcnow().timestamp()
          response = ujson.loads(msg.data)
          if (isinstance(response, list)):
            await producer.send_and_wait(TOPIC_NAME,
                                         value=reformat_response(response))
            print(f"Tick at {current_timestamp} sent!")
        elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
          break
    except Exception as error:
      print("WebSocket failed!")
      print(error)
      await producer.stop()
      await ws.close()
    finally:
      print("Finally Done with Websocket Connection!")
      await producer.stop()
      await ws.close()
  await session.close()


if __name__ == "__main__":
  print("Setting up Kraken BTC...")
  asyncio.run(run(["XBT/USD"]))
