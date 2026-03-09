import time
from datetime import datetime
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

    def process_and_sort(self, process_func: callable = None):
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
                        self.flush_sorted_buffer(process_func = process_func)
                        self.last_flush_time = current_time
                
                # If consume_messages yields nothing (timeout), still check if we need to flush
                if time.time() - self.last_flush_time >= self.window_size_sec:
                    self.flush_sorted_buffer(process_func = process_func)
                    self.last_flush_time = time.time()

        except KeyboardInterrupt:
            self.flush_sorted_buffer(process_func = process_func) # Final flush before exit
            self.close()

    def flush_sorted_buffer(self, process_func: callable = None):
        if not self.buffer:
            return
        
        # Calculate unique sessions using a set comprehension
        unique_sessions = {msg['session_id'] for msg in self.buffer}
        num_sessions = len(unique_sessions)
        print(f"📦 Sorting and flushing {len(self.buffer)} packets across {num_sessions} unique sessions...")
       
        # Sort by session_id first, then by timestamp
        # Note: timestamp is a string from pyshark, ensure it's float-compatible
        def parse_timestamp(ts_str):
            # Example input: '2026-03-08T15:25:17.716457900Z'
            # 1. Remove 'Z'
            clean_ts = ts_str.replace('Z', '')
            
            # 2. Truncate nanoseconds to microseconds (6 digits after the dot)
            # Most Python datetime parsers only handle up to 6 digits.
            if '.' in clean_ts:
                base, fraction = clean_ts.split('.')
                clean_ts = f"{base}.{fraction[:6]}"
            
            # 3. Parse using strptime
            return datetime.strptime(clean_ts, "%Y-%m-%dT%H:%M:%S.%f")
        
        # Sort by session_id, then by the parsed datetime object
        self.buffer.sort(key=lambda x: (x['session_id'], parse_timestamp(x['timestamp'])))

        # 2. Apply the transformation function
        # If no function is provided, we default to sending the raw buffer
        if process_func:
            results = process_func(self.buffer)
        else:
            results = self.buffer

        # 3. Ensure results is a list so we can iterate
        if isinstance(results, dict):
            results = [results]

        # 4. Produce the output
        for msg in results:
            payload = json.dumps(msg).encode('utf-8')
            # Use session_id if available, otherwise no key
            key = msg.get('session_id', '').encode('utf-8') if 'session_id' in msg else None
            
            self.my_producer.producer.produce(
                self.target_topic, 
                key=key, 
                value=payload
            )
        
        self.my_producer.flush()
        self.buffer.clear()
        
        
