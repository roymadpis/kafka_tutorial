import time
from typing import Callable, Iterable, Any, Optional

from MyProducer import MyProducer
from MyConsumer import MyConsumer


class MyDriver:
    def __init__(self, producer: Any, consumer: Any):
        """Initialize driver with a producer and a consumer instance."""
        self.producer = producer
        self.consumer = consumer

    def consume(self,
                topics: Optional[Iterable[str]] = None,
                callback: Optional[Callable[[dict, Any], None]] = None,
                timeout: float = 1.0):
        """
        Activate the consumer and process incoming messages.

        - topics: optional iterable of topic names to subscribe before consuming.
        - callback: optional function called for every message as callback(message, producer).
                    If no callback is provided, messages are printed.
        - timeout: poll timeout forwarded to consumer.consume_messages.
        """
        if topics:
            # ensure it's a list
            self.consumer.subscribe(list(topics))

        for message in self.consumer.consume_messages(timeout=timeout):
            if callback:
                try:
                    callback(message, self.producer)
                except Exception as e:
                    print(f"Error in callback: {e}")
            else:
                print(f"Consumed: {message}")

    def produce(self, topic: str, message_dict: dict, key: Optional[str] = None, verbose: bool = False):
        """Convenience wrapper to send a message using the driver's producer."""
        self.producer.send_message(topic, message_dict, key=key, verbose=verbose)


# --- Example usage ---
if __name__ == "__main__":
    import yaml

    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    prod = MyProducer(bootstrap_servers=config['bootstrap_servers'])
    unique_group = f"driver-group-{int(time.time())}"
    cons = MyConsumer(bootstrap_servers=config['bootstrap_servers'], group_id=unique_group)

    driver = MyDriver(prod, cons)
    driver.consume(topics=[config['topic_name_packets_stream']])
