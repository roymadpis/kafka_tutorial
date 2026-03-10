import yaml
import CreateTopic
import MyProducer
import MyConsumer
import time

def log_message(message, log_path = "log.txt", verbose=True):
    
    if verbose:
        print(f"Received message: {message}")
    
    #### create log file if it doesn't exist and write the message to it
    with open(log_path, 'a') as log_file:
        ### write the current timestamp and the message to the log file
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
            
            
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
        log_message(message, log_path = "log_transformed_packets.txt", verbose=True)
        # Accessing your specific fields
        # print(f"Received message: {message}")   
    
    ### optional: we can see what topics are configured:
    #CreateTopic.list_existing_topics(bootstrap_servers = bootstrap_servers)
    

            
            