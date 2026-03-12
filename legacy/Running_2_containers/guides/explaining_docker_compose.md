### 1. The Orchestrator: docker-compose.yaml
- A Docker Compose file is a configuration file, usually named docker-compose.yml, that allows you to define and run multi-container applications.
- In our case we want to define 2 containers:
    - 1. kafka server --> KRaft
    - 2. Our application container: the one that will run `driver_in_action.py`
- The advantage of using docker-compose rather then having 2 different dockerfiles and running them separately: When we run two containers separately via docker run, **they can't "see" each other unless we manually create a bridge network and link them.**
- Therefore the container of our app ( that runs `driver_in_action.py`) won't have access to the kafka server unless we use docker-compose (or configure the network).
- It ensures that our app (that is defined in the Dockerfile --> the `driver_in_action.py`) and the infrastructure it needs (Kafka) can talk to each other on a private virtual network.

#### The Kafka Service
- Our Kafka configuration is using **KRaft** (Kafka Raft) settings.
- `KAFKA_LISTENER_SECURITY_PROTOCOL_MAP`: This is a translator. It tells Kafka how to handle different types of traffic (e.g., "Internal traffic is PLAINTEXT, External is also PLAINTEXT").
    - In PLAINTEXT mode, data is sent over the network exactly as it is. If you send a message like "Hello World", anyone with access to the network sniffing the traffic (using a tool like the tshark we included in our Dockerfile) would be able to read that exact string. It is the opposite of SSL/TLS encryption.

- `KAFKA_LISTENERS` vs `KAFKA_ADVERTISED_LISTENERS`: This is the most common "gotcha" in Kafka.

    - `KAFKA_LISTENERS`: What ports the **Kafka** process is listening on inside the container.
    - `KAFKA_ADVERTISED_LISTENERS`: What address Kafka tells clients to use. Notice localhost:9092 is for us (on our host machine), while kafka:9094 is for our packet-app container.

- `KAFKA_PROCESS_ROLES`: 'broker,controller': This tells this single container to act as both the data storage (broker) and the cluster manager (controller).


#### The Packet-App Service
- `depends_on`: Ensures the **Kafka container** starts *before* our **app** attempts to connect.
- `volumes`: This maps a file from our local  computer (./k8s/config-map.yaml) directly into the container. This is likely used for configuration settings our Python code needs to read at runtime.

### 2. The Blueprint: Dockerfile
- The **Dockerfile** builds the environment where our Python code lives. we use python:3.12-slim, which is a "best practice" choice—it's lightweight but functional.

### Further explanation of how everything works together:
- The secret lies in the `KAFKA_ADVERTISED_LISTENERS` setting. Here is exactly what is happening when we run the script locally.

1. The "Two-Door" StrategyThink of your Kafka container as a room with two different doors.
    - Door A (Port 9094): Faces inside the Docker "building"
    - Door B (Port 9092): Faces outside to your Host Machine.When your Python script (running on your PC/Host) connects to localhost:9092, it enters through Door B.2. Which server is it sending to?Your script is sending to the Kafka container, but it is using the PLAINTEXT_HOST listener.In your docker-compose.yaml, look at this line:KAFKA_ADVERTISED_LISTENERS: 'PLAINTEXT://kafka:9094,PLAINTEXT_HOST://localhost:9092'When you run locally (on your PC): Your code connects to localhost:9092. Kafka says: "Ah, you're coming from the outside. Use the PLAINTEXT_HOST rules."When your packet-app runs (inside Docker): It connects to kafka:9094. Kafka says: "You're a fellow container. Use the internal PLAINTEXT rules."Both lead to the exact same Kafka engine and the exact same storage. The data isn't being "moved" between servers; it's being sent to the same process via different "addresses."3. How is it accessible in the container?Because Docker maps the ports. When you defined:YAMLports:
  - "9092:9092"
You told your computer: "Anything that hits my PC's port 9092 should be tunneled directly into the Kafka container's port 9092."Your Hotspot/Phone sends data $\rightarrow$ PC.producer_sending_packets.py (on PC) sends data $\rightarrow$ localhost:9092.Docker intercepts 9092 $\rightarrow$ forwards it into the Kafka Container.Kafka stores the message in its internal logs.packet-app (inside Docker) asks for data from kafka:9094.Kafka pulls that same message from its logs and hands it to the app.
