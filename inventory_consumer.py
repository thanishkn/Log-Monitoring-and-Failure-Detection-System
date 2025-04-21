from kafka import KafkaConsumer, KafkaProducer
import json

# Consumer configuration
CONSUMER_KAFKA_BROKER = 'localhost:9092'
CONSUMER_TOPIC = 'raw-logs-inventory'

# Producer configuration (same localhost, different port)
PRODUCER_KAFKA_BROKER = 'localhost:9092'  # Using a different port to avoid clashes
PRODUCER_TOPIC = 'spark_logs'

# Create Kafka consumer
consumer = KafkaConsumer(
    CONSUMER_TOPIC,
    bootstrap_servers=CONSUMER_KAFKA_BROKER,
    auto_offset_reset='earliest',  # or 'latest'
    enable_auto_commit=True,
    group_id='log-consumer-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Create Kafka producer
producer = KafkaProducer(
    bootstrap_servers=PRODUCER_KAFKA_BROKER,
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print(f"Listening for messages on topic: {CONSUMER_TOPIC}")
print(f"Forwarding messages to: {PRODUCER_TOPIC} on {PRODUCER_KAFKA_BROKER}")

# Consume messages and forward them
for message in consumer:
    log_data = message.value
    print(f"Received log: {log_data}")
    
    # Forward the message to the new topic
    producer.send(PRODUCER_TOPIC, value=log_data)
    producer.flush()  # Ensure the message is sent
    print(f"Forwarded to {PRODUCER_TOPIC}")