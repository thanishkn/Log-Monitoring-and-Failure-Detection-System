#!/bin/bash

# Trap Ctrl+C (SIGINT) to stop all child processes
trap 'echo "Stopping all producers..."; kill $auth_pid $inventory_pid $payment_pid; exit' SIGINT

echo "Starting auth producer..."
python3 auth_producer.py &
auth_pid=$!

echo "Starting inventory producer..."
python3 inventory_producer.py &
inventory_pid=$!

echo "Starting payment producer..."
python3 payment_producer.py &
payment_pid=$!

# Wait for all background jobs to finish
wait
