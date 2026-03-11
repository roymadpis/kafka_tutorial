# Kafka Tutorial — Packet capture to Kafka

### Summary
- This repository demonstrates capturing network packets, sending them to Apache Kafka, and consuming/transforming those messages.
- It contains example producer and consumer Python scripts, topic creation helpers, and a docker-compose.yaml to run a local Kafka stack.

### Key files
- docker-compose.yaml — Kafka (and Zookeeper) compose setup
- CreateTopic.py — helper to create Kafka topics
- MyProducer.py / producer_sending_packets.py — examples that send messages to Kafka
- MyConsumer.py / consumer_reading_transformed_packets.py — examples that consume and transform messages
- config.yaml — runtime configuration

### Running the project
- See **RunningFilesGuide.md** for step-by-step instructions on environment setup and how to run the project (Docker, Python dependencies, and example commands).

### Prerequisites
- Python 3.10+, pip
- Docker and Docker Compose

#### For more details and examples, open RunningFilesGuide.md in this repository.

docker compose up --build
docker logs -f kafka_tutorial-packet-app-1