resource "aws_db_subnet_group" "default" {
  name       = "audio-db-subnet-group"
  subnet_ids = [aws_subnet.private_subnet.id, aws_subnet.public_subnet.id]
}

resource "aws_db_instance" "postgres_db" {
  allocated_storage      = 20
  storage_type           = "gp2"
  engine                 = "postgres"
  engine_version         = "17.2"
  instance_class         = "db.t4g.micro"
  db_name                = "une"
  username               = "postgres"
  password               = "postgres"
  skip_final_snapshot    = false
  final_snapshot_identifier = "audio-final-snapshot"
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.default.name

  deletion_protection = true

  identifier          = "audio-proc"

  # lifecycle {
  #   prevent_destroy = true
  # }
}
