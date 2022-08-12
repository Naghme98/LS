## Task 1: Take NoSQL solution

Some examples:
- MongoDB (default choice)
- Redis
- CasandraDB
- ScyllaDB
- ...




### Implementation:

I am going to use MongoDB with docker.


## Task 2: NoSQL cluster theory

Give the answers for the following questions what is and for what, will be better to provide explanatory pictures/graphs:
1. Redundancy
2. HA
3. Fault Tolerance


### Answers:

1. Redundancy: Redundancy is extra hardware or software that can be used as backup if the main hardware or software fails. Redundancy can be achieved via load balancing, high availabiltiy, etc in an automated way.


2. HA (High Availability): High availability clusters are groups of hosts (physical machines) that act as a single system and provide continuous availability. In a way that if one host experience single point of failure, the whole system won't get affected and service would still be alive.
Nodes should have access to a shared storage too.
It can be in two modes:
- Active/Passive: only the active node will answer the requests and in the case of failover the IP address of the active node will map to the Passive one and so, the clients will be connected to the Passive one.
- Active/Active: Both nodes answer the requests and in the case of failure, the active one will answer the requests of the failed one and its share in a same time and when the node is active again, the lode will split between them again.


    
    
![](https://i.imgur.com/bK7UDc2.png)
<p align = "center">
  <i>Figure 1: Active/Passive HA cluster</i>
 </p>
    
![](https://i.imgur.com/C0rqg7S.png)
<p align = "center">
  <i>Figure 2: Active/Active HA cluster</i>
 </p>


3. Fault Tolerance: As far as I understand, fault tolerance is similar to the HA but better than it.
Unlike high availability, fault-tolerant systems:
    - Experience absolutely no downtime in the event of a failure since there is no crossover event. 
    - Are designed so that all traffic, requests, and changes to data are duplicated onto multiple redundant systems simultaneously. 


## Task 3: NoSQL cluster deployment & validation & Fault Tolerance

1. Deploy your NoSQL cluster (e.g. with master, primary, slave, replica...) and investigate/describe its features.



With the following stucture I am going to create each image and connect everything.



![](https://i.imgur.com/0KpJ5xo.png)
<p align = "center">
  <i>Figure 3: Cluster structure.</i>
 </p>


Some notes from MongoDB (Indeed it is for myself:))
- A replica set is a group of mongod instances that maintain the same data set. one and only one member is deemed the primary node, while the other nodes are deemed secondary nodes. The primary receives all the write operations. The secondaries replicate the primary's oplog and apply the operations to their data sets such that the secondaries' data sets reflect the primary's data set
- Config servers: Config servers store the metadata for a sharded cluster. The metadata reflects state and organization for all data and components within the sharded cluster. The metadata includes the list of chunks on every shard and the ranges that define the chunks.
- Router: interface with client applications and direct operations to the appropriate shard
- A shard is a single MongoDB instance that holds a subset of the sharded data. Shards can be deployed as replica sets to increase availability and provide redundancy.

I wrote a docker-compose file to create the cluster:

```
mongorsn1:
    container_name: mongors1n1
    image: mongo
    command: mongod --shardsvr --replSet mongors1 --dbpath /data/db --port 27017
    ports:
      - 27017:27017
    expose:
      - "27017"
    environment:
      TERM: xterm
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /mongo_cluster/data1:/data/db
```
It will create a service with the name of "mongorsn1". Then create a container called "mongorsn1" using image mongo and run a command on it.

- mongod is the primary daemon process for the MongoDB system.
- --shardsvr: This option says it is a shard server (trying to create a shard cluster)
- --replSet it specifies the replica set's name to mongors1
- --dbpath: The directory where the mongod instance stores its data.
- --port: The TCP port on which the MongoDB instance listens for client connections.

then it will set the port 27017 for outside and 27017 for container and open the port 27017. 

The exact lines should be written for the mongors1n2 and mongors1n3. (The full docker-compose fill will be added in the end)

Now it is the time to create the repica set for the config servers:
Config servers store the metadata for a sharded cluster. The metadata reflects state and organization for all data and components within the sharded cluster. The metadata includes the list of chunks on every shard and the ranges that define the chunks.

```
mongocfg1:
    container_name: mongocfg1
    image: mongo
    command: mongod --configsvr --replSet mongors1conf --dbpath /data/db --port 27017
    environment:
      TERM: xterm
    expose:
      - "27017"
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /mongo_cluster/config1:/data/db
```
Creating a container called mongocfg1 with mongo image and command (most part of the command is similar to the previous one I explained):

- --configsvr: Declares that this mongod instance serves as the config server of a sharded cluster.
- --replSet mongors1conf: the replication set's name is mongors1conf.

Exactly the same code will should be written for the two others.

Creating the Router:
MongoDB mongos instances route queries and write operations to shards in a sharded cluster. mongos provide the only interface to a sharded cluster from the perspective of applications. Applications never connect or communicate directly with the shards.
```
mongos1:
    container_name: mongos1
    image: mongo
    depends_on:
      - mongocfg1
      - mongocfg2
    command: mongos --configdb mongors1conf/mongocfg1:27017,mongocfg2:27017,mongocfg3:27017 --port 27017
    ports:
      - 27019:27017
    expose:
      - "27017"
    volumes:
      - /etc/localtime:/etc/localtime:ro
```
Creating a container named mongos1 with image mongo and express dependency between services. Means config servers should be started before routers. The command details are:
- --configdb: Specifies the configuration servers for the sharded cluster in this style: "replicasetName/config1,config2,.."
        
In the end I ran the docker-compose file.
    


![](https://i.imgur.com/w7oTaVq.png)    
<p align = "center">
  <i>Figure 4: Cluster output </i>
 </p>   


The sharding cluster needs to be configured:
Configure config servers replica set:

```
docker exec -it mongocfg1 bash -c "echo 'rs.initiate({_id: \"mongors1conf\",configsvr: true, members: [{ _id : 0, host : \"mongocfg1\" },{ _id : 1, host : \"mongocfg2\" }, { _id : 2, host : \"mongocfg3\" }]})' | mongo"
```
it will run a command on mongocfg1:
- rs.initiate: Initiates a replica set
- _id: The id of this set (name of the set)
- members: define the members of this set (the three nodes we created before)


We can check the status by 
```

docker exec -it mongocfg1 bash -c "echo 'rs.status()' | mongo"
```
This was the output and as you can see the first member became the primary one and the two others as secondary.

```
{
	"set" : "mongors1conf",
	"date" : ISODate("2022-02-28T12:09:21.431Z"),
	"myState" : 1,
	"term" : NumberLong(1),
	"syncSourceHost" : "",
	"syncSourceId" : -1,
	"configsvr" : true,
	"heartbeatIntervalMillis" : NumberLong(2000),
	"majorityVoteCount" : 2,
	"writeMajorityCount" : 2,
	"votingMembersCount" : 3,
	"writableVotingMembersCount" : 3,
	"optimes" : {
		"lastCommittedOpTime" : {
			"ts" : Timestamp(1646050160, 3),
			"t" : NumberLong(1)
		},
		"lastCommittedWallTime" : ISODate("2022-02-28T12:09:20.394Z"),
		"readConcernMajorityOpTime" : {
			"ts" : Timestamp(1646050160, 3),
			"t" : NumberLong(1)
		},
		"appliedOpTime" : {
			"ts" : Timestamp(1646050160, 3),
			"t" : NumberLong(1)
		},
		"durableOpTime" : {
			"ts" : Timestamp(1646050160, 3),
			"t" : NumberLong(1)
		},
		"lastAppliedWallTime" : ISODate("2022-02-28T12:09:20.394Z"),
		"lastDurableWallTime" : ISODate("2022-02-28T12:09:20.394Z")
	},
	"lastStableRecoveryTimestamp" : Timestamp(1646050121, 1),
	"electionCandidateMetrics" : {
		"lastElectionReason" : "electionTimeout",
		"lastElectionDate" : ISODate("2022-02-28T12:07:53.615Z"),
		"electionTerm" : NumberLong(1),
		"lastCommittedOpTimeAtElection" : {
			"ts" : Timestamp(1646050062, 1),
			"t" : NumberLong(-1)
		},
		"lastSeenOpTimeAtElection" : {
			"ts" : Timestamp(1646050062, 1),
			"t" : NumberLong(-1)
		},
		"numVotesNeeded" : 2,
		"priorityAtElection" : 1,
		"electionTimeoutMillis" : NumberLong(10000),
		"numCatchUpOps" : NumberLong(0),
		"newTermStartDate" : ISODate("2022-02-28T12:07:53.699Z"),
		"wMajorityWriteAvailabilityDate" : ISODate("2022-02-28T12:07:55.102Z")
	},
	"members" : [
		{
			"_id" : 0,
			"name" : "mongocfg1:27017",
			"health" : 1,
			"state" : 1,
			"stateStr" : "PRIMARY",
			"uptime" : 461,
			"optime" : {
				"ts" : Timestamp(1646050160, 3),
				"t" : NumberLong(1)
			},
			"optimeDate" : ISODate("2022-02-28T12:09:20Z"),
			"lastAppliedWallTime" : ISODate("2022-02-28T12:09:20.394Z"),
			"lastDurableWallTime" : ISODate("2022-02-28T12:09:20.394Z"),
			"syncSourceHost" : "",
			"syncSourceId" : -1,
			"infoMessage" : "Could not find member to sync from",
			"electionTime" : Timestamp(1646050073, 1),
			"electionDate" : ISODate("2022-02-28T12:07:53Z"),
			"configVersion" : 1,
			"configTerm" : 1,
			"self" : true,
			"lastHeartbeatMessage" : ""
		},
		{
			"_id" : 1,
			"name" : "mongocfg2:27017",
			"health" : 1,
			"state" : 2,
			"stateStr" : "SECONDARY",
			"uptime" : 99,
			"optime" : {
				"ts" : Timestamp(1646050159, 1),
				"t" : NumberLong(1)
			},
			"optimeDurable" : {
				"ts" : Timestamp(1646050159, 1),
				"t" : NumberLong(1)
			},
			"optimeDate" : ISODate("2022-02-28T12:09:19Z"),
			"optimeDurableDate" : ISODate("2022-02-28T12:09:19Z"),
			"lastAppliedWallTime" : ISODate("2022-02-28T12:09:20.394Z"),
			"lastDurableWallTime" : ISODate("2022-02-28T12:09:20.394Z"),
			"lastHeartbeat" : ISODate("2022-02-28T12:09:19.633Z"),
			"lastHeartbeatRecv" : ISODate("2022-02-28T12:09:21.136Z"),
			"pingMs" : NumberLong(0),
			"lastHeartbeatMessage" : "",
			"syncSourceHost" : "mongocfg1:27017",
			"syncSourceId" : 0,
			"infoMessage" : "",
			"configVersion" : 1,
			"configTerm" : 1
		},
		{
			"_id" : 2,
			"name" : "mongocfg3:27017",
			"health" : 1,
			"state" : 2,
			"stateStr" : "SECONDARY",
			"uptime" : 99,
			"optime" : {
				"ts" : Timestamp(1646050159, 1),
				"t" : NumberLong(1)
			},
			"optimeDurable" : {
				"ts" : Timestamp(1646050159, 1),
				"t" : NumberLong(1)
			},
			"optimeDate" : ISODate("2022-02-28T12:09:19Z"),
			"optimeDurableDate" : ISODate("2022-02-28T12:09:19Z"),
			"lastAppliedWallTime" : ISODate("2022-02-28T12:09:20.394Z"),
			"lastDurableWallTime" : ISODate("2022-02-28T12:09:20.394Z"),
			"lastHeartbeat" : ISODate("2022-02-28T12:09:19.633Z"),
			"lastHeartbeatRecv" : ISODate("2022-02-28T12:09:21.138Z"),
			"pingMs" : NumberLong(0),
			"lastHeartbeatMessage" : "",
			"syncSourceHost" : "mongocfg1:27017",
			"syncSourceId" : 0,
			"infoMessage" : "",
			"configVersion" : 1,
			"configTerm" : 1
		}
	],
	"ok" : 1,
	"$gleStats" : {
		"lastOpTime" : Timestamp(0, 0),
		"electionId" : ObjectId("7fffffff0000000000000001")
	},
	"lastCommittedOpTime" : Timestamp(1646050160, 3),
	"$clusterTime" : {
		"clusterTime" : Timestamp(1646050160, 3),
		"signature" : {
			"hash" : BinData(0,"AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
			"keyId" : NumberLong(0)
		}
	},
	"operationTime" : Timestamp(1646050160, 3)
}
bye

```

Building the shard replica set:

```
docker exec -it mongors1n1 bash -c "echo 'rs.initiate({_id : \"mongors1\", members: [{ _id : 0, host : \"mongors1n1\" },{ _id : 1, host : \"mongors1n2\" },{ _id : 2, host : \"mongors1n3\" }]})' | mongo"
```

It will be executed on node mongors1n1 with the id of mongors1 and indicating the members. After that, the shard nodes know each other.

```
#check the status:
docker exec -it mongors1n1 bash -c "echo 'rs.status()' | mongo"
```
The result was like following and the first node is the primary one now:

```
{
	"set" : "mongors1",
	"date" : ISODate("2022-02-28T12:11:32.032Z"),
	"myState" : 1,
	"term" : NumberLong(1),
	"syncSourceHost" : "",
	"syncSourceId" : -1,
	"heartbeatIntervalMillis" : NumberLong(2000),
	"majorityVoteCount" : 2,
	"writeMajorityCount" : 2,
	"votingMembersCount" : 3,
	"writableVotingMembersCount" : 3,
	"optimes" : {
		"lastCommittedOpTime" : {
			"ts" : Timestamp(1646050289, 1),
			"t" : NumberLong(1)
		},
		"lastCommittedWallTime" : ISODate("2022-02-28T12:11:29.338Z"),
		"readConcernMajorityOpTime" : {
			"ts" : Timestamp(1646050289, 1),
			"t" : NumberLong(1)
		},
		"appliedOpTime" : {
			"ts" : Timestamp(1646050289, 1),
			"t" : NumberLong(1)
		},
		"durableOpTime" : {
			"ts" : Timestamp(1646050289, 1),
			"t" : NumberLong(1)
		},
		"lastAppliedWallTime" : ISODate("2022-02-28T12:11:29.338Z"),
		"lastDurableWallTime" : ISODate("2022-02-28T12:11:29.338Z")
	},
	"lastStableRecoveryTimestamp" : Timestamp(1646050267, 1),
	"electionCandidateMetrics" : {
		"lastElectionReason" : "electionTimeout",
		"lastElectionDate" : ISODate("2022-02-28T12:11:19.225Z"),
		"electionTerm" : NumberLong(1),
		"lastCommittedOpTimeAtElection" : {
			"ts" : Timestamp(1646050267, 1),
			"t" : NumberLong(-1)
		},
		"lastSeenOpTimeAtElection" : {
			"ts" : Timestamp(1646050267, 1),
			"t" : NumberLong(-1)
		},
		"numVotesNeeded" : 2,
		"priorityAtElection" : 1,
		"electionTimeoutMillis" : NumberLong(10000),
		"numCatchUpOps" : NumberLong(0),
		"newTermStartDate" : ISODate("2022-02-28T12:11:19.300Z"),
		"wMajorityWriteAvailabilityDate" : ISODate("2022-02-28T12:11:20.831Z")
	},
	"members" : [
		{
			"_id" : 0,
			"name" : "mongors1n1:27017",
			"health" : 1,
			"state" : 1,
			"stateStr" : "PRIMARY",
			"uptime" : 591,
			"optime" : {
				"ts" : Timestamp(1646050289, 1),
				"t" : NumberLong(1)
			},
			"optimeDate" : ISODate("2022-02-28T12:11:29Z"),
			"lastAppliedWallTime" : ISODate("2022-02-28T12:11:29.338Z"),
			"lastDurableWallTime" : ISODate("2022-02-28T12:11:29.338Z"),
			"syncSourceHost" : "",
			"syncSourceId" : -1,
			"infoMessage" : "Could not find member to sync from",
			"electionTime" : Timestamp(1646050279, 1),
			"electionDate" : ISODate("2022-02-28T12:11:19Z"),
			"configVersion" : 1,
			"configTerm" : 1,
			"self" : true,
			"lastHeartbeatMessage" : ""
		},
		{
			"_id" : 1,
			"name" : "mongors1n2:27017",
			"health" : 1,
			"state" : 2,
			"stateStr" : "SECONDARY",
			"uptime" : 24,
			"optime" : {
				"ts" : Timestamp(1646050289, 1),
				"t" : NumberLong(1)
			},
			"optimeDurable" : {
				"ts" : Timestamp(1646050289, 1),
				"t" : NumberLong(1)
			},
			"optimeDate" : ISODate("2022-02-28T12:11:29Z"),
			"optimeDurableDate" : ISODate("2022-02-28T12:11:29Z"),
			"lastAppliedWallTime" : ISODate("2022-02-28T12:11:29.338Z"),
			"lastDurableWallTime" : ISODate("2022-02-28T12:11:29.338Z"),
			"lastHeartbeat" : ISODate("2022-02-28T12:11:31.233Z"),
			"lastHeartbeatRecv" : ISODate("2022-02-28T12:11:30.737Z"),
			"pingMs" : NumberLong(0),
			"lastHeartbeatMessage" : "",
			"syncSourceHost" : "mongors1n1:27017",
			"syncSourceId" : 0,
			"infoMessage" : "",
			"configVersion" : 1,
			"configTerm" : 1
		},
		{
			"_id" : 2,
			"name" : "mongors1n3:27017",
			"health" : 1,
			"state" : 2,
			"stateStr" : "SECONDARY",
			"uptime" : 24,
			"optime" : {
				"ts" : Timestamp(1646050289, 1),
				"t" : NumberLong(1)
			},
			"optimeDurable" : {
				"ts" : Timestamp(1646050289, 1),
				"t" : NumberLong(1)
			},
			"optimeDate" : ISODate("2022-02-28T12:11:29Z"),
			"optimeDurableDate" : ISODate("2022-02-28T12:11:29Z"),
			"lastAppliedWallTime" : ISODate("2022-02-28T12:11:29.338Z"),
			"lastDurableWallTime" : ISODate("2022-02-28T12:11:29.338Z"),
			"lastHeartbeat" : ISODate("2022-02-28T12:11:31.233Z"),
			"lastHeartbeatRecv" : ISODate("2022-02-28T12:11:30.739Z"),
			"pingMs" : NumberLong(0),
			"lastHeartbeatMessage" : "",
			"syncSourceHost" : "mongors1n1:27017",
			"syncSourceId" : 0,
			"infoMessage" : "",
			"configVersion" : 1,
			"configTerm" : 1
		}
	],
	"ok" : 1,
	"$clusterTime" : {
		"clusterTime" : Timestamp(1646050289, 1),
		"signature" : {
			"hash" : BinData(0,"AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
			"keyId" : NumberLong(0)
		}
	},
	"operationTime" : Timestamp(1646050289, 1)
}
bye

```

Introducing the shard to the routers:

```
docker exec -it mongos1 bash -c "echo 'sh.addShard(\"mongors1/mongors1n1\")' | mongo "
```
The status is like:

```
--- Sharding Status --- 
  sharding version: {
  	"_id" : 1,
  	"minCompatibleVersion" : 5,
  	"currentVersion" : 6,
  	"clusterId" : ObjectId("621cbb1aa737a0cf7a5b9826")
  }
  shards:
        {  "_id" : "mongors1",  "host" : "mongors1/mongors1n1:27017,mongors1n2:27017,mongors1n3:27017",  "state" : 1,  "topologyTime" : Timestamp(1646075511, 1) }
  active mongoses:
        "5.0.6" : 2
  autosplit:
        Currently enabled: yes
  balancer:
        Currently enabled: yes
        Currently running: no
        Failed balancer rounds in last 5 attempts: 0
        Migration results for the last 24 hours: 
                No recent migrations
  databases:
        {  "_id" : "config",  "primary" : "config",  "partitioned" : true }
bye

```


5. Try to add new nodes after cluster is created, show them. How hard is it?

**Bonus**: deploy your NoSQL Cluster as Ansible roles.


I realized that it is better to have another shard for continuing the work. So, I will do this part first.

I create another 3 container as a shard replica set.

```
version: '3.3'
services:
  mongors2n1:
    container_name: mongors2n1
    image: mongo
    command: mongod --shardsvr --replSet mongors2 --dbpath /data/db --port 27017
    ports:
      - 27057:27017
    expose:
      - "27017"
    environment:
      TERM: xterm
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /mongo_cluster/data4:/data/db
  mongors2n2:
    container_name: mongors2n2
    image: mongo
    command: mongod --shardsvr --replSet mongors2 --dbpath /data/db --port 27017
    ports:
      - 27067:27017
    expose:
      - "27017"
    environment:
      TERM: xterm
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /mongo_cluster/data5:/data/db
  mongors2n3:
    container_name: mongors2n3
    image: mongo
    command: mongod --shardsvr --replSet mongors2 --dbpath /data/db --port 27017
    ports:
      - 27077:27017
    expose:
      - "27017"
    environment:
      TERM: xterm
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /mongo_cluster/data6:/data/db
```

Initialize the replica:


```
docker exec -it mongors2n1 bash -c "echo 'rs.initiate({_id : \"mongors2\", members: [{ _id : 0, host : \"mongors2n1\" },{ _id : 1, host : \"mongors2n2\" },{ _id : 2, host : \"mongors2n3\" }]})' | mongosh"
```

Again introduce it to the router:

```
docker exec -it mongos1 bash -c "echo 'sh.addShard(\"mongors2/mongors2n1\")' | mongo "
```

And you can see that it was added:

```
--- Sharding Status --- 
  sharding version: {
  	"_id" : 1,
  	"minCompatibleVersion" : 5,
  	"currentVersion" : 6,
  	"clusterId" : ObjectId("621cbb1aa737a0cf7a5b9826")
  }
  shards:
        {  "_id" : "mongors1",  "host" : "mongors1/mongors1n1:27017,mongors1n2:27017,mongors1n3:27017",  "state" : 1,  "topologyTime" : Timestamp(1646075511, 1) }
        {  "_id" : "mongors2",  "host" : "mongors2/mongors2n1:27017,mongors2n2:27017,mongors2n3:27017",  "state" : 1,  "topologyTime" : Timestamp(1646404174, 4) }

```

And it wasnt hard to add nodes we only need to create the connections and nothing else.

I suddenly thought that maybe it wouldn't a bad idea to try to create a signle node and add it in shard1:

```
version: '3.3'
services:
  mongors2n1:
    container_name: mongors1n4
    image: mongo
    command: mongod --shardsvr --replSet mongors1 --dbpath /data/db --port 27017
    ports:
      - 27087:27017
    expose:
      - "27017"
    environment:
      TERM: xterm
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /mongo_cluster/data7:/data/db
```

Add the node to the replica set:

```
docker exec -it mongors1n3 bash -c "echo 'rs.add({ host : \"mongors1n4\" })' | mongosh"
```

You can see that the node was added successfully:



![](https://i.imgur.com/O2eOmFr.png)




Diagram after all changes:


![](https://i.imgur.com/dm5JlNI.png)





2. Validate all the features by operating with some dataset. Create new nodes/ destroy one…



Creating a database:
```
docker exec -it mongors1n1 bash -c "echo 'use testDb' | mongo"
```
Enabling the sharding on newly created database: 

```
docker exec -it mongos1 bash -c "echo 'sh.enableSharding(\"testDb\")' | mongo "
```
Creating a collection on the sharded database:

```
docker exec -it mongors1n1 bash -c "echo 'db.createCollection(\"testDb.testCollection\")' | mongo "
```

Choosing a hashed-base sharding key:

```
docker exec -it mongos1 bash -c "echo 'sh.shardCollection(\"testDb.testCollection\", {\"country\": \"hashed\"})' | mongo "
```

The output after running the previous command:

```
================
{
	"collectionsharded" : "testDb.testCollection",
	"ok" : 1,
	"$clusterTime" : {
		"clusterTime" : Timestamp(1646330796, 29),
		"signature" : {
			"hash" : BinData(0,"AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
			"keyId" : NumberLong(0)
		}
	},
	"operationTime" : Timestamp(1646330796, 25)
}
bye

```

Now lets insert some data in our database:

Switch to database:

```
docker exec -it mongos1 bash -c "echo use testDb | mongo "
```

Insert data:

```
db.testCollection.insertMany([
    {"name": "Seoul", "country": "South Korea", "continent": "Asia", "population": 25.674 },
    {"name": "Mumbai", "country": "India", "continent": "Asia", "population": 19.980 },
    {"name": "Lagos", "country": "Nigeria", "continent": "Africa", "population": 13.463 },
    {"name": "Beijing", "country": "China", "continent": "Asia", "population": 19.618 },
    {"name": "Shanghai", "country": "China", "continent": "Asia", "population": 25.582 },
    {"name": "Osaka", "country": "Japan", "continent": "Asia", "population": 19.281 },
    {"name": "Cairo", "country": "Egypt", "continent": "Africa", "population": 20.076 },
    {"name": "Tokyo", "country": "Japan", "continent": "Asia", "population": 37.400 },
    {"name": "Karachi", "country": "Pakistan", "continent": "Asia", "population": 15.400 },
    {"name": "Dhaka", "country": "Bangladesh", "continent": "Asia", "population": 19.578 },
    {"name": "Rio de Janeiro", "country": "Brazil", "continent": "South America", "population": 13.293 },
    {"name": "São Paulo", "country": "Brazil", "continent": "South America", "population": 21.650 },
    {"name": "Mexico City", "country": "Mexico", "continent": "North America", "population": 21.581 },
    {"name": "Delhi", "country": "India", "continent": "Asia", "population": 28.514 },
    {"name": "Buenos Aires", "country": "Argentina", "continent": "South America", "population": 14.967 },
    {"name": "Kolkata", "country": "India", "continent": "Asia", "population": 14.681 },
    {"name": "New York", "country": "United States", "continent": "North America", "population": 18.819 },
    {"name": "Manila", "country": "Philippines", "continent": "Asia", "population": 13.482 },
    {"name": "Chongqing", "country": "China", "continent": "Asia", "population": 14.838 },
    {"name": "Istanbul", "country": "Turkey", "continent": "Europe", "population": 14.751 }
])

```
with this sentax:

```
docker exec -it mongos1 /bin/bash
```



![](https://i.imgur.com/f3TI9hK.png)

![](https://i.imgur.com/NWied3c.png)


Lets search one data:

```
db.testCollection.find({"continent": "Europe"}).explain()
```


    
![](https://i.imgur.com/EGNHpJI.png)



We can see that it will search in two shards.

Then I stopped 2 containers "mongors1n2" and "mongors2n2" (one from each shard) and then ran the command again and I had the same output as before and nothing changed.



![](https://i.imgur.com/lydsXdh.png)



p.s: I tried to delete a whole shard and I faced a problem then I checked in the site and they said we should prepare the migration :)



3. Describe and validate the election process of the primary.
4. Destroy the nodes and describe what will happened?


When in replica set 4 events happen, we need a new primary one so an election would be held.
The events are:
- A new node was added.
- Initiating a replica set
- Using methods like rs.stepDown() or rs.reconfig() the would change the replica set maintenance
- The secondary members losing connectivity to the primary (for morethan 10 sec)

In the election, based on some factors the primary would be choosed:

- Replication Election Protocol: Replication protocolVersion: 1 reduces replica set failover time and accelerate the detection of multiple simultaneous primaries.
- Heartbeats(pings):  If a heartbeat does not return within 10 seconds, the other members mark the delinquent member as inaccessible and it will be eliminated from the election process.
- Member Priority: Member priority affects both the timing and the outcome of elections; secondaries with higher priority call elections relatively sooner than secondaries with lower priority, and are also more likely to win
- Mirrored Reads: It is used to warm electable secondary members' cache with the most recently accessed data

In a set, no morethan 7 nodes can vote (voting members)



![](https://i.imgur.com/1l2gqIq.png)



As you can see, after primary goes down, one of the remaining secondaries calls for an election to select a new primary and automatically resume normal operations. The election is first decided by priority. If both Nodes B & C have the same priority, then the one who is most up to date in respect to the failed primary (oplog) wins. Let's say it's Node B.

Once node A comes back alive, there is no new election. Node B remains the master, and C+A are now secondaries.

On the other hand, if two nodes go down you don't have a majority, so the replica set can't accept updates (apply writes) any more until at least one of the two failing servers becomes alive (and connected by the single surviving node) again.

Before turning off any nodes, the following is the current staus of the shard replica set2:

```
members: [
    {
      _id: 0,
      name: 'mongors2n1:27017',
      health: 1,
      state: 2,
      stateStr: 'SECONDARY',
    },
    {
      _id: 1,
      name: 'mongors2n2:27017',
      health: 1,
      state: 2,
      stateStr: 'SECONDARY',
    },
    {
      _id: 2,
      name: 'mongors2n3:27017',
      health: 1,
      state: 1,
      stateStr: 'PRIMARY',
    }
    
```

Then I would turn the mongors2n3 off:

```
{
      _id: 0,
      name: 'mongors2n1:27017',
      health: 1,
      state: 1,
      stateStr: 'PRIMARY',
    },
    {
      _id: 1,
      name: 'mongors2n2:27017',
      health: 1,
      state: 2,
      stateStr: 'SECONDARY',
    },
    {
      _id: 2,
      name: 'mongors2n3:27017',
      health: 0,
      state: 8,
      stateStr: '(not reachable/healthy)',
      uptime: 0,
      lastHeartbeatMessage: 'Error connecting to mongors2n3:27017 :: caused by :: Could not find address for mongors2n3:27017: SocketException: Host not found (authoritative)',

```
We can see that node 1 became the Primary succesfully.

And if I disable the primary now:

```
   {
      _id: 0,
      name: 'mongors2n1:27017',
      health: 0,
      state: 8,
      stateStr: '(not reachable/healthy)',
      lastHeartbeatMessage: 'Error connecting to mongors2n1:27017 :: caused by :: Could not find address for mongors2n1:27017: SocketException: Host not found (authoritative)'
    },
    
   {
      _id: 1,
      name: 'mongors2n2:27017',
      health: 1,
      state: 2,
      stateStr: 'SECONDARY',
      infoMessage: 'Could not find member to sync from',
    },
    {
    _id: 2,
      name: 'mongors2n3:27017',
      health: 0,
      state: 8,
      stateStr: '(not reachable/healthy)',
      lastHeartbeatMessage: 'Error connecting to mongors2n3:27017 :: caused by :: Could not find address for mongors2n3:27017: SocketException: Host not found (authoritative)'
    }
```

And as we expected, a new primary didn't selected.


-----------------
Refrences:

1. [High Availability: What It Is and How You Can Achieve It](https://www.kaseya.com/blog/2021/08/10/high-availability/)
2. [High Availability Cluster: Concepts and Architecture](https://cloud.netapp.com/blog/cvo-blg-high-availability-cluster-concepts-and-architecture)
3. [Active-Active vs. Active-Passive High-Availability Clustering](https://www.jscape.com/blog/active-active-vs-active-passive-high-availability-cluster)
4. [High Availability vs Fault Tolerance: An Overview](https://www.liquidweb.com/kb/high-availability-vs-fault-tolerance/)
5. [High Availability vs. Fault Tolerance vs. Disaster Recovery](https://www.lunavi.com/blog/high-availability-vs-fault-tolerance-vs-disaster-recovery)
6. [Composing a Sharded MongoDB Cluster on Docker Containers](https://dzone.com/articles/composing-a-sharded-mongodb-on-docker)
7. [How To Use Sharding in MongoDB](https://www.digitalocean.com/community/tutorials/how-to-use-sharding-in-mongodb)
8. 
