variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "app_name" {
  default = "audio-app"
}

variable "task_name" {
  default = "audio-task"
}

variable "domain_name" {
  default = "XXX.xxx"
}

variable "route53_zone_id" {
  default = "XXX"
}

variable "acm_certificate_arn" {
  default = "XXX"
}