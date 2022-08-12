## Task 1: Choose Container Engine & Orchestration

1. Choose a container engine. Some suggestions:
    - Docker (default choice)
    - Singularity
    - chroot
    - OpenVZ / Virtuozzo
    - other exotic choices (be sure that you will be available to deal with it and firstly discuss with TA)

Deploy a true container cluster farm, across several team machines. It is however recommended to proceed in a virtual machine environments so the worker nodes can have the exact same system patch level (which makes it easier).
**Bonus:** if you choose Docker, play with alternate storage drivers e.g. BTRFS or ZFS instead of OverlayFS.


### Implementation:

1. I chose docker and installed it on all the nodes and master through the following commands.


```
sudo apt-get update

sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
    
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg


echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null


sudo apt-get install docker-ce docker-ce-cli containerd.io
```

I created 3 virtual machines with kvm and used one as master and the other two as worker.

---------------

2. Сhoose an orchestration engine then:
    - Docker Swarm
    - Kubernetes or local k8s cluster:
        - minikube: works on all major operating systems and uses providers like Docker,Virtualbox and KVM to power the node
        - k3s: lightweight Kubernetes can work on Linux (WSL2 should also work steps here)
        - MicroK8s: lightweight Kubernetes compatible with Ubuntu (Linux) distribution (can work with MacOS and Windows when using mutlipass?).
    - Rancher (advanced)
    - other exotic choices (be sure that you will be available to deal with it and firstly discuss with TA)



### Implementation:

For this one, I will go on with Docker Swarm

