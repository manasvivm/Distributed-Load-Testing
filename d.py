from confluent_kafka import Consumer, Producer
import json
import requests
import time
import uuid
import sys
import threading

print(sys.argv)
kafka_consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': f'group_{sys.argv[1]}',
    'auto.offset.reset': 'latest'
})
kafka_producer = Producer({'bootstrap.servers': 'localhost:9092'})
test_config_topic = 'Test_config'
trigger_topic = 'Trigger'

metrics_topic = 'metrics'
heartbeat_topic = 'Heartbeat'
register_topic = 'Register'
tests={}


class Driver:
    def __init__(self, node_id, node_ip):
        self.node_id = node_id
        self.node_ip = node_ip

    def publish_message(self, topic, message):
        kafka_producer.produce(topic, json.dumps(message).encode('utf-8'))
        kafka_producer.flush()

    def send_http_request(self):
        # Implement your HTTP request logic here
        response = requests.get('http://localhost:8080/ping')
        return response.elapsed.total_seconds() * 1000  # Convert to milliseconds

    def get_metrics(latency):
        mean = latency.mean()
        min = latency.min()
        max = latency.max()
        median = latency.median()

    def store_load_test(self,test_config):
        tests[test_config['test_id']]=test_config
        print(tests)


    def run_load_test(self, test_config):
        test_id = test_config['test_id']
        print('running ',test_id)
        test = tests[test_id]
        message_count_per_driver=int(test['message_count_per_driver'])
        test_type = test['test_type']
        test_message_delay = int(test['test_message_delay'])
        time.sleep(0.5)
        latency_list = []

        for i in range((message_count_per_driver)):

            latency = self.send_http_request()
            latency_list.append(latency)
            metrics_message = {
                'node_id': self.node_id,
                'test_id': test_id,
                'report_id': str(uuid.uuid4()),
                'metrics': {
                    'mean_latency': sum(latency_list) / len(latency_list),
                    'min_latency': min(latency_list),
                    'max_latency': max(latency_list),
                    'latency': latency

                }
            }

            

            self.publish_message(metrics_topic, metrics_message)
            

            if test_type == 'TSUNAMI' and test_message_delay > 0:
                time.sleep(test_message_delay)  # Convert to seconds
        kafka_producer.produce(metrics_topic,'EOT'.encode('utf-8'))
        print('Test ',test_id,' Over')
    def heartbeat(self):
        while True:
            heartbeat_message = {
                'node_id': self.node_id,
                'heartbeat': 'YES'
            }
            self.publish_message(heartbeat_topic, heartbeat_message)
            time.sleep(1)

    def register(self):
        register_message = {
            'node_id': self.node_id,
            'node_ip': self.node_ip,
            'message_type': 'DRIVER_NODE_REGISTER'
        }
        self.publish_message(register_topic,register_message)

    def driver(self):
        

        driver_instance = Driver(node_id, node_ip)

        #   Subscribe to the test_config and trigger topics
        kafka_consumer.subscribe([test_config_topic,trigger_topic])

        while True:
            msg = kafka_consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                continue

            data = json.loads(msg.value().decode('utf-8'))
            print(data)

            if msg.topic() == test_config_topic:
                driver_instance.store_load_test(data)
            if msg.topic()==trigger_topic:
                driver_instance.run_load_test(data)



if __name__ == '__main__':
    # Retrieve node_id and node_ip from command-line arguments
    node_id = sys.argv[1]
    node_ip = sys.argv[2]
    driver = Driver(node_id=node_id,node_ip=node_ip)
    driver.register()
    # Start Flask web server in a separate thread
    threading.Thread(target=lambda: driver.driver()).start()

    # Start a thread to consume metrics
    threading.Thread(target=lambda: driver.heartbeat()).start()
