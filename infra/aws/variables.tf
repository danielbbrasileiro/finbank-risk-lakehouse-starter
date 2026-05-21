variable "aws_region" {
  description = "AWS region for the demo data lake."
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Globally unique S3 bucket name for the risk lake demo."
  type        = string
}

variable "environment" {
  description = "Environment label used for tagging."
  type        = string
  default     = "portfolio-demo"
}

variable "demo_object_retention_days" {
  description = "Number of days to retain demo data objects before automatic cleanup."
  type        = number
  default     = 7
}
