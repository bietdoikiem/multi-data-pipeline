from datetime import datetime
import sys
import signal
import os
from kafka import KafkaProducer
import ujson
from websocket import create_connection

KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 30))


def timeoutfunction(signalnumber, frame):
  raise KeyboardInterrupt


signal.signal(signal.SIGALRM, timeoutfunction)


def reformat_response(res):
  value_info = res[1]
  return {
      "timestamp": value_info[0],
      "open": value_info[2],
      "high": value_info[3],
      "low": value_info[4],
      "close": value_info[5],
      "volume": value_info[7],
      "pair": res[3]
  }


def in_range(number, low, high):
  return low <= number <= high


def run(pair, interval):
  print("Setting up Kraken producer at {}".format(KAFKA_BROKER_URL))
  producer = KafkaProducer(
      bootstrap_servers=[KAFKA_BROKER_URL],
    # Encode all values as JSON
      value_serializer=lambda x: ujson.dumps(x).encode('utf-8'),
  )
  # Open websocket connection and subscribe to ticker feed for XBT/USD
  try:
    ws = create_connection("wss://ws.kraken.com",)
  except Exception as error:
    print("Websocket connection failed (%s)" % error)
    sys.exit(1)

  # Send subscription request
  try:
    ws.send(
        ujson.dumps({
            "event": "subscribe",
            "pair": [pair],
            "subscription": {
                "interval": interval,
                "name": "ohlc"
            }
        }))
  except Exception as error:
    print("WebSocket subscription/request failed (%s)" % error)
    ws.close()
    sys.exit(1)

  print("Waiting for Kraken BTC/USD data...")
  # Infinite loop waiting for WebSocket data
  while True:
    try:
      response = ws.recv()
      response = ujson.loads(response)
      if (isinstance(response, list)):
        producer.send(TOPIC_NAME, value=reformat_response(response))
        print("OHLC at", response[1][0], "sent")
    except KeyboardInterrupt:
      print("Closing WebSocket connection by KeyboardInterrupt...")
      ws.close()
      sys.exit(1)
    except Exception as error:
      print("Websocket failed (%s)" % error)
      sys.exit(1)


if __name__ == "__main__":
  print("Setup-ing Kraken...")
  run("XBT/USD", 1)
