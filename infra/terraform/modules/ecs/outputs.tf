output "alb_dns_name"        { value = aws_lb.main.dns_name }
output "cluster_name"        { value = aws_ecs_cluster.main.name }
output "api_service_name"    { value = aws_ecs_service.api.name }
output "worker_service_name" { value = aws_ecs_service.worker.name }
output "ecr_repository_url"  { value = aws_ecr_repository.api.repository_url }
