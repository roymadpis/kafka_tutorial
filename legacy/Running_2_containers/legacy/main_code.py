import CreateTopic
import GenerateMessages
import MyProducer
import MyConsumer
import time
import yaml

# Load configurations from YAML file
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

bootstrap_servers = config['bootstrap_servers']
topic_name_packets_stream = config['topic_name_packets_stream']
key_field_in_messages = config['key_field_in_messages']


if __name__ == '__main__':
    print("Running the main code")
    
    ############################################## Variables ##############################################

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

    ############################################## Consumer ##############################################
    # # Initialize Consumer
    # consumer = MyConsumer.MyConsumer(bootstrap_servers=bootstrap_servers, group_id='main-group')
    # consumer.subscribe([topic_name_packets_stream])

    # try:
    #     while True:
    #         # 2. Consume messages
    #         for message in consumer.consume_messages(timeout=1.0):
    #             print(f"Consumed message: {message}")

    # except KeyboardInterrupt:
    #     consumer.close()
    #     producer.flush()