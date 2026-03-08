import json
import yaml
from confluent_kafka import Consumer, KafkaError
import time
# Load configurations from YAML file
# with open('config.yaml', 'r') as config_file:
#     config = yaml.safe_load(config_file)

class MyConsumer:
    def __init__(self, bootstrap_servers, group_id='my-data-group'):
        """
        Initializes the Kafka Consumer.
        group_id: Multiple consumers with the same ID will share the load.
        """
        conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest', # Read from the start if no previous offset exists
            'enable.auto.commit': True      # Automatically tell Kafka we've read the message
        }
        self.consumer = Consumer(conf)

    def subscribe(self, topics):
        """Subscribe to a list of topics."""
        self.consumer.subscribe(topics)
        print(f"📥 Subscribed to topics: {topics}")

    def consume_messages(self, timeout=1.0):
        """
        A generator that polls for messages, decodes the JSON, and yields them.
        """
        try:
            while True:
                msg = self.consumer.poll(timeout)

                if msg is None:
                    continue  # No message received within timeout
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event - not an error
                        continue
                    else:
                        print(f"❌ Consumer error: {msg.error()}")
                        break

                # Decode the message value from bytes to JSON
                try:
                    data = json.loads(msg.value().decode('utf-8'))
                    yield data
                except Exception as e:
                    print(f"⚠️ Error decoding message: {e}")

        except KeyboardInterrupt:
            print("\n🛑 Stopping consumer...")
        finally:
            self.close()

    def close(self):
        """Close the consumer connection."""
        self.consumer.close()

# --- Example Usage ---
if __name__ == "__main__":
    
    with open('config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    bootstrap_servers = config['bootstrap_servers']
    topic_name_packets_stream = config['topic_name_packets_stream']
    key_field_in_messages = config['key_field_in_messages']
        
    
    # consumer = MyConsumer(bootstrap_servers=bootstrap_servers, group_id='test-group-1')
    # consumer.subscribe([topic_name_packets_stream])
    # Use a unique group ID for testing to bypass old "bookmarks"
    
    unique_group = f"test-group-{int(time.time())}"
    
    print(f"Connecting to {config['bootstrap_servers']}...")
    
    consumer = MyConsumer(
        bootstrap_servers=config['bootstrap_servers'], 
        group_id=unique_group
    )
    consumer.subscribe([config['topic_name_packets_stream']])

    print(f"Waiting for messages in {config['topic_name_packets_stream']}...")
    
    for message in consumer.consume_messages(timeout=2.0):
        # Accessing your specific fields
        print(f"Received message: {message}")   
        # user = message.get('user_id')
        # lucky_num = message.get('user_lucky_number')
        # color = message.get('favorite_color')
        # print(f"👤 {user} | 🎲 Lucky: {lucky_num} | 🎨 Color: {color}")