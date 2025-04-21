#!/bin/bash

# Trap Ctrl+C (SIGINT) to stop all child processes
trap 'echo "Stopping all consumers..."; kill $auth_server_pid $inventory_server_pid $payment_server_pid; exit' SIGINT

echo "Starting auth consumer..."
python3 auth_consumer.py &
auth_server_pid=$!

echo "Starting inventory consumer..."
python3 inventory_consumer.py &
inventory_server_pid=$!

echo "Starting payment consumer..."
python3 payment_consumer.py &
payment_server_pid=$!

# Wait for all background jobs to finish
wait
