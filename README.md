# Kafka Tutorial — Packet capture to Kafka

### Summary
- This repository demonstrates capturing network packets, sending them to Apache Kafka, and consuming/transforming those messages.
- It contains example producer and consumer Python scripts, topic creation helpers, and a docker-compose.yaml to run a local Kafka stack.

### How to run the files?
+ Step 1: run in the terminal: `docker compose up -d` => Runs containers in detached mode (in the background).
    - This command creates 2 containes:
        - 1. kafka server --> KRaft
        - 2. Our application container: the one that will run `driver_in_action.py`
+ Step 2: sniff packets:
    - To enable sniffing packets:
    - 1. go to services.msc --> services --> internet connection sharing --> right click --> restart
    - 2. Go to settings in your pc --> Network & Internet --> Mobile hotspot --> on (share over WIFI) --> connect to that hotspot through phone
    - 3. In iphone: connect to the PC hotspot
    - 4. In your computer need to figure out the network you are connected to:
        - Open Wireshark on your PC.
        - You will see a list of interfaces. Look for one named something like "Local Area Connection X"* or "Microsoft Wi-Fi Direct Virtual Adapter." You should see activity spikes on this interface when you use your phone.
        - Copy the name of that interface
        - Open k8s/config-map.yaml and put the interface name in the variable: `packets_stream_interface`
+ Step 3: Run the producer that sniff the packets:
    - Run in another terminal: `py helpers/producer_sending_packets.py`
    - This will start a producer that sniff packets from the phone (Through the selected interface) and send them to the `source_topic` (that its name is defined in the k8s/config-map.yaml under the variable: `source_topic`)

+ Step 4: run in the terminal the following command to make sure the driver is working as expected:
      -  `docker logs -f kafka_tutorial-packet-app-1`
      - Explanation: when we ran earlier `docker compose up -d` we started 2 containers, both the kafka server and the app container that reads messages from the `source topic` and does some manipulation on them (and send them over to a new topic: `transformed_topic`)

+ Step 5: reading the transformed packets from the `transformed_topic`:
    - Run in another terminal: `py helpers/consumer_reading_transformed_packets.py`



### Running the project
- See **guides/RunningFilesGuide.md** for more instructions on environment setup and how to run the project (Docker, Python dependencies, and example commands).

### Prerequisites
- Python 3.10+, pip
- Docker and Docker Compose
