# Fault Tolerant and High Available Storage & Backup


## Fault Tolerant Storage

### Task 1: Take a pick

Before choosing, briefly describe and explain the difference between block storage, file storage and object storage.

Take a pick from the list proposed below:

- DRBD (preferred option)
- Ceph block device
- Gluster block device
- FreeBSD HAST (if you're familiar with *BSD)
- does anything else exist as for BDs?


#### Implementation:

- File storage: Everything is a file and there is a hierarchical structure and you can find each file by its path.
- Block storage: Data will be chuncked into blocks of data and stored separately with unique identifiers. The blocks can be stored in different environments, such as one block in Windows and the rest in Linux.
- Object storage: Data will be divided in to self-contained units that are re-stored in a flat environment, with all objects at the same level. Also, each object has a unique number.

These storages are different in cost of implementation (object storage is cheaper), ease of use (File storage for lower volumes of data and Object storage for high volumes of data)

I am going to use "DRBD"


### Task 2: Fault tolerant setup

Create and configure a necessary amount of VMs for your option. Install necessary packets and then configure a distributed block device.

Check (for all VMs) that a new block device appeared in the system and format it with usual filesystem like EXT4 or XFS and then mount. Make sure that each VM can recognize a filesystem on distributed block device.

Validate that storage on your distributed block device is fault tolerant (create some data, destroy one node, check storage status, etc.).

Have you lost your data after destroying one node? Was it necessary to do something on another nodes to get the data?


#### Implementation:

I am going to use three vms I have (pc1,pc2,pc3)

To install and configure the DRBD, I need to create an additional disk for all my VMs.

```
#Create 5G disk:
sudo time qemu-img create -f qcow2 /var/lib/libvirt/images/pc2-vdb.qcow2 5000M -o preallocation=full

#Attach the disk
sudo virsh attach-disk --domain pc3 /var/lib/libvirt/images/pc2-vdb.qcow2 --target vdb --persistent --config

```

Install the package:

```
sudo apt install drbd-utils
```

Create the configuration file in all the VMs (/etc/drbd.conf):

```
#include "drbd.d/global_common.conf";
include "drbd.d/*.res";

global { usage-count no; }
common { syncer { rate 100M; } }
resource r0 {
        protocol C;
        startup {
                wfc-timeout  15;
                degr-wfc-timeout 60;
        }
        net {
                cram-hmac-alg sha1;
                shared-secret "secret";
        }
        on pc1 {
                device /dev/drbd0;
                disk /dev/vdb1;
                address 192.168.122.189:7788;
                meta-disk internal;
        }        
        on pc2 {
                device /dev/drbd0;
                disk /dev/vdb1;
                address 192.168.122.30:7788;
                meta-disk internal;
        }
        on pc3 {
                device /dev/drbd0;
                disk /dev/vdb1;
                address 192.168.122.117:7788;
                meta-disk internal;
        }
}
```

Initialize the meta data storage (run on all Vms):

```
sudo drbdadm create-md r0
```

Start drdb daemon:

```
sudo systemctl start drbd.service
```

My PC3 is the primary one:
```
sudo drbdadm -- --overwrite-data-of-peer primary all
```

Then, I figured it out that DRBD version 8.4.x doesn't support more than 2 nodes.
I should upgrade to version 9.
After spending time, I figured out that I cannot upgrade to version 9 (it is not free). So, I will only continue with node pc3 and pc2 :)

After running the previous command, checking what is going on:



