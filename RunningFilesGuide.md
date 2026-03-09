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

#### Part 2: Route packets from iphone through PC 
- To enable sniffing packets:
- 1. go to services.msc --> services --> internet connection sharing --> right click --> restart
- 2. Go to settings in your pc --> Network & Internet --> Mobile hotspot --> on (share over WIFI) --> connect to that hotspot through phone
- 3. In iphone: connect to the PC hotspot

#### That's it the setup is ready


### Step 1:
+ Run in the terminal: `producer_sending_packets.py`
- This runs the code that reads the packes from the phone and sends them to the topic configured in the config.yaml file

### Step 2:
+ Run in another terminal: `driver_in_action.py`

This runs the driver code:
- Definnig a driver (consumer + producer)
- The consumer reads the packets in the topic the producer (from step 1) is sending data to
- In the driver_in_action.py file we define a function that determines how to filter/aggregate the incoming packets
- we have a variable (configured also in the config.yaml): `window_size_sec_for_consumer_buffer` that determines how many seconds to wait to get packets

- The producer is taking the output from the filter/aggregation function and sends the data to another topic
- The topic is confifured in the config.yaml file: `topic_name_transformed_packets`

### Step 3:
+ Run in another terminal: `consumer_reading_transformed_packets.py`

- This runs a consumer that reads the transformed packets from the topic: `topic_name_transformed_packets`