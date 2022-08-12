# Infrastructure Monitoring using Zabbix


## Task 1: Preparation

- Install a new guest system
- Install and configure web-server + DBMS (e.g. NGINX + MariaDB)
- Install and configure a CMS. Create a page with some heavy content
- Install another guest system and deploy the monitoring facility (and agents, if required)
---------------

### Implementation:

First of all I used kvm and created two ubuntu guest machines.

**Install Zabbix server on PC1:**
- Install the Apache, MariaDB, PHP:

```
apt-get install apache2 libapache2-mod-php mariadb-server php php-mbstring php-gd php-xml php-bcmath php-ldap php-mysql unzip curl gnupg2 -y
```
- Edit the apache config file (/etc/php/7.4/apache2/php.ini):

```
memory_limit = 256M
upload_max_filesize = 16M
post_max_size = 16M
max_execution_time = 300
max_input_time = 300
max_input_vars = 10000
date.timezone = Europe/Moscow
```

- Create the Zabbix database:

```
#Login to the shell
sudo mysql

#Create database and use
CREATE DATABASE zabbixdb character set utf8 collate utf8_bin;
CREATE USER 'zabbixuser'@'localhost' IDENTIFIED BY 'pass'

#Grant all the privilages on the zabbixdb to the user

GRANT ALL PRIVILEGES ON zabbixdb.* TO 'zabbixuser'@'localhost' WITH GRANT OPTION;

#flush the privileges and exit from the MariaDB shell 
FLUSH PRIVILEGES;
EXIT;

```

- Install the Zabbix server:

```
wget https://repo.zabbix.com/zabbix/5.0/ubuntu/pool/main/z/zabbix-release/zabbix-release_5.0-1+focal_all.deb
sudo dpkg -i zabbix-release_5.0-1+focal_all.deb 
apt update -y
sudo apt-get install zabbix-server-mysql zabbix-frontend-php zabbix-agent zabbix-apache-conf -y

#import the Zabbix database schema.
sudo zcat create.sql.gz | mysql -u zabbixuser -p zabbixdb

#Edit the zabbix default configuration file: (nano /etc/zabbix/zabbix_server.conf)

  DBHost=localhost
  DBName=zabbixdb
  DBUser=zabbixuser
  DBPassword=pass
  
#Restart Appache and Zabbix:
systemctl restart zabbix-server
systemctl restart apache2
```


**Install Nginx and config for the website on PC2**

I installed the Nginx and configured it to serve a domain name "http://www.mysite-st5.xyz". Cause I think installing and managing the Nginx is out of this assignment scope, I wont go through explaining the steps. 
Then I cloned this web project from github.

```
git clone https://github.com/QAZIMAAZARSHAD/Movie-Streaming-Website.git
```

