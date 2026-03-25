output "api_url" {
  description = "Public URL of the API load balancer"
  value       = module.ecs.alb_dns_name
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = module.rds.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = module.elasticache.endpoint
  sensitive   = true
}

output "s3_bucket" {
  description = "S3 document vault bucket name"
  value       = module.s3.bucket_name
}

output "ecr_api_url" {
  description = "ECR repository URL for API image"
  value       = module.ecs.ecr_repository_url
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}
