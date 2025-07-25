from kafka import KafkaConsumer
from kafka import KafkaProducer
import json
import queue

consumerA = KafkaConsumer("DE-ETL103",
                         bootstrap_servers = "localhost:9092",
                         auto_offset_reset='earliest')

consumerB = KafkaConsumer("DE-ETL100",
                         bootstrap_servers = "localhost:9092",
                         auto_offset_reset='earliest',
                          value_deserializer=lambda x: x.decode('utf-8'))
#kafka B
producer = KafkaProducer(bootstrap_servers="localhost:9092"
                        , value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                         value_deserializer=lambda x: x.decode('utf-8'))

# consA = queue.Queue()
# consB = queue.Queue()

while True:
    mgs_packA = consumerA.poll(timeout_ms=500)
    mgs_packB = consumerB.poll(timeout_ms=500)

    for (tpA, messagesA), (tpB, messagesB) in zip(mgs_packA.items(), mgs_packB.items()):
        for messageA, messageB in zip(messagesA, messagesB):
            mgsA = messageA.value
            mgsB = messageB.value if messageB is not None else None
            if mgsA != mgsB:
                producer.send("DE-ETL100", mgsA)
                producer.flush()

