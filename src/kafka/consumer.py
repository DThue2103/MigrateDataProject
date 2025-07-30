import json
from kafka import KafkaProducer
from kafka import KafkaConsumer
import re
consumer_server1 = KafkaConsumer("DE-ETL103",
                         bootstrap_servers = "localhost:9092")

consumer_server2 = KafkaConsumer("DE-ETL100",
                         bootstrap_servers = "localhost:9092")
#kafka server2
producer_server2 = KafkaProducer(bootstrap_servers="localhost:9092",
                        value_serializer=lambda x: json.dumps(x).encode('utf-8')
                         )

while True:
    #gửi data từ server1 sang server2 (lấy dl từ topic DE-ETL103 gửi đến topic DE-ETL100)
    mgs_pack1 = consumer_server1.poll(timeout_ms=500)
    for tp, messages in mgs_pack1.items():
        for message in messages:
            mgs = message.value.decode("utf-8")
            # print(message.value.decode("utf-8"))

            producer_server2.send("DE-ETL100", mgs)
            producer_server2.flush()

    #validate dữ liệu giữa server1 và server2
    mgs_pack2 = consumer_server2.poll(timeout_ms=500)

    for (tp1, messages1), (tp2, messages2) in zip(mgs_pack1.items(), mgs_pack1.items()):
        for message1, message2 in zip(messages1, messages2):
            mgs1 = message1.value.decode().replace("[","").replace("]", "") + ","
            list_mgs1 = [x.strip() + "}" for x in mgs1.split("},") if x.strip()]
            # for mgs in list_mgs1:
                # print(mgs)
            # print(list_mgs1)
            # print("-------------------")
            mgs2 = message2.value.decode().replace("[","").replace("]", "") + ","
            list_mgs2 = [x.strip() + "}" for x in mgs2.split("},") if x.strip()]
            # print(list_mgs2)

            for ms1 in list_mgs1:
                if ms1 not in list_mgs2:
                    producer_server2.send("DE-ETL100", ms1)
                    producer_server2.flush()

                # else:
                #     print("ok con bò")