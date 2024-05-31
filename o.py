from flask import Flask, request, jsonify,render_template
from confluent_kafka import Producer, Consumer
import json
import uuid
import threading
import time
import random
from turbo_flask import Turbo

test_details={}
register_node=[]
driver_last_heartbeat = {}
app = Flask(__name__)
turbo= Turbo(app)
kafka_producer = Producer({'bootstrap.servers': 'localhost:9092'})
kafka_consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'orchestrator-group'
    # 'auto.offset.reset': 'latest'
})
test_config_topic = 'Test_config'
trigger_topic = 'Trigger'

metrics_topic = 'metrics'
heartbeat_topic = 'Heartbeat'
register_topic = 'Register'


class Orchestrator:
    def __init__(self):
        self.test_id = str(uuid.uuid4())
        self.driver_metrics = {}

    def publish_message(self, topic, message):
        kafka_producer.produce(topic, json.dumps(message).encode('utf-8'))
        kafka_producer.flush()

    def consume_metrics(self):
        kafka_consumer.subscribe([metrics_topic])
        test_id=' '
        report_id=' '
        nodes={}
        nodes = {}
        with app.app_context():
         while True:
            msg = kafka_consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                continue
            if msg.value().decode()=='EOT':
                break
            data = json.loads(msg.value().decode('utf-8'))
            print(data)
            if msg.topic() == metrics_topic:
                driver_id = data['node_id']
                if driver_id not in nodes.keys():
                    nodes[driver_id]=0
                metrics = data['metrics']
                nodes[driver_id]=metrics
                # self.driver_metrics[driver_id] = data['metrics']
                test_id=data['test_id']
                report_id = data['report_id']
                print(data)
                turbo.push(turbo.replace(render_template('Response.html',test_id=test_id,report_id=report_id,nodes=nodes),'load'))
        print(test_details)
        # test_details.pop(test_id)
        print('Test Over')
        return render_template('Response.html',test_id=test_id,report_id=report_id,nodes=nodes)
                
    def heartbeat(self):
        kafka_consumer2 = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'orchestrator-group1'
        })
        kafka_consumer2.subscribe([heartbeat_topic])
        while True:
            msg = kafka_consumer2.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                continue
            data = json.loads(msg.value().decode('utf-8'))
            print(data)
            if msg.topic==heartbeat_topic:
                driver_id = data['node_id']
                driver_last_heartbeat[driver_id] = time.time()


    def handle_load_test(self, config):
        # Publish test configuration to driver nodes
        self.publish_message(test_config_topic, config)
        test_details[config['test_id']]=config
        return jsonify({'message': 'Load test stored successfully'})

    def trigger_load_test(self,trigger_message):
        # Trigger the load test
        self.publish_message(trigger_topic, trigger_message)
        self.consume_metrics()
        return jsonify({'message':'Test Done'})

    def get_driver_metrics(self):
        return jsonify({'metrics': self.driver_metrics})

    def get_driver_status(self):
        current_time = time.time()
        status = {}

        for driver_id, last_heartbeat_time in self.driver_last_heartbeat.items():
            time_since_last_heartbeat = current_time - last_heartbeat_time
            status[driver_id] = {'last_heartbeat_time': last_heartbeat_time, 'status': 'alive' if time_since_last_heartbeat < 5 else 'dead'}

        return jsonify({'driver_status': status})
    
    def register_nodes(self):
        kafka_consumer1 = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'orchestrator-group2'
        })
        kafka_consumer1.subscribe([register_topic])
        while True:
            msg = kafka_consumer1.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                continue
            data = json.loads(msg.value().decode('utf-8'))
            print(data)
            if msg.topic==register_topic:
                register_node.append(data['node_id'])
def generate_uid():
    return f"{int(time.time() * 1000)}_{random.getrandbits(32)}"




            

orchestrator_instance = Orchestrator()


    

@app.route('/', methods=['GET','POST'])
def load_test():
    if request.method == 'POST':
        test_id = generate_uid()
        test_config = {
            "query":"create_test",
            "test_id": test_id,
            "test_type": request.form['test_type'],
            "test_message_delay": request.form['test_message_delay'],
            "message_count_per_driver": request.form['message_count_per_driver']
        }
        orchestrator_instance.handle_load_test(test_config)
    return render_template('Home.html',test_details=(test_details))

@app.route('/trigger/<test_id>',methods=['POST'])
def trigger_test(test_id):
    trigger_message = {
        "query":"trigger_test",
        "test_id": test_id,
        "trigger": "YES"
    }
    return orchestrator_instance.trigger_load_test(trigger_message)
    # return update_load()

@app.route('/metrics', methods=['GET'])
def get_metrics():
    return orchestrator_instance.get_driver_metrics()

@app.route('/status', methods=['GET'])
def get_status():
    return orchestrator_instance.get_driver_status()

@app.route('/register', methods=['POST'])
def register_node():
    node_info = request.get_json()
    orchestrator_instance.driver_last_heartbeat[node_info['node_id']] = time.time()
    return jsonify({'message': 'Node registered successfully'})

@app.route('/getTests',methods=['GET'])
def getTests():
    return jsonify(test_details)
@app.context_processor
def init():
    test_id=" "
    report_id=" "
    nodes={
        "metrics":0
    }
    return {'test_id':test_id,'report_id':report_id,'nodes':nodes}

if __name__ == '__main__':
    # Start Flask web server in a separate thread
    threading.Thread(target=lambda: app.run(port=5000)).start()

    # Start a thread to consume metrics
    threading.Thread(target=lambda: orchestrator_instance.heartbeat()).start()

    # Registering
    threading.Thread(target=lambda:orchestrator_instance.register_nodes()).start()
