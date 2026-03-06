import json
from confluent_kafka import Producer
from GenerateMessages import generate_list_messages

class MyProducer:
    def __init__(self, bootstrap_servers='localhost:9092', client_id='python-producer'):
        """
        Initializes the Kafka Producer.
        """
        conf = {
            'bootstrap.servers': bootstrap_servers,
            'client.id': client_id,
            # Standard optimization: wait 5ms to batch messages together
            'linger.ms': 5 
        }
        self.producer = Producer(conf)

    def delivery_report(self, err, msg):
        """
        Callback triggered by poll() to report success or failure.
        """
        if err is not None:
            print(f'❌ Delivery failed: {err}')
        else:
            print(f'✅ Delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')

    def send_message(self, topic, message_dict, key=None, verbose=False):
        """
        Serializes a dictionary to JSON and sends it to Kafka.
        """
        try:
            # Convert dict to JSON bytes
            payload = json.dumps(message_dict).encode('utf-8')
            
            # If a key is provided, encode it as well
            # kafka_key = str(key).encode('utf-8') if key else None
            kafka_key = key
            if verbose:
                print(f"Sending message to topic '{topic}': {message_dict}")

            self.producer.produce(
                topic, 
                key=kafka_key, 
                value=payload, 
                callback=self.delivery_report
            )
            
            # poll(0) serves delivery callbacks from previous produce calls
            self.producer.poll(0)
            
        except BufferError:
            print(f"Local queue full ({len(self.producer)} messages awaiting delivery)")
            self.producer.poll(0.1)
        except Exception as e:
            print(f"Error producing message: {e}")

    def send_list_of_messages(self, topic, key, num_messages=10, verbose=False, **args):
        """
        Generates a list of messages using generate_list_messages and sends them to Kafka.
        """
        messages = generate_list_messages(num_messages, **args)
        for message in messages:
            self.send_message(topic = topic, message_dict = message,
                              key = key, verbose=verbose)

    def flush(self):
        """
        Wait for all messages in the producer queue to be delivered.
        """
        print("Cleaning up... flushing producer.")
        self.producer.flush()