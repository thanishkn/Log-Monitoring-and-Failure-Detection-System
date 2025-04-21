from kafka import KafkaProducer
import json
from datetime import datetime
import time
import random

KAFKA_BROKER = 'localhost:9092'
TOPIC = 'raw-logs-auth'
SERVICE_NAME = 'auth-service'
ERROR_MODE = True  # Toggle for error/noise

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Status codes
status_codes_positive = [200, 201, 400, 404]
status_codes_errors = [401, 403, 500, 502, 503, 504]

messages = {
    200: "Request completed successfully.",
    201: "Resource created successfully.",
    400: "Bad request from client.",
    401: "Unauthorized access attempt.",
    403: "Forbidden request.",
    404: "Requested resource not found.",
    500: "Internal server error occurred.",
    502: "Bad gateway response.",
    503: "Service temporarily unavailable.",
    504: "Gateway timeout occurred."
}

log_levels = {
    200: "INFO",
    201: "INFO",
    400: "WARN",
    401: "WARN",
    403: "WARN",
    404: "WARN",
    500: "ERROR",
    502: "ERROR",
    503: "ERROR",
    504: "ERROR"
}

def generate_log(log_number):
    code = random.choice(status_codes_positive)
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": SERVICE_NAME,
        "log_level": log_levels[code],
        "status_code": code,
        "response_time": random.randint(50, 500),
        "message": f"{messages[code]} (log #{log_number})"
    }

def generate_log_with_errors(log_number):
    code = random.choice(status_codes_errors)
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": SERVICE_NAME,
        "log_level": log_levels[code],
        "status_code": code,
        "response_time": random.randint(800, 1500),
        "message": f"{messages[code]} (log #{log_number})"
    }

# Send 5 logs per second
if __name__ == "__main__":
    log_count = 1
    try:
        while True:
            start_time = time.time()
            for _ in range(5):  # Send 5 logs in one second
                log = generate_log_with_errors(log_count) if ERROR_MODE else generate_log(log_count)
                if log_count % 20 == 0:
                    log = generate_log_with_errors(log_count) if not ERROR_MODE else generate_log(log_count)
                producer.send(TOPIC, log)
                print(f"[{SERVICE_NAME}] Sent log #{log_count}: {log['status_code']} - {log['log_level']}")
                log_count += 1
            elapsed = time.time() - start_time
            time.sleep(max(0, 1.0 - elapsed))  # Sleep for remainder of the second
    except KeyboardInterrupt:
        print(f"\n[{SERVICE_NAME}] Stopped sending logs.")
        producer.flush()
