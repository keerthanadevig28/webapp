
variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "aws_source_ami" {
  type    = string
  default = "ami-0e2c8caa4b6378d8c"
}

variable "aws_instance_type" {
  type    = string
  default = "t2.micro"
}

variable "aws_ssh_username" {
  type    = string
  default = "ubuntu"
}

variable "aws_ami_users" {
  type    = list(string)
  default = []
}

variable "gcp_project_id" {
  type    = string
  default = ""
}

variable "gcp_zone" {
  type    = string
  default = "us-east1-b"
}

variable "gcp_source_image_family" {
  type    = string
  default = "ubuntu-2404-lts-amd64"
}

variable "gcp_ssh_username" {
  type    = string
  default = "ubuntu"
}

variable "gcp_image_project" {
  type    = string
  default = ""
}

variable "app_artifact" {
  type    = string
  default = "webapp.zip"
}
