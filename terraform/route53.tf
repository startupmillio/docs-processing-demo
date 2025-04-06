resource "aws_route53_record" "une_dns" {
  zone_id = var.route53_zone_id  # Your Route 53 Hosted Zone ID
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_lb.audio_alb.dns_name
    zone_id                = aws_lb.audio_alb.zone_id
    evaluate_target_health = true
  }
}
