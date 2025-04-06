resource "aws_ecs_cluster" "api_cluster" {
  name = "${var.app_name}-cluster"
}

resource "aws_ecs_task_definition" "api_task" {
  family                   = "${var.app_name}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "4096"
  memory                   = "8192"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name      = var.app_name
      image     = aws_ecr_repository.audio_app_ecr_repo.repository_url
      portMappings = [{
        containerPort = 8000
        protocol      = "tcp"
      }]
      environment = local.common_env_vars
      healthCheck = {
        retries      = 3
        command      = [
          "CMD-SHELL",
          "curl -f http://localhost:8000/healthcheck || exit 1"
        ]
        timeout      = 5
        interval     = 60
        startPeriod  = 0
      }
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-create-group   = "true"
          awslogs-group          = "/ecs/audio-app"
          awslogs-stream-prefix  = "ecs"
          awslogs-region         = var.aws_region
        }
      }
    }
  ])
}

resource "aws_cloudwatch_log_group" "audio_logs" {
  name              = "/ecs/audio-app"
  retention_in_days = 7
}

resource "aws_ecs_service" "audio_service" {
  name            = "${var.app_name}-service"
  cluster         = aws_ecs_cluster.api_cluster.id
  task_definition = aws_ecs_task_definition.api_task.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets         = [aws_subnet.public_subnet.id, aws_subnet.private_subnet.id]
    security_groups = [aws_security_group.audio_app_sg.id]
    assign_public_ip = true
  }


  load_balancer {
    target_group_arn = aws_lb_target_group.audio_tg.arn
    container_name   = var.app_name
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.https_listener]
}
