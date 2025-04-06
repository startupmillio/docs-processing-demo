resource "aws_ecs_task_definition" "celery_task" {
  family                   = "celery-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "4096"
  memory                   = "8192"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name      = "celery-worker"
      image     = aws_ecr_repository.audio_task_ecr_repo.repository_url
      command   = ["celery", "-A", "tasks.transcribe_audio", "worker", "--loglevel=info"]
      environment = local.common_env_vars
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = "/ecs/celery"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "celery_worker" {
  name            = "celery-worker"
  cluster         = aws_ecs_cluster.api_cluster.id
  task_definition = aws_ecs_task_definition.celery_task.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  network_configuration {
    subnets         = [aws_subnet.public_subnet.id, aws_subnet.private_subnet.id]
    security_groups = [aws_security_group.audio_app_sg.id]
    assign_public_ip = true
  }

  depends_on = [aws_ecs_task_definition.celery_task]
}


resource "aws_cloudwatch_log_group" "celery_logs" {
  name              = "/ecs/celery"
  retention_in_days = 7
}


resource "aws_appautoscaling_target" "celery_scaling_target" {
  max_capacity       = 2
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.api_cluster.name}/${aws_ecs_service.celery_worker.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}


resource "aws_appautoscaling_policy" "celery_cpu_policy" {
  name               = "scale-on-cpu"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.celery_scaling_target.resource_id
  scalable_dimension = aws_appautoscaling_target.celery_scaling_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.celery_scaling_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }

    target_value       = 50.0   # если CPU > 50%, масштабировать
    scale_in_cooldown  = 60
    scale_out_cooldown = 60
  }
}

