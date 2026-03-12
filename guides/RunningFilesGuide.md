### Step 0 - Setup

#### Part 1: Kafka server --> need to setup a kafka server
- Need to create a `docker-compose.yaml` --> you can use chatGPT for that
- Make sure you have the following lines:
      # Broker configurations for single broker setup
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_OFFSETS_TOPIC_NUM_PARTITIONS: 1
      KAFKA_DEFAULT_REPLICATION_FACTOR: 1
      KAFKA_MIN_INSYNC_REPLICAS: 1
- Run in the terminal: `docker compose up -d` => Runs containers in detached mode (in the background).
- run `docker ps` in the terminal to make sure the docker container is up and ready to use

- run in the terminal the following command to make sure the driver is working as expected:
      -  docker logs -f kafka_tutorial-packet-app-1

#### Part 2: Route packets from iphone through PC 
- To enable sniffing packets:
- 1. go to services.msc --> services --> internet connection sharing --> right click --> restart
- 2. Go to settings in your pc --> Network & Internet --> Mobile hotspot --> on (share over WIFI) --> connect to that hotspot through phone
- 3. In iphone: connect to the PC hotspot

### Step 3:
+ Run in another terminal: `consumer_reading_transformed_packets.py`

- This runs a consumer that reads the transformed packets from the topic: `topic_name_transformed_packets`