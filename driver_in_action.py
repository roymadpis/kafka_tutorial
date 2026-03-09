import time
import yaml
import CreateTopic
import MyProducer
import MyConsumer
import MyDriver

# Define "Reduction" Functions
# we can create different strategies to reduce the number of packets we send each time through the producer

# Option 1: The "Aggregator" (1000 packets from 10 sessions ids -> 10 summaries of those sessions)
# This function looks at the whole buffer and returns a single summary of the traffic per session.
def aggregate_per_session(packet_list):
    if not packet_list:
        return []
    
    sessions = {}
    
    for packet in packet_list:
        sid = packet.get('session_id', 'unknown')
        
        if sid not in sessions:
            # Initialize entry for a new session
            sessions[sid] = {
                "session_id": sid,
                "first_seen": packet['timestamp'],
                "last_seen": packet['timestamp'],
                "packet_count": 0,
                "total_bytes": 0,
                "src_ip": packet.get('src_ip'),
                "dst_ip": packet.get('dst_ip'),
                "first_seq_num": packet.get('seq_num') if 'seq_num' in packet else None,
                "last_seq_num": packet.get('seq_num') if 'seq_num' in packet else None,
                "first_ack_num": packet.get('ack_num') if 'ack_num' in packet else None,
                "last_ack_num": packet.get('ack_num') if 'ack_num' in packet else None,
                "protocols": set()
            }
        
        # Update existing session data
        sess = sessions[sid]
        sess["packet_count"] += 1
        sess["total_bytes"] += packet.get('length', 0)
        sess["last_seen"] = packet['timestamp']
        sess["protocols"].add(packet.get('protocol'))
        # Update sequence and acknowledgment numbers if present
        if 'seq_num' in packet:
            sess["last_seq_num"] = packet['seq_num']
        if 'ack_num' in packet:
            sess["last_ack_num"] = packet['ack_num']

    # Convert sets to lists for JSON serialization before returning
    for sess in sessions.values():
        sess["protocols"] = list(sess["protocols"])
        
    return list(sessions.values())

# Option 2: The "Session Filter" (1000 packets -> ~10 session logs)
# This groups packets by session and only sends the "heaviest" or most recent state of each.
def summarize_by_session(packet_list):
    sessions = {}
    for p in packet_list:
        sid = p['session_id']
        if sid not in sessions:
            sessions[sid] = {"session_id": sid, "count": 0, "bytes": 0}
        sessions[sid]["count"] += 1
        sessions[sid]["bytes"] += p['length']
    return list(sessions.values())


def filter_small_packets(packet_list, size_threshold=500):
    # Only keep packets that are larger than the threshold
    return [p for p in packet_list if p['length'] > size_threshold]


if __name__ == '__main__':
    print("Running the main code")
    
    ############################################## Variables ##############################################
    # Load configurations from YAML file
    with open('config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    bootstrap_servers = config['bootstrap_servers']
    topic_name_packets_stream = config['topic_name_packets_stream']
    key_field_in_messages = config['key_field_in_messages']

    consumer_group_id = config['consumer_group_id']
    topic_name_transformed_packets = config['topic_name_transformed_packets']
    window_size_sec_for_consumer_buffer = config['window_size_sec_for_consumer_buffer']
    
    ############################################# Topic - transformed packets ##############################################
    ### step 1: create a topic - transformed_packets
    CreateTopic.create_topic(bootstrap_servers = bootstrap_servers,
                             topic_name = topic_name_transformed_packets,
                             num_partitions = 3, replication_factor=1)
    
    ############################################## Consumer - getting packets ##############################################
    # Initialize the driver
    my_producer = MyProducer.MyProducer(bootstrap_servers=bootstrap_servers)
    my_consumer = MyConsumer.MyConsumer(bootstrap_servers=bootstrap_servers,
                                     group_id=consumer_group_id)
    
    my_driver = MyDriver.MyDriver(my_producer = my_producer,
                                  my_consumer = my_consumer,
                                  source_topic = topic_name_packets_stream,
                                  target_topic = topic_name_transformed_packets,
                                  window_size_sec=window_size_sec_for_consumer_buffer)
    
    #################### Running the driver with different processing functions ####################
    my_driver.process_and_sort(process_func=aggregate_per_session, message_key='session_id')
    # my_driver.process_and_sort(process_func=summarize_by_session, message_key='session_id')
    
    
    
    