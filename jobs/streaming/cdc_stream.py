"""Spark Structured Streaming CDC consumer with checkpointed Parquet output."""
import argparse
import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T


def run(bootstrap: str, topic: str, output: str, checkpoint: str) -> None:
    builder = SparkSession.builder.appName("RetailPulse-CDCStreaming")
    builder = (builder
               .config("spark.jars.packages",
                       "org.apache.hadoop:hadoop-aws:3.3.4,"
                       "com.amazonaws:aws-java-sdk-bundle:1.12.262,"
                       "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3")
               .config("spark.hadoop.fs.s3a.endpoint",
                       os.getenv("SEAWEED_S3_ENDPOINT", "http://localhost:8333"))
               .config("spark.hadoop.fs.s3a.access.key",
                       os.getenv("SEAWEED_ACCESS_KEY", "retailpulse"))
               .config("spark.hadoop.fs.s3a.secret.key",
                       os.getenv("SEAWEED_SECRET_KEY", "retailpulse_secret"))
               .config("spark.hadoop.fs.s3a.path.style.access", "true")
               .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
               .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem"))
    spark = builder.getOrCreate()
    schema = T.StructType([
        T.StructField("payload", T.StructType([
            T.StructField("op", T.StringType()),
            T.StructField("ts_ms", T.LongType()),
            T.StructField("after", T.MapType(T.StringType(), T.StringType())),
            T.StructField("before", T.MapType(T.StringType(), T.StringType())),
            T.StructField("source", T.StructType([T.StructField("table", T.StringType())])),
        ]))
    ])
    events = (spark.readStream.format("kafka").option("kafka.bootstrap.servers", bootstrap)
              .option("subscribe", topic).option("startingOffsets", "latest").load())
    parsed = (events.select(F.from_json(F.col("value").cast("string"), schema).alias("event"),
                            F.col("timestamp").alias("ingested_at"))
              .select("event.payload.*", "ingested_at")
              .withColumn("event_date", F.to_date("ingested_at")))
    query = (parsed.writeStream.format("parquet").option("path", output)
             .option("checkpointLocation", checkpoint).partitionBy("event_date")
             .outputMode("append").start())
    query.awaitTermination()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap", default="localhost:9092")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--checkpoint", required=True)
    args = parser.parse_args()
    run(args.bootstrap, args.topic, args.output, args.checkpoint)
