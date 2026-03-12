import time
import yaml
import os
import sys
# Add the parent directory of the current file to the system path to allow importing from src_code
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src_code import MyConsumer
from src_code import CreateTopic
from src_code import MyProducer
from src_code import MyDriver
from helpers import utils


if __name__ == '__main__':
    print("Running the main code")
    
    ############################################## Variables ##############################################
    ### Load configurations from YAML file
    try:
        with open('/app/k8s/config-map.yaml', 'r') as f: # if we run in a container, the config map will be mounted at /app/config/config-map.yaml
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

    # bootstrap_servers = config_data.get('bootstrap_servers')
    topic_name_packets_stream = config_data.get('source_topic')
    consumer_group_id = config_data.get('consumer_group_id')
    consumer_group_id_transformed_packets = config_data.get('consumer_group_id_transformed_packets')
    topic_name_transformed_packets = config_data.get('transformed_topic')
    window_size_sec_for_consumer_buffer = config_data.get('window_size_sec')
    
    
    ############################################# Topic - transformed packets ##############################################
    ### step 1: create a topic - transformed_packets
    CreateTopic.create_topic(bootstrap_servers = bootstrap_servers,
                             topic_name = topic_name_transformed_packets,
                             num_partitions = 3, replication_factor=1)
    
    ############################################## Consumer - getting packets ##############################################
    # Initialize the driver
    my_producer = MyProducer.MyProducer(bootstrap_servers=bootstrap_servers)
    my_consumer = MyConsumer.MyConsumer(bootstrap_servers=bootstrap_servers,
                                     group_id=consumer_group_id)
    
    my_driver = MyDriver.MyDriver(my_producer = my_producer,
                                  my_consumer = my_consumer,
                                  source_topic = topic_name_packets_stream,
                                  target_topic = topic_name_transformed_packets,
                                  window_size_sec=window_size_sec_for_consumer_buffer)
    
    #################### Running the driver with different processing functions ####################
    my_driver.process_and_sort(process_func=None, message_key='session_id')
    # my_driver.process_and_sort(process_func=utils.aggregate_per_session, message_key='session_id')
    # my_driver.process_and_sort(process_func=utils.summarize_by_session, message_key='session_id')
    
    
    
    