```
#Add manager:
docker swarm init --advertise-addr 10.1.1.86

# Add worker:
docker swarm join --token SWMTKN-1-1doqcuhj4hfbp9w4l74hgcyee510csk4f4qnfhzja30a7veyzz-93bicglqb0f1x33alz1uvpaih 10.1.1.86:2377
```
I add two workers to my cluster as you can see in figure 3.

    
![](https://i.imgur.com/Q1Nf1pm.png)
<p align = "center">
  <i>Figure 1: Add docker swarm master</i>
 </p>

![](https://i.imgur.com/p8AzO4D.png)
<p align = "center">
  <i>Figure 2: Add worker    </i>
 </p>
    
![](https://i.imgur.com/0aLmgqc.png)
<p align = "center">
  <i>Figure 3: Available nodes in the cluster</i>
 </p>
    


-------------

3. Analyze and describe the best practices of usage the chosen container engine


Docker Engine is an open-source containerization technology for building and containerizing applications. It works as a client-server application. It can be used to easily deployment of services on the cloud, create predictable environments that are isolated from other apps, mobility, fast deployment, etc.
Docker Engine supports the tasks and workflows involved to build, shipping, and run container-based applications. The engine creates a server-side daemon process that hosts images, containers, networks, and storage volumes.



## Task 2: Distributing an Application/Microservices

Base level (it means that this task will be evaluated very meticulously): deploy at least a simple application (e.g. a simple web page showing the hostname of the host node it is running upon) and validate that its instances are spreading across the farm. It is literally not necessary to create your own service/application: you can use something from a public repository, for example, from
DockerHub. However, no one forbids you to work with self-written projects.

Hint: creating such application is particularly easy to achieve with Swarm when the nodes does not share storage. Same goes for K8s, but you need use a workaround e.g. volumes with hostPath.

**Semi-Bonus 1**: deploy a microservices instead of standalone application, e.g. full stack web application
with web server, database...
**Bonus 2**: use Veewee/Vargant to build and distribute your development environment.
**Bonus 3**: if you use k8s, prepare a helm chart for your application.




### Implementation:

I used microservice for this part. From the docker hub, I found a project called "doctors office management system" with three images, and I wrote a docker-compose.yml file to manage them as a single application. Also, I used one image to give me a visualization of this cluster.

In this file, I defined each image with a name (doctor_panel, patient_paner, and authentication). Then for testing, I tried to tell the swarm that I want two deployments (instances) for two of these images and one for the docter_panel. For the Visualizer part, I said it should run on the manager node, not the workers.



![](https://i.imgur.com/G1Nqf1V.png)
<p align = "center">
  <i>Figure 4: Yml file</i>
 </p>



Then I should create a stack and push this file inside it.

A definition for stack:
- Stack: Docker Stacks occur when a Swarm Manager is managing multiple Swarms for multiple Services, on a given Cluster, for a given application; hence the difference between a Swarm and a Stack is that a Swarm simply applies to a single Service, whereas a Stack manages multiple Swarms and hence multiple Services




```
#We should be in a same directory as our .yml file is there.
docker-compose push
```
Then : 

```
docker stack deploy --compose-file docker-compose.yml test_stack
```

It will create the services and spread the instances through our cluster.



![](https://i.imgur.com/UHbWiiR.png)
<p align = "center">
  <i>Figure 5: Deploy services</i>
 </p>

![](https://i.imgur.com/UzKwg88.png)
<p align = "center">
  <i>Figure 6: Instance spreading through the cluster</i>
 </p>
    
    
![](https://i.imgur.com/nMM7b7U.png)
<p align = "center">
  <i>Figure 7: Validate the services</i>
 </p>
    


## Task 3: Validation

Validate that when a node goes down a new instance is launched. Show how the redistribution of
the instances can happen when the broken node comes back alive. Describe all steps of tests in
your report in details



### Implementation:

We can make a node Availability to change from "Active" to "Drain" and see what will happen.

```
docker node update --availability drain <NODE-ID>
```
As you can see in figure 9, the tasks on node 2, are divided on the Manager and Worker2.




![](https://i.imgur.com/XRdjjJN.png)
<p align = "center">
  <i>Figure 8: Change node avilability</i>
 </p>
    
![](https://i.imgur.com/CrifDt4.png)
<p align = "center">
  <i>Figure 9: Cluster changes after one node off </i>
 </p>       



Then to make it alive:

```
docker node update --availability active <NODE-ID>
```
But, there is no auto-rebalancing in the swarm. That means, when we join a new node to the cluster, it won't stop the services which are already running and redistribute everything (It is understandable.  If I were to add a new node, I don't necessarily want a bunch of other containers stopped, and new ones created on my new node. Swarm only stops containers from "move" replicas when it has to (in replicated mode))

So, to rebalance everything again, I used the following command (it will restart all the services)

p.s: I changed the docker-compose.yml file a little that will only run the doctor_panel, authentication, patient_panel on the worker nodes.

```
 docker service ls -q > dkr_svcs && for i in `cat dkr_svcs`; do docker service update "$i" --detach=false --force ; done
```
    
![](https://i.imgur.com/aThukLl.png)
<p align = "center">
  <i>Figure 10: Before disabling a node</i>
 </p>
    
![](https://i.imgur.com/9f8yppQ.png)    
<p align = "center">
  <i>Figure 11: After diabling a node</i>
 </p>
    
![](https://i.imgur.com/X73pSWT.png)  
<p align = "center">
  <i>Figure 12: After turning back the node and restart the services    </i>
 </p>


## Task 4: Load-balancing

1. Choose a load-balancing facility, which will be installed and tested against your orchestrator. You can choose either l3 or l7 solutions. The disadvantage of layer-3 is that web sessions may break against statefull applications. There is a trick to deal with that, though, for example with OpenBSD Packet Filter.

Note: for K8S, you can try to do Ingress.


2. Choose a load-balancer to distribute the load to the worker nodes, for example either layer 3:
    - layer-3 BSD pf / npf / ipfilter/ipnat
    - layer-3 Linux Netfilter ( iptables )
    - layer 3 Linux nftables ( nft )
    - layer-3+7 HAProxy 
     
    or HTTP reverse-proxy:
    - layer 7 NGINX / NGINX Plus (dynamic objects?)
    - layer 7 Apache Traffic Server? (static objects?)
    - layer 7 OpenBSD Relayd
    - K8S Ingress / Ingress-NGINX
    
3. Swarm or K8S’s network overlay is already spreading the requests among the farm, right? So why would a load-balancer still be needed? Explain and show briefly how a real-life network architecture look like with a small diagram.



### Implementation:

For this part, I realized that I need to see an IP address that would tell me if I am everything is right or not.

So, I created two flask apps and print the socket IP address (I couldn't find a way to print the actual IP address of the machine that is answering the request -- I mean the node) Then I created a docker file to create an Nginx service and also wrote the Nginx.conf file to allow the proxy. I wanted to use the NGINX Plus but they didn't send me the activation link to get the public, private certificate to use it. I also push the images into the docker hub and used them in my docker-compose file.

The other problem I faced, was I wanted to have two locations "/app1" and "/app2" and two proxy binding but it all said it cannot find the /app1 e.g on the server (I couldn't understand why) so I applied it only for 1 service.

In summary, the Nginx will receive all the requests and based on what address we set, will send our requests to that server.



![](https://i.imgur.com/4tAQri4.png)
<p align = "center">
  <i>Figure 13: Nginx.conf</i>
 </p>

![](https://i.imgur.com/aMrXTYr.png)
<p align = "center">
  <i>Figure 14: New services</i>
 </p>
    
![](https://i.imgur.com/kSjlw6s.png)
<p align = "center">
  <i>Figure 15: After applying the nginx proxy    </i>
 </p>




3. As far as I understood, a Swarm load balancer is a basic Layer 4 (TCP) load balancer. Sometimes, we need additional features for our services like:

- SSL/TLS termination
- Content‑based routing (based, for example, on the URL or a header)
- Access control and authorization
- Rewrites and redirects 

That's why we will use external balancers.


![](https://i.imgur.com/lQVTFg9.png)
<p align = "center">
  <i>Figure 16: External load balancer diagram</i>
 </p>
    
![](https://i.imgur.com/OW9bKQt.png)        
<p align = "center">
  <i>Figure 17: Real life digram I found </i>
 </p>   



In conclusion, as I understand, in real life, they will depend on both internal and external for answering the requests from both outside and insides (requests between microservices). The internal load balancer will receive and take the action to the external and then route the request based on the configurations.


-----------------
Refrences:

1. [Docker Swarm Load Balancing with NGINX and NGINX Plus](https://www.nginx.com/blog/docker-swarm-load-balancing-nginx-plus/)
2. [Sample Load balancing solution with Docker and Nginx](https://towardsdatascience.com/sample-load-balancing-solution-with-docker-and-nginx-cf1ffc60e644)
3. [Use NGINX to load balance across your Docker Swarm cluster](https://techcommunity.microsoft.com/t5/containers/use-nginx-to-load-balance-across-your-docker-swarm-cluster/ba-p/382362)
4. [Nginx-Swarm-Demo-Github](https://github.com/nginxinc/NGINX-Demos/tree/master/nginx-swarm-demo/nginxplus)
5. [How To Remove Docker Images, Containers, and Volumes](https://www.digitalocean.com/community/tutorials/how-to-remove-docker-images-containers-and-volumes)
6. [Configuring NGINX and NGINX Plus as a Web Server](https://docs.nginx.com/nginx/admin-guide/web-server/web-server/)
7. 
