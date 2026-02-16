packer {
  required_plugins {
    amazon = {
      version = ">= 1.0.0"
      source  = "github.com/hashicorp/amazon"
    }
    googlecompute = {
      version = ">= 1.0.0"
      source  = "github.com/hashicorp/googlecompute"
    }
  }
}

source "amazon-ebs" "webapp" {
  ami_name      = "webapp-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"
  instance_type = var.aws_instance_type
  region        = var.aws_region
  ami_users     = var.aws_ami_users

  source_ami_filter {
    filters = {
      name                = "ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["099720109477"]
  }

  ssh_username = var.aws_ssh_username

  launch_block_device_mappings {
    device_name           = "/dev/sda1"
    volume_size           = 25
    volume_type           = "gp2"
    delete_on_termination = true
  }
}

source "googlecompute" "webapp" {
  project_id          = var.gcp_project_id
  source_image_family = var.gcp_source_image_family
  ssh_username        = var.gcp_ssh_username
  zone                = var.gcp_zone
  image_name          = "webapp-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"
  image_family        = "webapp"
  disk_size           = 25
  disk_type           = "pd-balanced"
}

build {
  sources = [
    "source.amazon-ebs.webapp",
    "source.googlecompute.webapp"
  ]

  provisioner "file" {
    source      = var.app_artifact
    destination = "/tmp/webapp.zip"
  }

  provisioner "file" {
    source      = "systemd/webapp.service"
    destination = "/tmp/webapp.service"
  }

  provisioner "shell" {
    script = "packer/scripts/setup.sh"
  }

  provisioner "shell" {
    inline = [
      "sudo apt-get install -y unzip",
      "sudo unzip /tmp/webapp.zip -d /opt/webapp/",
      "sudo chown -R csye6225:csye6225 /opt/webapp",
      "cd /opt/webapp && sudo -u csye6225 /opt/webapp/venv/bin/pip install -r requirements.txt"
    ]
  }

  provisioner "shell" {
    inline = [
      "sudo mv /tmp/webapp.service /etc/systemd/system/webapp.service",
      "sudo chown root:root /etc/systemd/system/webapp.service",
      "sudo chmod 644 /etc/systemd/system/webapp.service",
      "sudo systemctl daemon-reload",
      "sudo systemctl enable webapp.service"
    ]
  }

  provisioner "shell" {
    inline = [
      "sudo rm -f /tmp/webapp.zip",
      "sudo apt-get clean"
    ]
  }
}
