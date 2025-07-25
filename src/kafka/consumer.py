import json

from kafka import KafkaProducer
from kafka import KafkaConsumer

consumer = KafkaConsumer("DE-ETL103",
                         bootstrap_servers = "localhost:9092")

#kafka B
producer = KafkaProducer(bootstrap_servers="localhost:9092"
                        , value_serializer=lambda x: json.dumps(x).encode('utf-8')
                         )
while True:
    mgs_pack = consumer.poll(timeout_ms=500)
    for tp, messages in mgs_pack.items():
        for message in messages:
            # mgs = message.value.decode("utf-8")
            producer.send("DE-ETL100", message)
            producer.flush()

