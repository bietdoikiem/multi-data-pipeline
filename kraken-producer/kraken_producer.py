import os
import time
from kafka import KafkaProducer
import json
from websocket import create_connection

KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 30))

def run():
  iterator = 0
  print("Setting up Kraken producer at {}".format(KAFKA_BROKER_URL))
  # producer = KafkaProducer(
  #   bootstrap_servers=[KAFKA_BROKER_URL],
  #   # Encode all values as JSON
  #   value_serializer=lambda x: json.dumps(x).encode('utf-8'),
  # )
  # Open websocket connection and subscribe to ticker feed for XBT/USD
  try:
    ws = create_connection(
      "wss://ws.kraken.com/",
    )
    ws.send(
      '{"event": "subscribe", "pair": [ "XBT/USD" ], "subscription": {"name": "ticker"}}',
    )
  except Exception as e:
    print(str(e))
  
  # Infinite loop waiting for WebSocket data
  while True:
    try:
      response = json.loads(ws.recv())
      if (isinstance(response, list)):
        print(response)
    except KeyboardInterrupt:
      print("Closing WebSocket connection by KeyboardInterrupt...")

if __name__ == "__main__":
  print("Setup-ing Kraken...")
  run()