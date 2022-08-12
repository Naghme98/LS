# This region must match the region where Terraform will build the AMI
variable "region" {
  type    = string
  default = "us-east-1"
}

# This block Creates a formatted timestamp for AMI name uniquness
locals { timestamp = regex_replace(timestamp(), "[- TZ:]", "") }

# Generating a template for the  AMI.
# The source amazon-ebs declares this image will be created in AWS.
source "amazon-ebs" "example" {
  ami_name      = "lab3-LS-course-${local.timestamp}"
  instance_type = "t2.micro"
  region        = var.region
  # Searching for a base AMI with the parameters which are defined in the filters part 
  source_ami_filter {
    filters = {
      name                = "ubuntu/images/*ubuntu-bionic-18.04-amd64-server-*"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    # We need to find this AMI so, we need to search it in someones sources.
    owners      = ["099720109477"]
  }
  ssh_username = "ubuntu"
}

# a build block invokes sources and runs provisioning steps on them.
build {
  sources = ["source.amazon-ebs.example"]
  # copying the key to the image and run your setup script.
  provisioner "file" {
    source      = "../tf-packer.pub"
    destination = "/tmp/tf-packer.pub"
  }
  provisioner "shell" {
    script = "../scripts/setup.sh"
  }
}
