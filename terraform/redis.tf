resource "aws_elasticache_subnet_group" "redis_subnet" {
  name       = "redis-subnet"
  subnet_ids = [aws_subnet.public_subnet.id, aws_subnet.private_subnet.id]
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "audio-proc-redis"
  engine               = "redis"
  node_type            = "cache.t4g.micro"
  num_cache_nodes      = 1
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.redis_subnet.name
  security_group_ids   = [aws_security_group.redis_sg.id]
  parameter_group_name = "default.redis7"
}

