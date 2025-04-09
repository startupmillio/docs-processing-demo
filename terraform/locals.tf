locals {
  common_env_vars = [
    { name = "ENV_FOR_DYNACONF", value = "default" },
    {
      name  = "REDIS_HOST"
      value = aws_elasticache_cluster.redis.cache_nodes[0].address
    },
    {
      name  = "DYNACONF_API_URL"
      value = "https://${var.domain_name}"
    },
    {
      name  = "DYNACONF_DATABASE_HOST",
      value = "${aws_db_instance.postgres_db.address}"
    },
    {
      name  = "DYNACONF_DATABASE_DB",
      value = "${aws_db_instance.postgres_db.db_name}"
    },
    {
      name  = "DYNACONF_DATABASE_USER",
      value = "${aws_db_instance.postgres_db.username}"
    },
    {
      name  = "DYNACONF_DATABASE_PASSWORD",
      value = "${aws_db_instance.postgres_db.password}"
    },
    {
      name  = "DYNACONF_OPENAI_API_KEY",
      value = "XXX"
    },
    {
      name  = "DYNACONF_AUTH0_DOMAIN"
      value = "XXX.com"
    },
    {
      name  = "DYNACONF_AUTH0_CLIENT_ID",
      value = "XXX"
    },
    {
      name  = "DYNACONF_AUTH0_CLIENT_SECRET",
      value = "XXX"
    },
    {
      name  = "DYNACONF_AWS_REGION",
      value = var.aws_region
    },
    {
      name  = "DYNACONF_AWS_S3_BUCKET",
      value = "XXX"
    },
    {
      name  = "DYNACONF_ACCESS_KEY_ID",
      value = "XXX"
    },
    {
      name  = "DYNACONF_ACCESS_SECRET_KEY",
      value = "XXX"
    },
    {
      name  = "DYNACONF_AUTH_SECRET",
      value = "some_test_auth_secret"
    },
    {
      name  = "DYNACONF_BROKER_URL"
      value = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:${aws_elasticache_cluster.redis.cache_nodes[0].port}"
    }
  ]
}