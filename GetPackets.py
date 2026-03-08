import CreateTopic
import MyProducer

import pyshark
from confluent_kafka import Producer
import json
import yaml

if __name__ == "__main__":

    ############################################## Variables ##############################################
    # Load configurations from YAML file
    with open('config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    bootstrap_servers = config['bootstrap_servers']
    topic_name_packets_stream = config['topic_name_packets_stream']
    key_field_in_messages = config['key_field_in_messages']

    ############################################## Topic - packets_stream1 ##############################################
    ### step 1: create a topic - packets_stream1
    CreateTopic.create_topic(bootstrap_servers = bootstrap_servers,
                             topic_name = topic_name_packets_stream,
                             num_partitions = 3, replication_factor=1)
    
    ### optional: we can see what topics are configured:
    #CreateTopic.list_existing_topics(bootstrap_servers = bootstrap_servers)

    ############################################## Producer ##############################################

    # Initialize
    producer = MyProducer.MyProducer(bootstrap_servers=bootstrap_servers)
    producer.send_list_of_messages(topic=topic_name_packets_stream, num_messages=10,
                                   key = key_field_in_messages,
                                   verbose=True)
    producer.flush()




# Kafka Configuration
conf = {'bootstrap.servers': "localhost:9092"}
producer = Producer(conf)
topic = "iphone-packets"

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")

def stream_packets():
    # Replace 'Wi-Fi' with the name of your Hotspot interface
    capture = pyshark.LiveCapture(interface='Local Area Connection* X')
    
    print("Starting packet stream to Kafka...")
    
    for packet in capture.sniff_continuously():
        try:
            # Extract basic metadata for the dataset
            packet_data = {
                'timestamp': packet.sniff_timestamp,
                'protocol': packet.highest_layer,
                'length': packet.length,
                'source': packet.ip.src if hasattr(packet, 'ip') else "N/A",
                'destination': packet.ip.dst if hasattr(packet, 'ip') else "N/A"
            }
            
            # Produce to Kafka
            producer.produce(
                topic, 
                key=packet_data['source'], 
                value=json.dumps(packet_data), 
                callback=delivery_report
            )
            producer.poll(0)
            
        except AttributeError:
            # Skip packets without IP layers (like ARP)
            continue

if __name__ == "__main__":
    stream_packets()
    producer.flush()



if __name__ == "__main__":
    import pyshark
    capture = pyshark.LiveCapture(interface='Wi-Fi')
    for packet in capture.sniff_continuously():
        print(packet)



