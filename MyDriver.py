import time
from confluent_kafka import Consumer, KafkaError, Producer
import MyConsumer
import MyProducer
import json

class MyDriver():
    def __init__(self, my_producer, my_consumer, source_topic, target_topic, window_size_sec=5):
        self.source_topic = source_topic
        self.target_topic = target_topic
        self.window_size_sec = window_size_sec
        self.buffer = []
        self.last_flush_time = time.time()
        self.my_producer = my_producer
        self.my_consumer = my_consumer

    def process_and_sort(self):
        """
        Consumes messages, buffers them for X seconds, sorts, and publishes.
        """
        self.my_consumer.subscribe([self.source_topic])
        print(f"🚀 Sorting service started. Window: {self.window_size_sec}s")

        try:
            while True:
                # Use the generator from the base class
                for msg_data in self.my_consumer.consume_messages(timeout=1.0):
                    self.buffer.append(msg_data)

                    # Check if the window has elapsed
                    current_time = time.time()
                    if current_time - self.last_flush_time >= self.window_size_sec:
                        self.flush_sorted_buffer()
                        self.last_flush_time = current_time
                
                # If consume_messages yields nothing (timeout), still check if we need to flush
                if time.time() - self.last_flush_time >= self.window_size_sec:
                    self.flush_sorted_buffer()
                    self.last_flush_time = time.time()

        except KeyboardInterrupt:
            self.flush_sorted_buffer() # Final flush before exit
            self.close()

    def flush_sorted_buffer(self):
        if not self.buffer:
            return

        print(f"Sorting and flushing {len(self.buffer)} messages...")

        # Sort by session_id first, then by timestamp
        # Note: timestamp is a string from pyshark, ensure it's float-compatible
        self.buffer.sort(key=lambda x: (x['session_id'], float(x['timestamp'])))

        for msg in self.buffer:
            payload = json.dumps(msg).encode('utf-8')
            # Use session_id as the key to ensure affinity in the new topic
            self.my_producer.produce(
                self.target_topic, 
                key=msg['session_id'].encode('utf-8'), 
                value=payload
            )
        
        self.my_producer.flush()
        self.buffer.clear()