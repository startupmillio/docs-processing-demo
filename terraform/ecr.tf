resource "aws_ecr_repository" "audio_app_ecr_repo" {
  name = "audio-proc/api"
}

resource "aws_ecr_repository" "audio_task_ecr_repo" {
  name = "audio-proc/task"
}
