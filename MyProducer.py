import json
from confluent_kafka import Producer
from GenerateMessages import generate_list_messages
import pyshark

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
        self.packet_id_counter = 0
        
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
 
 
    def stream_live_packets(self, topic, packets_stream_interface):
        # Filter: Ignore Kafka traffic and capture only IP/TCP
        capture = pyshark.LiveCapture(
            interface=packets_stream_interface, 
            display_filter='tcp.port != 9092',
            include_raw=False,
            use_json=True
        )
        
        print(f"📡 Capturing on {packets_stream_interface}... Press Ctrl+C to stop.")
        
        try:
            for packet in capture.sniff_continuously():
                try:
                    # Check for IP and TCP layers safely
                    if not ('IP' in packet and 'TCP' in packet):
                        continue

                    self.packet_id_counter += 1
                    
                    packet_data = {
                        'id': self.packet_id_counter,
                        'session_id': f"{packet.ip.src}:{packet.tcp.srcport}_{packet.ip.dst}:{packet.tcp.dstport}",
                        'timestamp': packet.sniff_timestamp,
                        'protocol': packet.highest_layer,
                        'length': int(packet.length),
                        'src_ip': packet.ip.src,
                        'dst_ip': packet.ip.dst,
                        'src_port': packet.tcp.srcport,
                        'dst_port': packet.tcp.dstport,
                        'tcp_flags': getattr(packet.tcp, 'flags', None),
                        'win_size': getattr(packet.tcp, 'window_size_value', None),
                    }

                    # Send with src_ip as key to maintain order per host
                    self.send_message(topic, packet_data, key=packet_data['src_ip'])
                    
                except AttributeError:
                    # Skip packets with missing expected fields
                    continue
        except KeyboardInterrupt:
            print("\nStopping capture...")
        finally:
            self.flush()


    def flush(self):
        """
        Wait for all messages in the producer queue to be delivered.
        """
        print("Cleaning up... flushing producer.")
        self.producer.flush()