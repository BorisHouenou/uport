variable "environment"            { type = string }
variable "aws_region"             { type = string }
variable "vpc_id"                 { type = string }
variable "public_subnet_ids"      { type = list(string) }
variable "private_subnet_ids"     { type = list(string) }
variable "task_execution_role"    { type = string }
variable "task_role"              { type = string }
variable "api_image"              { type = string }
variable "api_cpu"                { type = number; default = 512 }
variable "api_memory"             { type = number; default = 1024 }
variable "api_desired_count"      { type = number; default = 2 }
variable "database_url"           { type = string; sensitive = true }
variable "redis_url"              { type = string; sensitive = true }
variable "s3_bucket"              { type = string }
variable "certificate_arn"        { type = string }
variable "anthropic_api_key_arn"  { type = string }
variable "clerk_secret_arn"       { type = string }
variable "stripe_secret_arn"      { type = string }
