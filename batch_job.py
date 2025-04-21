from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, sum, col
import time

# MySQL connection properties
mysql_user = "root"
mysql_password = "" #ENTER PASSWORD HERE

# MySQL table info
mysql_url = "jdbc:mysql://172.25.160.1:3306/LogRecords"
mysql_table = "service_metrics"

def analyze_service_metrics(mysql_url, mysql_user, mysql_password):
    # Start Spark session using Maven package for MySQL connector
    spark = SparkSession.builder \
        .appName("ServiceMetricsAnalysis") \
        .config("spark.jars.packages", "mysql:mysql-connector-java:8.0.28") \
        .getOrCreate()

    # Read from MySQL table via JDBC
    df = spark.read.format("jdbc").options(
        url=mysql_url,
        driver="com.mysql.cj.jdbc.Driver",
        dbtable="service_metrics",
        user=mysql_user,
        password=mysql_password
    ).load()

    batch_start_time = time.time()

    # Compute metrics
    result = df.groupBy("service").agg(
        avg("avg_response_time").alias("total_average_response_time"),
        sum(col("failure").cast("int")).alias("number_of_failures")
    )

    batch_end_time = time.time()  # End timing the batch
    elapsed = batch_end_time - batch_start_time
    print(f"⏱️ Time taken to process batch: {elapsed:.2f} seconds\n")

    # Convert to list of dictionaries
    result_list = [row.asDict() for row in result.collect()]


    # Stop Spark session
    spark.stop()

    return result_list

# Call the function and print the result
print(analyze_service_metrics(mysql_url, mysql_user, mysql_password))
