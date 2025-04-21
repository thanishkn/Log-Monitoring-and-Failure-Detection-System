import time
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, current_timestamp, from_json, when, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
from py4j.protocol import Py4JJavaError
from pyspark.sql.functions import window


# Define schema for incoming Kafka messages
log_schema = StructType([
    StructField("timestamp", TimestampType(), True),
    StructField("service", StringType(), True),
    StructField("log_level", StringType(), True),
    StructField("status_code", IntegerType(), True),
    StructField("response_time", IntegerType(), True),
    StructField("message", StringType(), True)
])

# MySQL connection properties
mysql_properties = {
    "user": "root",
    "password": "", #ENTER PASSWORD HERE
    "driver": "com.mysql.cj.jdbc.Driver"
}

# MySQL table info
mysql_url = "jdbc:mysql://172.25.160.1:3306/LogRecords"
mysql_table = "service_metrics"

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Multi-Service Log Analytics") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,mysql:mysql-connector-java:8.0.28") \
    .getOrCreate()

# Set log level
spark.sparkContext.setLogLevel("ERROR")

# Read from Kafka stream
stream_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "spark_logs") \
    .option("startingOffsets", "latest") \
    .load()

# Parse JSON messages
parsed_df = stream_df \
    .selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", log_schema).alias("data")) \
    .select("data.*")



# Track metrics for ALL services, not just failing ones
# This ensures we track all three services even if they have no errors
service_metrics_df = parsed_df \
    .withWatermark("timestamp", "30 seconds") \
    .groupBy(
        window(col("timestamp"), "30 seconds"),  # Tumbling window
        col("service")
    ).agg(
        count(when((col("log_level") == "ERROR") | 
                  (~col("status_code").between(100, 499)) |
                  (col("response_time") > 3400), 1)).alias("error_count"),
        count("*").alias("total_requests"),
        avg("response_time").alias("avg_response_time")
    )


# Add failure flag and timestamp for all services
# Add failure flag and timestamp for all services
final_df = service_metrics_df \
    .withColumn("error_rate", col("error_count") / col("total_requests") * 100) \
    .withColumn("failure", when(
        (col("error_count") > 5) & (col("error_rate") >= 50),
        lit(True)
    ).otherwise(lit(False))) \
    .withColumn("processed_at", col("window.start")) \
    .drop("window")  # Remove the window column entirely

# Function to write to MySQL
def write_to_mysql(batch_df, batch_id):
    if not batch_df.isEmpty():
        batch_start_time = time.time()
        print(f"Writing batch {batch_id} to MySQL")
        
        # Show results in console - all services with their metrics
        print(f"Batch {batch_id} Data:")
        batch_df.show(truncate=False)

        batch_end_time = time.time()  # End timing the batch
        elapsed = batch_end_time - batch_start_time
        print(f"⏱️ Time taken to process batch {batch_id}: {elapsed:.2f} seconds\n")
        
        try:
            batch_df.write \
                .format("jdbc") \
                .option("url", mysql_url) \
                .option("dbtable", mysql_table) \
                .options(**mysql_properties) \
                .mode("append") \
                .save()
            print(f"Batch {batch_id} successfully written to MySQL")
            batch_df = spark.createDataFrame(spark.sparkContext.emptyRDD(), batch_df.schema)


        except Exception as e:
            print(f"Error writing to MySQL: {str(e)}")
        
        

# Start streaming write
query = final_df.writeStream \
    .foreachBatch(write_to_mysql) \
    .trigger(processingTime="5 seconds") \
    .outputMode("update") \
    .start()

# Keep application running
try:
    print("Spark Streaming job started. Monitoring all services...")
    query.awaitTermination()
except KeyboardInterrupt:
    print("Stopping the streaming job...")
    query.stop()
    print("Job stopped")
finally:
    spark.stop()