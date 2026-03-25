terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  backend "s3" {
    # Override per environment:
    #   terraform init -backend-config=environments/prod/backend.hcl
    bucket         = "uportai-terraform-state"
    key            = "uportai/terraform.tfstate"
    region         = "ca-central-1"
    encrypt        = true
    dynamodb_table = "uportai-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "uportai"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# ── Modules ───────────────────────────────────────────────────────────────────

module "vpc" {
  source      = "./modules/vpc"
  environment = var.environment
  vpc_cidr    = var.vpc_cidr
}

module "iam" {
  source      = "./modules/iam"
  environment = var.environment
  s3_bucket   = var.s3_bucket_name
}

module "s3" {
  source      = "./modules/s3"
  environment = var.environment
  bucket_name = var.s3_bucket_name
}

module "rds" {
  source              = "./modules/rds"
  environment         = var.environment
  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  db_name             = var.db_name
  db_username         = var.db_username
  db_password         = var.db_password
  instance_class      = var.rds_instance_class
}

module "elasticache" {
  source             = "./modules/elasticache"
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  node_type          = var.redis_node_type
}

module "ecs" {
  source                = "./modules/ecs"
  environment           = var.environment
  aws_region            = var.aws_region
  vpc_id                = module.vpc.vpc_id
  public_subnet_ids     = module.vpc.public_subnet_ids
  private_subnet_ids    = module.vpc.private_subnet_ids
  task_execution_role   = module.iam.task_execution_role_arn
  task_role             = module.iam.task_role_arn
  api_image             = var.api_image
  api_cpu               = var.api_cpu
  api_memory            = var.api_memory
  api_desired_count     = var.api_desired_count
  database_url          = "postgresql+asyncpg://${var.db_username}:${var.db_password}@${module.rds.endpoint}/${var.db_name}"
  redis_url             = "redis://${module.elasticache.endpoint}:6379/0"
  s3_bucket             = var.s3_bucket_name
  certificate_arn       = var.acm_certificate_arn
  anthropic_api_key_arn = var.anthropic_api_key_ssm_arn
  clerk_secret_arn      = var.clerk_secret_ssm_arn
  stripe_secret_arn     = var.stripe_secret_ssm_arn
}
