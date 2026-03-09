
import random
import json
from datetime import datetime

def generate_random_message(color_list = ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'Orange', 'Cyan', 'Magenta']):
    
    # Constructing the message structure
    message = {
        "user_id": f"user_{random.randint(1, 100):02d}", # Formats as user_01, user_10, etc.
        "user_lucky_number": random.randint(1, 1000),
        "timestamp": datetime.now().isoformat(), # Standard ISO 8601 string
        "favorite_color": random.choice(color_list),
        "value": random.randint(0, 100000)
    }
    
    return message


def generate_list_messages(num_messages = 10, **args):
    msg_list = []
    for i in range(num_messages):
        msg_i = generate_random_message(**args)
        msg_list.append(msg_i)
        
    return msg_list


if __name__ == '__main__':
    # Test the generator
    new_msg = generate_random_message()
    print(json.dumps(new_msg, indent=4))
