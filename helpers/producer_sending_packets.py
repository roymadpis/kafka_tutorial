
import time
import yaml
import os
import sys
# Add the parent directory of the current file to the system path to allow importing from src_code
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src_code import MyConsumer
from src_code import CreateTopic
from src_code import MyProducer

if __name__ == '__main__':
    
    ############################################## Variables ##############################################
    ### Load configurations from YAML file
    try:
        with open('/app/k8s/config-map.yaml', 'r') as f: # if we run in kubernetes, the config map will be mounted at /app/config/config-map.yaml
            config_map = yaml.safe_load(f)
            config_data = config_map.get('data') 
            config_data = yaml.safe_load(config_data['config.yaml'])
            bootstrap_servers = config_data.get('bootstrap_servers')

    except:
        with open('k8s/config-map.yaml', 'r') as config_file: # if we run locally, the config map will be at k8s/config-map.yaml
            config_map = yaml.safe_load(config_file)
            config_data = config_map.get('data') 
            config_data = yaml.safe_load(config_data['config.yaml'])
            bootstrap_servers = config_data.get('bootstrap_servers_local')

    topic_name_packets_stream = config_data.get('source_topic')
    packets_stream_interface = config_data.get('packets_stream_interface')
    
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
