from confluent_kafka.admin import AdminClient, NewTopic

def create_topic(bootstrap_servers, topic_name, num_partitions, replication_factor):
    admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})
    
    # Define topic: name, number of partitions, and replication factor
    topic = NewTopic(topic_name, num_partitions=num_partitions, replication_factor=replication_factor)
    
    fs = admin_client.create_topics([topic])

    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print(f"Topic '{topic}' created successfully.")
        except Exception as e:
            print(f"Failed to create topic '{topic}': {e}")

# create_topic(bootstrap_servers = 'localhost:9092', topic_name = 'roy_topic1',
#              num_partitions = 3, replication_factor=1)
 
def list_existing_topics(bootstrap_servers):
    # Initialize the AdminClient
    admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})
    
    # Fetch cluster metadata
    metadata = admin_client.list_topics(timeout=10)
    
    print("Existing Kafka Topics:")
    print("-" * 30)
    
    # metadata.topics is a dict where keys are topic names
    for topic_name in metadata.topics:
        print(f" - {topic_name}")

# Usage
# list_existing_topics(bootstrap_servers = 'localhost:9092')

