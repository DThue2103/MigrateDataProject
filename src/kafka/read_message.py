from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'repo-change-log',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',  # hoặc 'latest' nếu chỉ muốn message mới
    enable_auto_commit=True,
    group_id='test-consumer-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("----Waiting for messages----")

for message in consumer:
    print(f"----Received message: {message.value}-----")
