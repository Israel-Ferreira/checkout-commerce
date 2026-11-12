from aiokafka import AIOKafkaProducer

from typing import Dict, Any

import os

import json

class KafkaClient:

    def __init__(self):
        self._producer: AIOKafkaProducer | None =  None
        self._bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS")



    async def startup(self):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            compression_type="gzip",
            acks="all"
        )


        await self._producer.start()


    async def shutdown(self):
        if self._producer:
            await self._producer.stop()


    async def publish(self, topic: str, value: Dict[str, Any], key: str = None):
        if not self._producer:
            raise RuntimeError("Kafka Producer is not started.")

        await self._producer.send_and_wait(topic, value=value, key=key)



kafka_client = KafkaClient()

async def get_kafka_client() -> KafkaClient:
    return kafka_client
    

