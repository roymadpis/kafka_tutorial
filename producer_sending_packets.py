import CreateTopic
import MyProducer
import MyConsumer
import time
import yaml


if __name__ == '__main__':
    
    ############################################## Variables ##############################################
    # Load configurations from YAML file
    with open('config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    bootstrap_servers = config['bootstrap_servers']
    topic_name_packets_stream = config['topic_name_packets_stream']
    # key_field_in_messages = config['key_field_in_messages']
    packets_stream_interface = config['packets_stream_interface'] ### this is the name of the interface that will be used to capture the packets. You can find it in wireshark or in the output of "tshark -D" command. For example, it can be 'Wi-Fi' or 'Ethernet' or 'LAN2' or 'Adapter for loopback traffic capture' etc. Make sure to set it correctly according to your system and the traffic you want to capture.
    
    print(f"Running the producer that takes packets and send them to the kafka topic: {topic_name_packets_stream}")

    ############################################## Topic - packets_stream1 ##############################################
    ### step 1: create a topic - packets_stream1
    CreateTopic.create_topic(bootstrap_servers = bootstrap_servers,
                             topic_name = topic_name_packets_stream,
                             num_partitions = 3, replication_factor=1)
    
    ### optional: we can see what topics are configured:
    #CreateTopic.list_existing_topics(bootstrap_servers = bootstrap_servers)

    ############################################## Producer ##############################################
    producer = MyProducer.MyProducer(bootstrap_servers=bootstrap_servers)
    producer.stream_live_packets(topic=topic_name_packets_stream,
                                 packets_stream_interface=packets_stream_interface,
                               # interface_id=r'\Device\NPF_{5D2399F7-B526-469D-8252-82201272FE86}',
                                )
