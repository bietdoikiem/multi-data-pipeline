from datetime import datetime
import os
from kafka import KafkaProducer
import ujson
from websocket import create_connection

KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 30))


def reformat_response(res):
  value_info = res[1]
  ask_price = value_info['a'][0]
  return {"ask_price": ask_price, "datetime": datetime.utcnow().timestamp()}


def run():
  iterator = 0
  print("Setting up Kraken producer at {}".format(KAFKA_BROKER_URL))
  producer = KafkaProducer(
      bootstrap_servers=[KAFKA_BROKER_URL],
    # Encode all values as JSON
      value_serializer=lambda x: ujson.dumps(x).encode('utf-8'),
  )
  # Open websocket connection and subscribe to ticker feed for XBT/USD
  try:
    ws = create_connection("wss://ws.kraken.com/",)
    ws.send(
        '{"event": "subscribe", "pair": [ "XBT/USD" ], "subscription": {"name": "ticker"}}',
    )
  except Exception as e:
    print(str(e))

  print("Waiting for Kraken BTC/USD data...")
  # Infinite loop waiting for WebSocket data
  while True:
    try:
      response = ujson.loads(ws.recv())
      if (isinstance(response, list)):
        producer.send(TOPIC_NAME, value=reformat_response(response))
        iterator += 1
        print("Ticker no.", iterator, "sent")
    except KeyboardInterrupt:
      print("Closing WebSocket connection by KeyboardInterrupt...")


if __name__ == "__main__":
  print("Setup-ing Kraken...")
  run()
