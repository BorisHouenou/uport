variable "environment" {
  description = "Deployment environment (dev | staging | prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be dev, staging, or prod"
  }
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ca-central-1"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "uportai"
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "uportai"
  sensitive   = true
}

variable "db_password" {
  description = "PostgreSQL master password"
  type        = string
  sensitive   = true
}

variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.medium"
}

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t4g.small"
}

variable "s3_bucket_name" {
  description = "S3 bucket for certificates and documents"
  type        = string
}

variable "api_image" {
  description = "ECR image URI for the API container (tag included)"
  type        = string
}

variable "api_cpu" {
  description = "Fargate task CPU units"
  type        = number
  default     = 512
}

variable "api_memory" {
  description = "Fargate task memory (MiB)"
  type        = number
  default     = 1024
}

variable "api_desired_count" {
  description = "Number of API tasks to run"
  type        = number
  default     = 2
}

variable "acm_certificate_arn" {
  description = "ACM certificate ARN for HTTPS"
  type        = string
}

variable "anthropic_api_key_ssm_arn" {
  description = "SSM Parameter Store ARN for ANTHROPIC_API_KEY"
  type        = string
}

variable "clerk_secret_ssm_arn" {
  description = "SSM Parameter Store ARN for CLERK_SECRET_KEY"
  type        = string
}

variable "stripe_secret_ssm_arn" {
  description = "SSM Parameter Store ARN for STRIPE_SECRET_KEY"
  type        = string
}
