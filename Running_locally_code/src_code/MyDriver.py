import time
from datetime import datetime
from confluent_kafka import Consumer, KafkaError, Producer
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
                ### also we need to check if the buffer is not empty, otherwise we might end up flushing empty buffers and sending empty messages to the next topic
                current_time = time.time()
                if current_time - self.last_flush_time >= self.window_size_sec and self.buffer:
                    self.flush_sorted_buffer(process_func = process_func, message_key=message_key)
                    self.last_flush_time = current_time ### reset the last flush time       
                
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
        # We use a dictionary where the key is a unique identifier (session + seq_num)
        # This automatically keeps only the first version of a retransmitted packet.
        deduplicated_dict = {}
        for msg in self.buffer:
            unique_id = (msg.get('session_id'), msg.get('seq_num'))
            # Logic: For every unique id (session_id + seq number) keep the first packet we saw
            if unique_id not in deduplicated_dict:
                deduplicated_dict[unique_id] = msg
                
        # Convert back to list of messages (but cleaned - without retransmitted packets)
        clean_buffer = list(deduplicated_dict.values())
        ### 2. sorting logic: per session id, we want to sort the packets by their seq number (if available) and then by their timestamp. This way, we can ensure that the packets are processed in the correct order
        clean_buffer.sort(key=lambda x: (
        x.get('session_id'), 
        x.get('seq_num', 0),            # Primary Sort: Protocol Order
        parse_timestamp(x['timestamp'])  # Secondary Sort: Time Order --> if seq number is not available
        ))
            
        
        # Calculate number of unique sessions --> just for print purposes, otherwise we don't need this 
        unique_sessions = {msg['session_id'] for msg in clean_buffer}
        num_sessions = len(unique_sessions)
        print(f"Sorting and flushing {len(clean_buffer)} packets across {num_sessions} unique sessions...")
       
        # 3. Apply a transformation function
        # If no function is provided, we default to sending the raw buffer
        if process_func:
            results = process_func(clean_buffer)
        else:
            results = clean_buffer

        # 4. Ensure results is a list so we can iterate (in the producer we iterate over a list of messages to send)
        if isinstance(results, dict):
            results = [results]

        ##### 4. group together messages with the same message id (=> session id = 4 touple)
        ## then "compress" all the messages with the same message id together into one message and send it to the next topic.
        # This way, we can ensure that all the messages with the same message id are processed together and we can also reduce the number of messages sent to the next topic.
        msg_dict_with_session_id_as_key = {}
        for msg in results:
            msg_session_id = msg['session_id']
            if msg_session_id not in msg_dict_with_session_id_as_key:
                msg_dict_with_session_id_as_key[msg_session_id] = []
            msg_dict_with_session_id_as_key[msg_session_id].append(msg)
            
        ### 5. now we have a dictionary where the key is the session id and
        # the value is a list of messages with that session id
        # We can then "compress" all the messages with the same session id together into
        # one message and send it to the next topic.
        
        print(
            f"\nIncoming number of packets: {len(clean_buffer)}. "
            f"Number of unique sessions: {len(msg_dict_with_session_id_as_key)}. "
            f"Sending {len(msg_dict_with_session_id_as_key)} compressed messages to next topic..."
        )
        
        for msg_session_id, msgs_list in msg_dict_with_session_id_as_key.items():
            compressed_msg = {
                "session_id": msg_session_id,
                "number_of_packets": len(msgs_list),
                "messages": msgs_list ### Roy: TBD --> here we can apply another compression using a compression library function to reduce the total bytes
            }
            
            self.my_producer.producer.produce(
                self.target_topic,
                key = compressed_msg['session_id'].encode('utf-8'),
                value = json.dumps(compressed_msg).encode('utf-8')
            )
        self.my_producer.flush()
        clean_buffer.clear()
        self.buffer.clear()
            
        
        
