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
        
    def process_and_sort(self, consumer_timeout:int = 1.0, process_func: callable = None, message_key='session_id'):
        self.my_consumer.subscribe([self.source_topic])
        # Log initialization info
        mode = f"Using function '{process_func.__name__}'" if process_func else "No filtering/aggregation"
        print(f"Sorting/flushing across unique sessions. {mode}. Key: {message_key}, Window: {self.window_size_sec} sec")
        try:
            while True:
                # poll for messages using the consumer generator
                msg = self.my_consumer.consumer.poll(timeout=consumer_timeout)
                
                ### if a msg was recieved, we decode it and add it to the buffer
                if msg is not None and not msg.error():
                    try:
                        msg_data = json.loads(msg.value().decode('utf-8'))
                        self.buffer.append(msg_data)
                    except Exception as e:
                        print(f"!!!!!!! Error decoding message: {e}")
                        
                elif msg is not None and msg.error():
                    if msg.error().code() != KafkaError._PARTITION_EOF:
                        print(f"!!!!!!! Consumer error: {msg.error()}")
                        
                # Check if the window has elapsed --> this is the buffer logic
                ### also check if the buffer is not empty, otherwise we might end up flushing empty buffers and sending empty messages to the next topic
                current_time = time.time()
                if current_time - self.last_flush_time >= self.window_size_sec and self.buffer:
                    self.flush_sorted_buffer(process_func = process_func, message_key=message_key)
                    self.last_flush_time = current_time ### recet the last flush time       
                
        except KeyboardInterrupt:
            print("\n -------> Stopping driver...")
            self.flush_sorted_buffer(process_func = process_func, message_key=message_key) # Final flush before exit
            self.my_consumer.close()
                

    def flush_sorted_buffer(self, process_func: callable = None, message_key='session_id'):
        # parsing timestamps in the format "2024-06-17T12:34:56.789Z" to datetime objects for accurate sorting
        def parse_timestamp(ts_str):
            clean_ts = ts_str.replace('Z', '')
            
            # Truncate nanoseconds to microseconds (6 digits after the dot)
            if '.' in clean_ts:
                base, fraction = clean_ts.split('.')
                clean_ts = f"{base}.{fraction[:6]}"
            
            # Parse using strptime
            return datetime.strptime(clean_ts, "%Y-%m-%dT%H:%M:%S.%f")
        
        if not self.buffer:
            return
        #####################################################################
        # 1. Deduplication (Handling Retransmissions)
        # We use a dictionary where the key is a unique identifier (session + seq)
        # This automatically keeps only the latest version of a retransmitted packet.
        deduplicated_dict = {}
        for msg in self.buffer:
            unique_id = (msg.get('session_id'), msg.get('seq'))
            # Logic: For every unique id (session_id + seq number) keep the first packet we saw
            if unique_id not in deduplicated_dict:
                deduplicated_dict[unique_id] = msg
                
        # Convert back to list
        clean_buffer = list(deduplicated_dict.values())
        ### sorting logic: per session id, we want to sort the packets by their seq number (if available) and then by their timestamp. This way, we can ensure that the packets are processed in the correct order
        clean_buffer.sort(key=lambda x: (
        x.get('session_id'), 
        x.get('seq', 0),            # Primary Sort: Protocol Order
        parse_timestamp(x['timestamp'])  # Secondary Sort: Time Order
        ))
            
        
        # Calculate unique sessions using a set comprehension
        unique_sessions = {msg['session_id'] for msg in clean_buffer}
        num_sessions = len(unique_sessions)
        print(f"Sorting and flushing {len(clean_buffer)} packets across {num_sessions} unique sessions...")
       
        # Apply the transformation function
        # If no function is provided, we default to sending the raw buffer
        if process_func:
            results = process_func(clean_buffer)
        else:
            results = clean_buffer

        # 3. Ensure results is a list so we can iterate
        if isinstance(results, dict):
            results = [results]

        # 4. Produce the output
        for msg in results:
            payload = json.dumps(msg).encode('utf-8')
            # Use session_id if available, otherwise no key
            key = msg.get(message_key, '').encode('utf-8') if message_key in msg else None
            
            self.my_producer.producer.produce(
                self.target_topic, 
                key=key, 
                value=payload
            )
        self.my_producer.flush()
        clean_buffer.clear()
        self.buffer.clear()
        
        
