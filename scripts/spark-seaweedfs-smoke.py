def main() -> None:
    from pyspark.sql import SparkSession

    spark = (SparkSession.builder.appName("RetailPulse-SeaweedFS-Spark-Test")
             .config("spark.jars.packages",
                     "org.apache.hadoop:hadoop-aws:3.3.4,"
                     "com.amazonaws:aws-java-sdk-bundle:1.12.262")
             .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:8333")
             .config("spark.hadoop.fs.s3a.access.key", "retailpulse")
             .config("spark.hadoop.fs.s3a.secret.key", "retailpulse_secret")
             .config("spark.hadoop.fs.s3a.path.style.access", "true")
             .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
             .config("spark.hadoop.fs.s3a.impl",
                     "org.apache.hadoop.fs.s3a.S3AFileSystem")
             .getOrCreate())

    frame = spark.createDataFrame(
        [(1, "bronze"), (2, "silver")],
        ["id", "layer"],
    )
    frame.write.mode("overwrite").parquet(
        "s3a://retailpulse/spark-test/parquet",
    )
    count = spark.read.parquet(
        "s3a://retailpulse/spark-test/parquet",
    ).count()
    print(f"Spark S3A row count: {count}")
    spark.stop()


if __name__ == "__main__":
    main()
