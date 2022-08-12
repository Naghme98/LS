# Infrastructure as Code


## Task 1: IaC Theory

Briefly answer for the following questions what is and for what:

- git repository:
    - /.git
    - /.github
    - .gitignore
    - .gitmodules
-----

### Answers:
1. Git uses repository as a file system-based database to have a history of what every change we made. the ".git" folder contains all the information needed for our project like commits, HEAD, remote repository address, logs, etc.
2. It is a location in which some certain GitHub-specific files, such as GitHub Actions workflows or issue templates can be placed.
3. The .gitignore file tells Git which files to ignore when committing the project to the GitHub repository. gitignore is located in the root directory of our repository.
4. We can use other codes from different repositories in our current project as submodules in a way that there is a clear separation between them and reserve the modularity form of the project. To use these submodules, we need to specify the name and address of these modules in the ".gitmodules" file. The .gitmodules file, located in the top-level directory of a Git working tree, is a text file with a syntax matching the requirements of git-config

--------
- ansible directory:
    - ansible.cfg
    - inventory folder
    - roles folder
        - tasks
        - defaults
        - files
        - handlers
        - templates
    - playbooks folder

----------

### Answers:

- ansible directory:
    - ansible.cfg :  The first config where we define the common parameters and paths to inventory and roles files
    - inventory folder: Defines the hosts and groups of hosts upon which commands, modules, and tasks in a playbook operate
    - roles folder
        - tasks: tasks that would normally be defined in the tasks section of a regular Ansible playbook are placed here
        - defaults: setting default variables for included or dependent roles
        - files: Contains static files and script files that might be copied to or executed on a remote server.
        - handlers: Contains a list of tasks that must be executed in response to changes made to the system. there are tasks that are started only once after the successful execution of other tasks, if these tasks have changed something
        - templates: This directory is reserved for templates that will generate files on remote hosts. Templates typically use variables defined on files located in the vars directory, and on host information that is collected at runtime
    - playbooks folder: There are yaml files that combine Inventory, which describes the groups of hosts on which tasks should be executed, with roles that means what should be executed. This is sorted by Deployment environments and then by projects and services. This folder contains Playbooks with the list of hosts it is run on. It can also override default variables of a role and tune some other parameters



----------
- terraform folder:
    - main.tf
    - variables.tf: Consists variable blocks that defining configuration options that can change each time terraform is executed (The primary region, The primary zones, ports, disk size and so on)
    - outputs.tf: Makes shared configuration available for other providers and additional provisioning data
---------


### Answers:

1. The main configuration file where we define the resource definition
2. The file to define our variables
3. This file contains output definitions for our resources

----------

## Task 2: Choose your application/microservices

