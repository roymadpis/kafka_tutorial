
import CreateTopic
from confluent_kafka.admin import AdminClient, NewTopic

if __name__ == '__main__':
    print("Running the main code")
    bootstrap_servers = 'localhost:9092'
    
    ### step 1: create a topic - packets_stream1
    topic_name_packets_stram = "packets_stream1"
    CreateTopic.create_topic(bootstrap_servers = bootstrap_servers,
                             topic_name = topic_name_packets_stram,
                             num_partitions = 3, replication_factor=1)
    
    ### optional: we can see what topics are configured:
    #CreateTopic.list_existing_topics(bootstrap_servers = bootstrap_servers)



