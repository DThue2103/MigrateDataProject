import json

from kafka import KafkaConsumer

consumer = KafkaConsumer("DE-ETL103",
                         bootstrap_servers = "localhost:9092")
while True:
    mgs_pack = consumer.poll(timeout_ms=500)
    for tp, messages in mgs_pack.items():
        for message in messages:
            print(message.value.decode("utf-8"))