Base level (it means that this task will be evaluated very meticulously): find (much better to write) a
simple application with REST interface. For example, it could be a web server that returns "Hello
to SNE family! Time is: < current time in Innopolis >". Use whatever programming language that
you want (python, golang, C#, java...).
Semi-Bonus: prepare microservices instead of standalone application, e.g. full stack web application
with web server, database...

--------------


### Implementation:

For this part I wrote a semi-Restful web application with database that user can register and check if he is registered or not. 

if you run the app using "ip:5000/" you can see the pages.

----------

## Task 3: Dockerize your application

1. Build Docker image for your application (make Dockerfile).
Look for the best Docker practices, try to follow them and put into report. 
Bonus: use docker-compose in the case of microservices.
------------


### Implementation:

Because I had to initialize mysql + my webapp, I used a docker-compose file.



![](https://i.imgur.com/zAvagyz.png)
<p align=center>
<i>Figure 1: docker-compose file</i>
</p>



As you can see, there are two services, one with name of "app" and the other one "db". It would expose ports in the format of "host:container" and define that db should run every time (using the entry point) and also in a "RO, Read Only" format.



![](https://i.imgur.com/N3qCDgf.png)    
<p align=center>
<i>Figure 2: Web app Dockerfile</i>
</p>


For the web app, I'll use python as the base image and expose the port 5000 for it and change to the working directory which is /app and copy the requirements file to that directory and use the pip to install them (flask and other needed packages)
Then copy the app.py into that direcory and also the templates which are the html files.
Finally, I'll run the app.py


--------------
## Task 4: Deliver your app using Software Configuration Management

1. Get your personal cloud account. To avoid some payment troubles, take a look on free tier
that e.g. AWS or GCP offers for you (this account type should be fit for a lab).
2. Use Terraform to deploy your required cloud instance.
Look for the best Terraform practices, try to follow them and put into report.
**Bonus:** use Packer to deploy your cloud image/docker container.
--------------

### Implementation: 
For this task, I use my AWS account as the required cloud account.

Packer is HashiCorp's open-source tool for creating machine images from source configuration. Then, Terraform can use the created Packer image to create the instance without manual configuration on the cloud.

- Installing Packer:

```
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install packer
```

- Installing Terraform:

```
sudo apt-get update && sudo apt-get install -y gnupg software-properties-common curl
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install terraform
```
- Creating a user for AWS and Access key for connection:



![](https://i.imgur.com/THpULWS.png)
<p align=center>
<i>Figure 3 :  Creating user </i>
</p>
    
![](https://i.imgur.com/iqrUGBN.png)
<p align=center>
<i>Figure 4 : Creating the group for it</i>
</p>

![](https://i.imgur.com/7EQmrUd.png)
<p align=center>
<i>Figure 5 :  Access key ID and Secret Access key for the created user</i>
</p>
    

- Generating SSH keys for the image:

```
ssh-keygen -t rsa -C "n.mohammadifar@innopolis.university" -f ./tf-packer
```

- Creating a setup script to do some jobs like installing the dependencies and creating a user and ...

```
#!/bin/bash
set -x

# Install necessary dependencies
sudo apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" dist-upgrade
sudo apt-get update
sudo apt-get -y -qq install curl wget git vim apt-transport-https ca-certificates
sudo add-apt-repository ppa:longsleep/golang-backports -y
sudo apt-get -y -qq install golang-go

# Setup sudo to allow no-password sudo for "hashicorp" group and adding "terraform" user
sudo groupadd -r hashicorp
sudo useradd -m -s /bin/bash terraform
sudo usermod -a -G hashicorp terraform
sudo cp /etc/sudoers /etc/sudoers.orig
echo "terraform  ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/terraform

# Installing SSH key
sudo mkdir -p /home/terraform/.ssh
sudo chmod 700 /home/terraform/.ssh
sudo cp /tmp/tf-packer.pub /home/terraform/.ssh/authorized_keys
sudo chmod 600 /home/terraform/.ssh/authorized_keys
sudo chown -R terraform /home/terraform/.ssh
sudo usermod --shell /bin/bash terraform

```


- Creating a file to build the image (AMI):

```
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
```

- Build the Packer image: As you can see, the ami is created successfully.



![](https://i.imgur.com/qQsX98p.png)
    

![](https://i.imgur.com/kqz2NSC.png)    
<p align=center>
<i>Figure 6: Building the image</i>
</p>

![](https://i.imgur.com/6XfT0oO.png)
<p align=center>
<i>Figure 7: Created AMI showin the AWS list of my AMIs</i>
</p>
    


- Using Terafform to deploy the built ami to the aws.

For that, we need to create main.tf file that hold all the configurations for our AWS instance like the open ports, networking, etc.

The most important block of this file is the following block that I had to put the created ami file there.

```
resource "aws_instance" "web" {
  ami                         = "ami-0aa129cdfb7702424"
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.subnet_public.id
  vpc_security_group_ids      = [aws_security_group.sg_22_80.id]
  associate_public_ip_address = true

  tags = {
    Name = "Learn-Packer"
  }

```

- Creating a new file called terraform.tfvars:

```
# Packer image's region
region = "us-east-1"
```

- Initializing and applying:


![](https://i.imgur.com/W1MaDgR.png)
    
![](https://i.imgur.com/cOllcLe.png)  
<p align=center>
<i>Figure 9: Terraform deploying</i>
</p>


- Test if I can use the ssh or not:

    
![](https://i.imgur.com/E4M4xmd.png)
<p align=center>
<i>Figure 10: SSH to the new created instance</i>
</p>
    
    
![](https://i.imgur.com/kkU4Qan.png)
    
![](https://i.imgur.com/DTINIJi.png)
<p align=center>
<i>Figure 11: Showing the information about the created instance in AWS</i>
</p>



- P.S: I forgot to say that, I import the "AWS_ACCESS_KEY_ID" and "AWS_SECRET_ACCESS_KEY" in the system instead of putting them directly in the files.

--------------
3. Choose SCM tool. Suggestions:
    - Ansible (default choice)
    - SaltStack
    - Puppet
    - Chef
    - ...
4. Using SCM tool, write a playbook tasks to deliver your application to cloud instance. Try to
separate your configuration files into **inventory/roles/playbooks** files. In real practice, we almost never use poor playbooks where everything all in one.
Also try to use the best practices for you SCM tool and put them into report.
Use Molecula and Ansible Lint to test your application before to deliver to cloud (or their
equivalents).
--------------


### Implementation:

I used Ansible.

For this part I tried to follow the style of writing in roles instead of just writing in a simple playbook file. This style will increase the modularity and usability of the tasks.
Also I defined the hosts in the inventory folder and in a way that was in the best practices.



![](https://i.imgur.com/5h8iNrP.png) 
<p align=center>
<i>Figure 11: Project structure</i>
</p>
    
![](https://i.imgur.com/rCbdyFm.png)
<p align=center>
<i>Figure 12:  playbook.yml</i>
</p>


Figure 12: in this file we will define that on which host this tasks should run and then which roles to be called also I defined the vars folder.

The roles/apt/tasks/main.yml is simple downloading packages using apt and roles/docker/tasks/main.yml just download and initialize the docker (I didn't put the codes here, you can see them in the repository)

The "web" (figure 14) will clone the repository (In that time I didn't add the terraform,ansible,packer files there, so it was logical) and run the docker-compose file. At the end we are able to access the web app.

p.s: I forgot to add the port 5000 as an ingress in the terraform step and I had to open it manually.

Also, I used the ansible-lint to test my playbook with the following command:

```
ansible-lint playbook.yml
```



![](https://i.imgur.com/u1RP16G.png)
<p align=center>
<i>Figure 13: web tasks</i>
</p>
    
    
![](https://i.imgur.com/LOK22qE.png)    
<p align=center>
<i>Figure 14: Test the web app</i>
</p>