![](https://i.imgur.com/GP1xZLv.png)    
<p align = "center">
  <i>Figure 1: first stage of primary/secondry (pc3-primary)</i>
 </p>
    
![](https://i.imgur.com/rseKiuB.png)
<p align = "center">
  <i>Figure 2: pc2 health checking    </i>
 </p>
    
![](https://i.imgur.com/zElxDc1.png)
    
![](https://i.imgur.com/9jZqY7N.png)

<p align = "center">
  <i>Figure 3: volume drbd0 created on both PCs  </i>
 </p>  


Adding a filesystem to /dev/drbd0 and mount:

```
sudo mkfs.ext4 /dev/drbd0
sudo mkdir -p /mnt/lab6
sudo mount /dev/drbd0 /mnt/lab6

```


![](https://i.imgur.com/pxOFvFa.png)
<p align = "center">
  <i>Figure 4: Check the filesystem    </i>
 </p>


But there was no such a result in pc2 (no filesystem for the drbd0). I don't think this shows a problem .. but in this step I am not sure.

Test that the data is syncing between the hosts:


```
sudo cp -r /etc/default /mnt/lab6/

#unmount
sudo umount /mnt/lab6

#change the role from primary to secondary (PC3):
sudo drbdadm secondary r0

#change the role from secondary to primary (PC2)
#in a way that something happend for our primary node and we need to have another primary one.
#so we will have the complete syncornization again. For this happening we also need to mount the partition.

sudo drbdadm primary r0
sudo mount /dev/drbd0 /mnt/lab6  
```

Then, we can see the files in our PC2's mnt/lab6 directory:



![](https://i.imgur.com/RQB6POp.png)
<p align = "center">
  <i>Figure 5: Synced files</i>
 </p>
    
![](https://i.imgur.com/ZbkaHek.png)
<p align = "center">
  <i>Figure 6: Syncornization completed  </i>
 </p>  


p.s: now PC2 has the ext4 filesystem (After mounting), so, there is no problem.



![](https://i.imgur.com/pGvIRSe.png)
<p align = "center">
  <i>Figure 7: pc2 drbd0 filesystem</i>
 </p>



As a conclusion, data was not lost!

### Task 3: High Available setup

Modify your configuration to make storage high available. Besides it, you will need to format your block device with a clustered filesystem (e.g., OCFS2, GlusterFS, MooseFS).

Again validate the storage on your distributed block device.

Was it necessary to do something on another nodes to get the data in this setup?


#### Implementation:

For this part I configured my /etc/drbd.conf file in the following way:

```
startup {
        wfc-timeout  15;
        degr-wfc-timeout 60;
        become-primary-on both;
}
net {
        cram-hmac-alg sha1;
        shared-secret "secret";
        allow-two-primaries yes;
        after-sb-0pri discard-zero-changes;
        after-sb-1pri discard-secondary;
        after-sb-2pri disconnect;

}

```
- allow-two-primaries – Generally, DRBD has a primary and a secondary node. In this case, we will allow both nodes to have the filesystem mounted at the same time.
- after-sb-0pri discard-zero-changes – DRBD detected a split-brain scenario, but none of the nodes think they’re a primary. DRBD will take the newest modifications and apply them to the node that didn’t have any changes.
- after-sb-1pri discard-secondary – DRBD detected a split-brain scenario, but one node is the primary and the other is the secondary. In this case, DRBD will decide that the secondary node is the victim and it will sync data from the primary to the secondary automatically.
- after-sb-2pri disconnect – DRBD detected a split-brain scenario, but it can’t figure out which node has the right data. It tries to protect the consistency of both nodes by disconnecting the DRBD volume entirely. You’ll have to tell DRBD which node has the valid data in order to reconnect the volume.


Then I configured the OCFS2 as the cluster filesystem. This filesystem allow both nodes in a cluster mount and transfer files in a same place.

Install OCFS2 on both nodes:
```
apt-get install -y ocfs2-tools
```

Creating the file "/etc/ocfs2/cluster.conf" on both nodes with the following lines:

```
cluster:
    node_count = 2
    name = web

node:
    ip_port = 7777
    ip_address = 192.168.122.117
    number = 1
    name = pc3
    cluster = web

node:
    ip_port = 7777
    ip_address = 192.168.122.30
    number = 2
    name = pc2
    cluster = web

```

Making the filesystem:

```
# on Node PC3
mkfs.ocfs2 -L "web" /dev/drbd0
```


it will create a cluster with name web and two nodes "pc2" and "pc3".

Enabling on both nodes:

```
dpkg-reconfigure ocfs2-tools
    # Answer "y" to "Load O2CB driver on boot"
    # Answer "web" to "Cluster to start on boot"

/etc/init.d/o2cb start && /etc/init.d/ocfs2 start

```

Starting the drbd:

```
drbdadm create-md r0
 
modprobe drbd
drbdadm up r0
```
Then I had this outputs:


    
![](https://i.imgur.com/EOb6voR.png)
<p align = "center">
  <i>Figure 8: first stage of enabling drdb</i>
 </p>



```
# on Node pc3
drbdadm -- --overwrite-data-of-peer primary r0
```


![](https://i.imgur.com/1tEonqj.png)    
<p align = "center">
  <i>Figure 9: After enabling one node as primary - the syncing process</i>
 </p>


```
# on Node pc2
sudo drbdadm primary r0
```


![](https://i.imgur.com/tkl6rkl.png)
<p align = "center">
  <i>Figure 10: After second node became primary</i>
 </p>


Adding the mounting point to startup, and then mount it (on both nodes):

```
echo "/dev/drbd0 /mnt/lab6 ocfs2  noauto,noatime  0 0" >> /etc/fstab

sudo mount /dev/drbd0 
```

    
![](https://i.imgur.com/5kZQ3Aq.png)
    
![](https://i.imgur.com/QLtZdKH.png)
<p align = "center">
  <i>Figure 11: mounting point</i>
 </p>


Then I just copied some files into the mounting point and I was able to see it on the other node too (without any unmounting, dgrading to secondary and making primary which were necessary for the previous state)

```
sudo cp -r /etc/default /mnt/lab6/
```




![](https://i.imgur.com/SwurBB0.png)

![](https://i.imgur.com/fzLbpSu.png)
    
<p align = "center">
  <i>Figure 12: File on both nodes available</i>
 </p>


### Task 4: Questions

- Explain what is fault tolerance and high availability 
- What is a split-brain situation?
- What are the advantages and disadvantages of clustered filesystems?


#### Implementation:

HA (High Availability): High availability clusters are groups of hosts (physical machines) that act as a single system and provide continuous availability. In a way that if one host experience single point of failure, the whole system won't get affected and service would still be alive.
Nodes should have access to a shared storage too.
It can be in two modes:
- Active/Passive: only the active node will answer the requests and in the case of failover the IP address of the active node will map to the Passive one and so, the clients will be connected to the Passive one.
- Active/Active: Both nodes answer the requests and in the case of failure, the active one will answer the requests of the failed one and its share in a same time and when the node is active again, the lode will split between them again.
- clustered file systems provide increased resource availability and minimize the downtime. cause if a node goes down, the other ones have access to the data and there would be no downtime.  A clustered file system can distribute projects and data across different nodes to create the desired configuration (means reduce of hardware). increase in performance, greater scalability, and simplified data management.
I couldn't find disadvantages for these filesystems .. 

    
    
![](https://i.imgur.com/bK7UDc2.png)
<p align = "center">
  <i>Figure 13: Active/Passive HA cluster</i>
 </p>
    
![](https://i.imgur.com/C0rqg7S.png)
<p align = "center">
  <i>Figure 14: Active/Active HA cluster</i>
 </p>


Fault Tolerance: As far as I understand, fault tolerance is similar to the HA but better than it.
Unlike high availability, fault-tolerant systems:
    - Experience absolutely no downtime in the event of a failure since there is no crossover event. 
    - Are designed so that all traffic, requests, and changes to data are duplicated onto multiple redundant systems simultaneously. 

Split brain:
A split brain situation is caused by a temporary failure of the network link between the cluster nodes, resulting in both nodes switching to the active (primary) role while disconnected. This might cause new data (for example, log messages) to be created on both nodes without being replicated to the other node.

## Backup

### Task 1: Take a pick

Choose any tool from the list below:
- Borg
- restic
- rsync


#### Implementation:

I am going to use Borg.


### Task 2: Configuration & Testing

Create 2 VMs (server and client), install and configure OS (please check the list of supported OS for your solution).

Configure your solution: install necessary packets, edit the configuration.

Create a repo on the backup server which will be used to store your backups.
**Bonus**: configure an encrypted repo.

Make a backup of /home directory (create some files and directories before backuping) of your client. Don't forget to make a verification of backup (some solutions provide an embedded option to verify backups). If there is no embedded option to verify backups try to make a verification on your own.

Then damage your client's /home/ directory (encrypt it or forcibly remove) and restore from
backup. Has anything changed with the files after restoring? Can you see and edit them?


#### Implementation:

Installing Borg on both machines:

```
sudo apt-get install borgbackup
```
Create a backup repository on PC2 for PC3:

```
sudo borg init --encryption=repokey pc2@192.168.122.30:/home/pc2/backup

```


    
![](https://i.imgur.com/evFXjt3.png)
<p align = "center">
  <i>Figure 15: creating a repository</i>
 </p>
    
![](https://i.imgur.com/nptW3X2.png)    
<p align = "center">
  <i>Figure 16: Home directory    </i>
 </p>


Creating a backup

```
borg create pc2@192.168.122.30:/home/pc2/backup::archive1 /home
```

I verified the backup from both PCs with the following commands and there were no problem found.

```
#PC3 
borg check --verify-data --verbose pc2@192.168.122.30:/home/pc2/backup::archive1

#PC2
borg check --verify-data --verbose backup/
```


![](https://i.imgur.com/Vr9cXrG.png)

![](https://i.imgur.com/eER0VuP.png)
<p align = "center">
  <i>Figure 17: verify the backup</i>
 </p>


I delete my home directory and try to restore the backup.

we can check the available backups:

```
sudo borg list pc2@192.168.122.30:/home/pc2/backup
```
Also we can see the content of the archive using:

```
sudo borg list pc2@192.168.122.30:/home/pc2/backup::archive1
```


![](https://i.imgur.com/9QKLsVP.png)    
<p align = "center">
  <i>Figure 18: list of files in archive1</i>
 </p>


With the following command we can restore the backup:

```
sudo borg extract pc2@192.168.122.30:/home/pc2/backup::archive1
```

And you can see that everything is back successfully. Also yes, everything was fine and I was able to read and write in the files.



![](https://i.imgur.com/rJ6r1Ck.png)    
<p align = "center">
  <i>Figure 19: Restore backup</i>
 </p>



### Task 3: Questions

- When and how often do you need to verify your backups?
- Backup rotations schemes, what are they? Are they available in your solution?


-  Failures (fail to restore data from backups, backup failure, etc.) can be avoided as long as we verify the backups on a regular basis. We can follow different ways for this checking and it depends on our company's strategy, how much data we have, the level of security and ...
    -  When Application Changes Greatly
    -  When Application Data Changes Drastically
    -  When New Application Is Installed

- A backup rotation scheme is a system of backing up data to computer media. The scheme determines how and when each piece of removable storage is used for a backup job and how long it is retained once it has backup data stored on it. Some of the schemes are:
    - First in, first out: Saves new or modified files onto the "oldest" media in the set
    - Grandfather-father-son: There are three or more backup cycles, such as daily, weekly and monthly. Each one on their basis (daily backup on daily basis using FIFO and so on)
    - Tower of Hanoi

In my current solution no, I don't think so. But I am not sure if I understood the question well.


--------------
1. [Create, attach, detach disk to vm in kvm on command line](https://bgstack15.wordpress.com/2017/09/22/create-attach-detach-disk-to-vm-in-kvm-on-command-line/)
2. [How to add disk image to KVM virtual machine with virsh command](https://www.cyberciti.biz/faq/how-to-add-disk-image-to-kvm-virtual-machine-with-virsh-command/)
3. [Ubuntu HA - DRBD](https://ubuntu.com/server/docs/ubuntu-ha-drbd)
4. [How to Setup DRBD to Replicate Storage on Two CentOS 7 Servers](https://www.tecmint.com/setup-drbd-storage-replication-on-centos-7/)
5. [What is Split brain and why do you need to worry about it?](https://www.45drives.com/community/articles/what-is-split-brain/)
6. [Recovering from Split-Brain situation in high availability environment](https://support.oneidentity.com/syslog-ng-store-box/kb/264445/recovering-from-split-brain-situation-in-high-availability-environment)
7. [DRBD with Cluster File System on Debian Jessie](https://ip.engineering/drbd-with-cluster-file-system-on-debian-jessie/)
8. [Backing Up With Borg](https://medium.com/swlh/backing-up-with-borg-c6f13d74dd6)
9. [Borg man page](https://manpages.debian.org/testing/borgbackup/borg-check.1.en.html)
10. [How Often Should You Verify Data Backups?](https://www.datanumen.com/blogs/often-verify-data-backups/)
11. [Backup rotation scheme](https://en.wikipedia.org/wiki/Backup_rotation_scheme)
12. [Backup Rotation Schemes](https://www.handybackup.net/backup-rotation-schedule.shtml)
