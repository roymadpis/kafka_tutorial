import json
from confluent_kafka import Producer
from GenerateMessages import generate_list_messages
import pyshark

class MyProducer:
    def __init__(self, bootstrap_servers='localhost:9092', client_id='python-producer', packets_stream_interface:str = None):
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
            kafka_key = str(key).encode('utf-8') if key else None

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
 
 
    def stream_live_packets(self, topic):
        """
        Captures packets from the interface and sends them to a Kafka topic.
        """
        if not self.packets_stream_interface:
            raise ValueError(
                "No network interface provided. Please specify an interface when initializing MyProducer. "
                "Example: MyProducer(packets_stream_interface='Wi-Fi')"
            )
        
        interface = self.packets_stream_interface
        # Filter: Ignore traffic on port 9092 to prevent a feedback loop
        capture = pyshark.LiveCapture(
            interface=interface, 
            display_filter='tcp.port != 9092'
        )
        
        print(f"📡 Capturing on {interface}... Press Ctrl+C to stop.")
        
        try:
            for packet in capture.sniff_continuously():
                try:
                    packet_data = {
                        'timestamp': packet.sniff_timestamp,
                        'protocol': packet.highest_layer,
                        'length': int(packet.length),
                        'src_ip': packet.ip.src if hasattr(packet, 'ip') else "N/A",
                        'dst_ip': packet.ip.dst if hasattr(packet, 'ip') else "N/A",
                        'src_port': packet[packet.transport_layer].srcport if hasattr(packet, 'transport_layer') else None
                    }
                    
                    self.send_message(topic, packet_data, key=packet_data['src_ip'])
                    
                except AttributeError:
                    continue
        except KeyboardInterrupt:
            self.flush()

 
            
    def stream_packets(interface='חיבור מקומי- 2'):
        # Replace 'Wi-Fi' with the name of your Hotspot interface
        capture = pyshark.LiveCapture(interface=interface)
        
        print("Starting packet stream to Kafka...")
        
        for packet in capture.sniff_continuously():
            try:
                # Extract basic metadata for the dataset
                packet_data = {
                    'timestamp': packet.sniff_timestamp,
                    'protocol': packet.highest_layer,
                    'length': packet.length,
                    'source': packet.ip.src if hasattr(packet, 'ip') else "N/A",
                    'destination': packet.ip.dst if hasattr(packet, 'ip') else "N/A"
                }
                
                # Produce to Kafka
                producer.produce(
                    topic, 
                    key=packet_data['source'], 
                    value=json.dumps(packet_data), 
                    callback=delivery_report
                )
                producer.poll(0)
                
            except AttributeError:
                # Skip packets without IP layers (like ARP)
                continue

    def flush(self):
        """
        Wait for all messages in the producer queue to be delivered.
        """
        print("Cleaning up... flushing producer.")
        self.producer.flush()