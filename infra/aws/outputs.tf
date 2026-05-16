output "bucket_name" {
  value       = aws_s3_bucket.risk_lake.bucket
  description = "Provisioned S3 bucket for bronze/silver/gold lakehouse objects."
}
