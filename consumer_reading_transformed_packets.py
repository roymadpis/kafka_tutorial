import yaml
import CreateTopic
import MyProducer
import MyConsumer

if __name__ == '__main__':
    print("Running the main code")
    
    ############################################## Variables ##############################################
    # Load configurations from YAML file
    with open('config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    bootstrap_servers = config['bootstrap_servers']
    #topic_name_packets_stream = config['topic_name_packets_stream']
    # key_field_in_messages = config['key_field_in_messages']
    
    consumer_group_id_transformed_packets = config['consumer_group_id_transformed_packets']
    topic_name_transformed_packets = config['topic_name_transformed_packets']
    
    ############################################## Consumer - getting packets ##############################################
    # Initialize Consumer
    consumer = MyConsumer.MyConsumer(bootstrap_servers=bootstrap_servers,
                                     group_id=consumer_group_id_transformed_packets)
    
    
    consumer.subscribe([topic_name_transformed_packets])
    print(f"Waiting for messages in {topic_name_transformed_packets}...")
    
    for message in consumer.consume_messages(timeout=2.0):
        # Accessing your specific fields
        print(f"Received message: {message}")   
    

    
    ### optional: we can see what topics are configured:
    #CreateTopic.list_existing_topics(bootstrap_servers = bootstrap_servers)