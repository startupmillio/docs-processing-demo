resource "aws_security_group" "alb_sg" {
  name   = "alb-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}



# Application Load Balancer
resource "aws_lb" "audio_alb" {
  name               = "audio-alb"
  load_balancer_type = "application"
  subnets            = [
    aws_subnet.public_subnet.id, aws_subnet.private_subnet.id
  ]
  security_groups    = [aws_security_group.alb_sg.id]
}

# Target Group
resource "aws_lb_target_group" "audio_tg" {
  name        = "audio-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/healthcheck"
    interval            = 45
    unhealthy_threshold = 3
  }
  tags = {
    Name = "api-target-group"
  }
  target_health_state {
    enable_unhealthy_connection_termination = false
  }
}

resource "aws_lb_listener" "https_listener" {
  load_balancer_arn = aws_lb.audio_alb.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = var.acm_certificate_arn  # Make sure you define this variable

  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.audio_tg.arn
  }
}


resource "aws_lb_listener" "une_app" {
  load_balancer_arn = aws_lb.audio_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}


resource "aws_security_group_rule" "alb_to_fargate" {
  type                     = "ingress"
  from_port                = 8000
  to_port                  = 8000
  protocol                 = "tcp"
  security_group_id        = aws_security_group.audio_app_sg.id
  source_security_group_id = aws_security_group.alb_sg.id
}