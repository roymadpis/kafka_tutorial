
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
