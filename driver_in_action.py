import time
import yaml
import CreateTopic
import MyProducer
import MyConsumer
import MyDriver

if __name__ == '__main__':
    print("Running the main code")
    
    ############################################## Variables ##############################################
    # Load configurations from YAML file
    with open('config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    bootstrap_servers = config['bootstrap_servers']
    topic_name_packets_stream = config['topic_name_packets_stream']
    key_field_in_messages = config['key_field_in_messages']

    consumer_group_id = config['consumer_group_id']
    topic_name_transformed_packets = config['topic_name_transformed_packets']
    window_size_sec_for_consumer_buffer = config['window_size_sec_for_consumer_buffer']
    
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
    
    #################### TBDDD HERE I STOPEED
    my_driver.process_and_sort()
    
    
    
    
