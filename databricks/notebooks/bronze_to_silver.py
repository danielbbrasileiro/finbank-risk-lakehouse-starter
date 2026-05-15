# Databricks notebook source
# FinBank Risk Lakehouse - Bronze to Silver transformation

from pyspark.sql import functions as F

bronze_path = "s3://finbank-risk-lake/bronze/transactions/"
silver_path = "s3://finbank-risk-lake/silver/transactions/"

df = (
    spark.read.format("parquet")
    .load(bronze_path)
)

silver = (
    df
    .dropDuplicates(["transaction_id"])
    .withColumn("transaction_date", F.to_date("transaction_date"))
    .withColumn("amount", F.col("amount").cast("decimal(18,2)"))
    .withColumn("ingestion_processed_at", F.current_timestamp())
)

(
    silver.write
    .format("delta")
    .mode("overwrite")
    .save(silver_path)
)
