environment        = "prod"
aws_region         = "ca-central-1"
vpc_cidr           = "10.0.0.0/16"
db_name            = "uportai"
db_username        = "uportai"
rds_instance_class = "db.t4g.medium"
redis_node_type    = "cache.t4g.small"
s3_bucket_name     = "uportai-prod-documents"
api_cpu            = 1024
api_memory         = 2048
api_desired_count  = 2

# Fill these in before first deploy:
# db_password              = ""
# api_image                = "<account>.dkr.ecr.ca-central-1.amazonaws.com/uportai-prod-api:latest"
# acm_certificate_arn      = "arn:aws:acm:..."
# anthropic_api_key_ssm_arn = "arn:aws:ssm:..."
# clerk_secret_ssm_arn     = "arn:aws:ssm:..."
# stripe_secret_ssm_arn    = "arn:aws:ssm:..."
