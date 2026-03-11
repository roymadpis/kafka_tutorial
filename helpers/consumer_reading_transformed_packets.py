import os
import sys
import time
import yaml

# Add the parent directory of the current file to the system path to allow importing from src_code
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src_code import MyConsumer
from src_code import CreateTopic
from src_code import MyProducer

def log_message(message, log_path = None, verbose=True):
    if log_path is None:
        # place logs in <repo_root>/logs/log_transformed_packets.txt
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "log_transformed_packets.txt")
    
    if verbose:
        print(f"Received message: {message}")
    
    #### create log file if it doesn't exist and write the message to it
    with open(log_path, 'a') as log_file:
        ### write the current timestamp and the message to the log file
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
            
            
if __name__ == '__main__':
    print("Running the main code")
    
    ############################################## Variables ##############################################
    ### Load configurations from YAML file
    try:
        with open('/app/config/config-map.yaml', 'r') as f: # if we run in kubernetes, the config map will be mounted at /app/config/config-map.yaml
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
    consumer_group_id_transformed_packets = config_data.get('consumer_group_id_transformed_packets')
    topic_name_transformed_packets = config_data.get('transformed_topic')
    
    ############################################## Consumer - getting packets ##############################################
    # Initialize Consumer
    consumer = MyConsumer.MyConsumer(bootstrap_servers=bootstrap_servers,
                                     group_id=consumer_group_id_transformed_packets)
    
    
    consumer.subscribe([topic_name_transformed_packets])
    print(f"Waiting for messages in {topic_name_transformed_packets}...")
    
    for message in consumer.consume_messages(timeout=2.0):
        log_message(message, log_path = 'logs/log_transformed_packets.txt', verbose=True)
        # Accessing your specific fields
        # print(f"Received message: {message}")   
    
    ### optional: we can see what topics are configured:
    #CreateTopic.list_existing_topics(bootstrap_servers = bootstrap_servers)
    

            
            