![](https://i.imgur.com/q3ZcUmO.png)
<p align = center>
<i>Figure 1: Website</i>
</p>

**Install Zabbix agent on PC2**


```
#Edit /etc/zabbix/zabbix_agentd.conf file:
    Hostname=system.hostname
    ServerActive=192.168.122.189
    Server=192.168.122.189
```

![](https://i.imgur.com/2V9z2qX.png)   

![](https://i.imgur.com/MH8wmsu.png)

![](https://i.imgur.com/Qrvm5ZE.png)
    
![](https://i.imgur.com/g6sdGhu.png)
    
![](https://i.imgur.com/QM5NFVR.png)
    
<p align = center>
<i>Figure 2: Zabbix server webpage -- configuration</i>
</p>


- Add agent to the server:

![](https://i.imgur.com/wiKCe4r.png)
<p align = center>
<i>Figure 3: Add agent</i>
</p>

--------------
## Task 2: Status alerts

Setup a few alerts including

- against the guest system itself (ping)
- against available RAM or disk space (with threshold about 90%)
- against the web service
- and against two web pages, a simple one and the heavy-duty one

Validate that your monitoring displays an alert once you destroy the service (what is the delay, how long does it take for it to appear?)

**Bonus**: configure and validate that you receive an email (you can use Telegram instead of email (at least it is possible in Zabbix) for alerts.
-------------


### Implementation:


1. I add the "Template Module ICMP Ping" and then cut the pc2's internet off. It took about 3 minutes until I had the alert on the dashbord. And thats because of what is writen in the trigger part of this template (figure 6)


![](https://i.imgur.com/hh3VDX6.png)
<p align = center>
<i>Figure 4: ICMP lost Alert</i>
</p>

![](https://i.imgur.com/hTSqzI1.png)
<p align = center>
<i>Figure 5: ICMP lost alert details</i>
</p>
    
![](https://i.imgur.com/zuodCYV.png) 
<p align = center>
<i>Figure 6: ICMP Ping triggers</i>
</p>

- Telegram alert receiving: 
I used the @BotFather and created the channel then it gave me a token which I used in the zabbix to enable the messagin. Then I had to enable zabbix to send the message (figure 8). At the end, I had to create a telegram media for admin (Figure 9)


![](https://i.imgur.com/pPQ6LtY.png)
<p align = center>
<i>Figure 7</i>
</p>

![](https://i.imgur.com/O13LfyY.png)
<p align = center>
<i>Figure 8</i>
</p>
    
![](https://i.imgur.com/zISnPGR.png)
<p align = center>
<i>Figure 9</i>
</p>
    
![](https://i.imgur.com/3BLvFXx.png)
<p align = center>
<i>Figure 10: ICMP Alert in telegram </i>    
</p>



2. Cause I didn't find a template to show the used memory percentage, I create the template and add two Items inside it. One for Available RAM (used one) and the other for the total RAM. In the end I create the trigger to calculate "(Used RAM/ Total RAM)*100" and if this value was more than 80% create a warning (Cause I couldn't increase the RAM usage to morethan 70 to test if mine is working correctly or not):


![](https://i.imgur.com/iCHkxQ7.png)

![](https://i.imgur.com/3ZyLDRb.png)

![](https://i.imgur.com/0J9GtLI.png)
<p align = center>
<i>Figure 11: Creating an item and a trigger for available RAM</i>
</p>


Then I tried to increase the RAM Usage and I had the alert:

![](https://i.imgur.com/u0LIiew.png)
    
![](https://i.imgur.com/kzXmlDG.png)
<p align = center>
<i>Figure 12: Alert from RAM usage</i>
</p>


For monitoring the web service, I think you meant web server status and these kind of staffs so, I used the Nginx template by Agent and itself had some configured triggers so, I tried to destroy the service and see what happenes.

![](https://i.imgur.com/HK5ElPk.png)
<p align = center>
<i>Figure 13: Available metrics for nginx</i>
</p>
    
![](https://i.imgur.com/J0iptsc.png)
<p align = center>
<i>Figure 14: Available triggers</i>
</p>
    
![](https://i.imgur.com/aR1CqWE.png)
    
![](https://i.imgur.com/qhoZd90.png)
<p align = center>
<i>Figure 15 : Alerts for web service </i>
</p>   



And for the availabliltiy of the webpage I had to create a web scenario:

![](https://i.imgur.com/rD5tiCz.png)
![](https://i.imgur.com/FMYLid7.png)
    
<p align = center>
<i>Figure 16 : web scenario and its step</i>
</p>



Then creating a trigger:

![](https://i.imgur.com/auzhNCF.png)    
<p align = center>
<i>Figure 17: Web trigger</i>
</p>
    
![](https://i.imgur.com/3afu2Al.png)
    
![](https://i.imgur.com/pjvRmkZ.png)
<p align = center>
<i>Figure 18 : Web alert  </i>
</p>  
    
------------
## Task 3: Stress & performance graphs

Take a pick for stress benchmark
- yandex.tank
- AB
- Autocannon
- Siege
- K8
- ...

Then use your load-testing tool of choice and perform a few different load tests.
- Define performance graphs for AT LEAST the four different kinds of resources (CPU, RAM, DISK I/O, Network TX/RX)

----------

## Implementation:

I picked AB (Apache Bench) for the load-testing tool.


For the graph, I used both creating a graph as widget and also creating it in the tab of graph in template.


![](https://i.imgur.com/QXSukN0.png)
<p align = center>
<i>Figure 19: Creating a graph widget for Used RAM (Available RAM)</i>
</p>
    
![](https://i.imgur.com/Ivi3H1S.png)
<p align = center>
<i>Figure 20: Used RAM graph</i>
</p>
    
![](https://i.imgur.com/SBnsOZo.png)
<p align = center>
<i>Figure 21: Create graph for CPU idle time and user time</i>
</p>
    
![](https://i.imgur.com/zAv3Gn0.png)
<p align = center>
<i>Figure 22: CPU idle/user time graph</i>
</p>
    
![](https://i.imgur.com/n4n81tK.png)
<p align = center>
<i>Figure 23: CPU idle/user time graph widget  </i>
</p>    


For the Disk IO I created the following items:

![](https://i.imgur.com/hawLgko.png)
    
![](https://i.imgur.com/s6cytk2.png)
<p align = center>
<i>Figure 24: Disk IO Items</i>
</p>


Then creating the graph:

![](https://i.imgur.com/B4WVvLA.png)
<p align = center>
<i>Figure 25: Disk IO graph</i>
</p>


For Network input and output:

![](https://i.imgur.com/Ae8VwbP.png)
    
![](https://i.imgur.com/wrvy9qA.png)
<p align = center>
<i>Figure 26: Network monitoring items</i>
</p>

![](https://i.imgur.com/KjRdBKR.png)
<p align = center>
<i>Figure 27: Network monitoring graph</i>
</p>
    
    
![](https://i.imgur.com/IUfgcgq.png)
<p align = center>
<i>Figure 28: Full dashboard graphs </i>
</p>   

----------------
- Play with the number of threads, number of clients, and request bodies while performing requests
--------------


### Implementation:

I used the command below and have the following output for the first test:

```
ab -k -n 10000 -c 1000 http://www.mysite-st5.xyz/home.html
```
This will create a http keep alive connection with request count equal to 10k and 1000 requestes in a same time (concurrent request count)
```
This is ApacheBench, Version 2.3 <$Revision: 1843412 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking www.mysite-st5.xyz (be patient)
Completed 1000 requests
Completed 2000 requests
Completed 3000 requests
Completed 4000 requests
Completed 5000 requests
Completed 6000 requests
Completed 7000 requests
Completed 8000 requests
Completed 9000 requests
Completed 10000 requests
Finished 10000 requests


Server Software:        nginx/1.18.0
Server Hostname:        www.mysite-st5.xyz
Server Port:            80

Document Path:          /home.html
Document Length:        141617 bytes

Concurrency Level:      1000
Time taken for tests:   0.218 seconds
Complete requests:      10000
Failed requests:        320
   (Connect: 0, Receive: 0, Length: 160, Exceptions: 160)
Keep-Alive requests:    9840
Total transferred:      1395990960 bytes
HTML transferred:       1393511280 bytes
Requests per second:    45771.41 [#/sec] (mean)
Time per request:       21.848 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
Transfer rate:          6239889.88 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   3.1      0      13
Processing:     0   19  11.0     15      41
Waiting:        0   19  11.1     15      41
Total:          0   20  11.2     19      47

Percentage of the requests served within a certain time (ms)
  50%     19
  66%     27
  75%     30
  80%     31
  90%     35
  95%     39
  98%     40
  99%     44
 100%     47 (longest request)

```

After that in multiple test cases I increased the number of concurrent requests and number of requests per second to the following one:

```
ab -k -n 186650 -c 1000 http://www.mysite-st5.xyz/home.html

```
I couldn't increase them more (it would stop working) and the output was like the below.

```
This is ApacheBench, Version 2.3 <$Revision: 1843412 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking www.mysite-st5.xyz (be patient)
Completed 18665 requests
Completed 37330 requests
Completed 55995 requests
Completed 74660 requests
Completed 93325 requests
Completed 111990 requests
Completed 130655 requests
Completed 149320 requests
Completed 167985 requests
Completed 186650 requests
Finished 186650 requests


Server Software:        nginx/1.18.0
Server Hostname:        www.mysite-st5.xyz
Server Port:            80

Document Path:          /home.html
Document Length:        141617 bytes

Concurrency Level:      1000
Time taken for tests:   3.208 seconds
Complete requests:      186650
Failed requests:        448
   (Connect: 0, Receive: 0, Length: 224, Exceptions: 224)
Keep-Alive requests:    185069
Total transferred:      26448063409 bytes
HTML transferred:       26401090842 bytes
Requests per second:    58178.06 [#/sec] (mean)
Time per request:       17.189 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
Transfer rate:          8050543.04 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   1.1      0      22
Processing:     0   17  11.0     17     269
Waiting:        0   17  10.3     16     213
Total:          0   17  11.1     17     269

Percentage of the requests served within a certain time (ms)
  50%     17
  66%     20
  75%     22
  80%     25
  90%     28
  95%     32
  98%     36
  99%     41
 100%    269 (longest request)

```


---------
- Look at the monitoring screen to see how bad your system is. What resource is the more impacted?..
--------

I ran the test multiple times and the following graph is the graph for last five minutes:

![](https://i.imgur.com/iHUjNio.png)
<p align = center>
<i>Figure 29: output after the test</i>
</p>

I think RAM usage and Disk IO write were infected the most in comperison with before.

------------
- Configure an alert threshold for one of those and validate it (Note: it does not make sense to define a threshold for CPU or Network unless you can define a timer within it)


**Bonus:** deal with the resource metrics from the virtualization host instead of guest agents.
**Bonus:** enable SSL on your web service and evaluate the impact on delay and performance.
-----------

I tried to create a trigger for cpu user time that would create an alert if the cpu usage would be greater than 25 for 3 minutes.

![](https://i.imgur.com/BBnknmg.png)
<p align = center>
<i>Figure 30: configuration for trigger</i>
</p>


Then I checked it:


![](https://i.imgur.com/rMOUgNK.png)    
<p align = center>
<i>Figure 31: graph for cpu usage</i>
</p>
    
![](https://i.imgur.com/56QH9Ca.png)
<p align = center>
<i>Figure 32: Alerts in the telegram   </i>
</p> 


-----------
**Questions:**
- Do the resulting metrics match with your stress load-test?
- Are your metrics representative of the actual state of affairs? Do they reflect reality?
- Are some of those irrelevant and should be omitted?
- So is your system high-load capable? If not, what would it take to make it happen?
----------

- I think yes. Cause when I start the load testing all the metrics were changed in a way that I expected (they increased)
- If I understood the question correctly, I think metrics are not bad or unreal. They only see for example how much the CPU is in use and so on. But on the other side I think the stress load testing was not real cause in the real world we will face more complicated scenarios and maybe our webserver would not work ideally.
- I think these 4 are needed to be considered always cause they represent the 4 most important parts of a system. It is important to see how much CPU is in use, how much network input-output we had, and...
- I think yes it didn't work badly in the stress load testing (or maybe not .. I am not sure)


-------------
## Task 4: Trends & business metrics

**Trends** - collect and store metric results for some period of time to see the analytic and forecasts.
Define a few ones, for example:
- RPC (requests per second) on web-server, DBMS, etc
- worker threads and processes
- queue size
- reply time (web-page generation time).
- MySQL/MariaDB types of operations, operations per second, db bandwidth, db disk i/o

and eventually define an alert threshold for one of those.

**Business metrics** - the above metric does not mean or cannot prove that you application works well in terms of functionality. Proceed with more fine-grained data, for example
- user activity (number of visits/views)
- how many views vs how many applicants
- page load time
- login/sign ups/buys/comments/etc
- ad conversions
- high-level metrics
------------


### Implementation:

From the Nginx template I added previously, I can get the requests per second on the web-server and for the response time, I'll use the web scenario I created. I'll create an item for number of processes in the worker node:



![](https://i.imgur.com/7eEhauq.png)
    


Then I create the forecast trigger:




![](https://i.imgur.com/KxqhSQW.png)



For response time:

![](https://i.imgur.com/VgjDe4I.png)



For processes:


![](https://i.imgur.com/fSGEAwe.png)



I am not sure but I think, connection accepted per second is the metric for user activity (number of visits/views):

![](https://i.imgur.com/5ffECH4.png)


We can see the values:


    
![](https://i.imgur.com/QDoqfWn.png)
    


----------
Refrences:

1. [How to Install Zabbix Monitoring Server on Ubuntu 20.04 ](https://www.alibabacloud.com/blog/how-to-install-zabbix-monitoring-server-on-ubuntu-20-04_597802)
2. [Подключаем Telegram к Zabbix](https://osbsd.com/connecting-telegram-to-zabbix.html)
3. [Zabbix Web Monitoring: Create Web Scenarios with Examples](https://bestmonitoringtools.com/zabbix-web-monitoring-create-web-scenarios-with-examples/)
4. [Web monitoring items](https://www.zabbix.com/documentation/current/en/manual/web_monitoring/items)
5. [Notes on selecting processes in proc.mem and proc.num item]()
6. [Zabbix Monitor Linux Process](https://techexpert.tips/zabbix/zabbix-monitor-linux-process/)
