-- Create the database (if it doesn't exist)
CREATE DATABASE IF NOT EXISTS LogRecords;

-- Use the database
USE LogRecords;

-- Create the table
CREATE TABLE service_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service VARCHAR(100) NOT NULL,
    error_count INT NOT NULL,
    total_requests INT NOT NULL,
    avg_response_time FLOAT NOT NULL,
    failure BOOLEAN NOT NULL,
    processed_at TIMESTAMP NOT NULL,
    error_rate FLOAT NOT NULL
);

SELECT * FROM service_metrics;
SELECT COUNT(*) FROM service_metrics;

# Drop database LogRecords;
