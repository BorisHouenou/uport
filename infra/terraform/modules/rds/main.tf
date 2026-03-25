resource "aws_db_subnet_group" "main" {
  name       = "uportai-${var.environment}"
  subnet_ids = var.private_subnet_ids
  tags       = { Name = "uportai-${var.environment}-db-subnet-group" }
}

resource "aws_security_group" "rds" {
  name        = "uportai-${var.environment}-rds"
  description = "Allow PostgreSQL from ECS tasks"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_parameter_group" "main" {
  name   = "uportai-${var.environment}-pg16"
  family = "postgres16"

  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements,vector"
  }
}

resource "aws_db_instance" "main" {
  identifier              = "uportai-${var.environment}"
  engine                  = "postgres"
  engine_version          = "16.3"
  instance_class          = var.instance_class
  allocated_storage       = 20
  max_allocated_storage   = 100
  storage_type            = "gp3"
  storage_encrypted       = true
  db_name                 = var.db_name
  username                = var.db_username
  password                = var.db_password
  db_subnet_group_name    = aws_db_subnet_group.main.name
  vpc_security_group_ids  = [aws_security_group.rds.id]
  parameter_group_name    = aws_db_parameter_group.main.name
  multi_az                = var.environment == "prod"
  deletion_protection     = var.environment == "prod"
  skip_final_snapshot     = var.environment != "prod"
  backup_retention_period = var.environment == "prod" ? 7 : 1
  apply_immediately       = true
  tags                    = { Name = "uportai-${var.environment}" }
}
