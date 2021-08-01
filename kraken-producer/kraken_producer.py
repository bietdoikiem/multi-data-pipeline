import asyncio
from datetime import date, datetime
import sys
import os
from aiokafka import AIOKafkaProducer
import ujson
from websocket import create_connection
import time
import aiohttp
import logging
import socket

KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 30))

# logger = logging.getLogger(__name__)

# logging.basicConfig(
#     stream=sys.stdout,
#     level=logging.DEBUG,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# def reformat_response(res):
#   value_info = res[1]['c']
#   return {
#       "datetime": datetime.utcnow().isoformat(sep=' ', timespec='milliseconds'),
#       "last_trade_value": value_info[0],
#       "volume": value_info[1],
#       "pair": res[3]
#   }


def timestamp_response(current_ts, res):
  return {"timestamp": current_ts, "result": res}


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
  shutdown = False
  # Open forever websocket connection and subscribe to ticker feed for XBT/USD
  while (shutdown == False):
    session = aiohttp.ClientSession(json_serialize=ujson.dumps)
    async with session.ws_connect("wss://ws.kraken.com") as ws:
      # Send websocket subscription to XBT/USD
      print("Setting subscription to Ticker XBT/USD")
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
                                           value=timestamp_response(
                                               current_timestamp, response))
              print(
                  f"Tick event type {response[0]} at {current_timestamp} sent!")
          elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
            try:
              pong = await ws.ping()
              await asyncio.wait_for(pong, timeout=5)
              print("Ping OK, keeping connection alive...")
              continue
            except:
              print(
                  'Ping error - retrying connection in 5 sec (Ctrl-C to quit)')
              await asyncio.sleep(5)
              break
      except (asyncio.CancelledError, aiohttp.ClientError):
        print("Client disconnected from Websocket!")
        break
      except KeyboardInterrupt:
        shutdown = True
        print("Finally Done with Websocket Connection!")
        break
      finally:
        await producer.stop()
        await ws.close()
      await session.close()
      if (shutdown == False):
        print("Attempting to reconnect...")
      else:
        print("Shutting down Websocket connection...")
      await asyncio.sleep(1)


if __name__ == "__main__":
  print("Setting up Kraken BTC...")
  asyncio.run(run(["XBT/USD", "ETH/USD"]))
