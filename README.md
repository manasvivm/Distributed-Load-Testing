# Distributed Load Testing Orchestrator

This repository contains a set of Python scripts and an HTML template for orchestrating distributed load testing. The system utilizes Flask for web application functionality, Confluent Kafka for communication between components, and Turbo-Flask for real-time updates.<br>


![image](https://github.com/Cloud-Computing-Big-Data/EC-Team-44-Distributed-Load-Testing-System/assets/106965125/2cd699c4-befb-4137-a86f-d0d507bb78b1)

## Contents

1. [**o.py**](o.py): Flask application serving as the orchestrator for distributed load testing.

2. [**d.py**](d.py): Load testing driver script that simulates load by sending HTTP requests.
 
3. [**server.py**](server.py):  Flask application with two routes: /ping (GET) responds with 'PONG', and /metrics (GET) returns mock metrics in JSON format.

4. [**topic_setup.py**](topic_setup.py): To create Kafka topics named 'metrics', 'Test_config', 'Trigger', 'Heartbeat', and 'Register'.
   
5. [**Home.html**](templates/Home.html): HTML code displaying a Bootstrap-themed web page for a load testing orchestrator.

6. [**Response.html**](templates/Response.html): HTML template for displaying load test metrics.

## Setup and Requirements

### Prerequisites

- Python 3.x
- Flask
- Confluent Kafka
- Turbo-Flask
- Additional dependencies as specified in the code

### Installation

1. **Clone the repository:**

```bash
git clone https://github.com/your-username/distributed-load-testing.git
```
2. **Install dependencies:**

bash

```
pip install -r requirements.txt
```
### Usage
  <h3>1.Start Kafka Broker:</h3>
  
  Make sure the Kafka broker is running on localhost:9092 or update the broker address in the code.


<h3>2.Run Orchestrator:</h3>

bash
```
python o.py
```
The orchestrator serves the web application on http://localhost:5000/.


<h3>3.Run Driver:</h3>

bash
```
python d.py <node_id> <node_ip>
```
Replace <node_id> and <node_ip> with the respective values for the load testing driver.


<h3>4.Access Web Interface:</h3>

Open your web browser and go to http://localhost:5000/ to access the orchestrator's interface.


<h3>5.Configure Load Test:</h3>

Choose the test type, set message delay, and define the message count per driver.


<h3>6.Trigger Load Test:</h3>

Submit the configuration to trigger the load test.


<h3>7.View Metrics:</h3>

Metrics are displayed on the web interface in real-time.


## Additional Information

The system uses Kafka topics **(te, tr, METRICS2, h, r)** for communication between orchestrator and driver nodes.

Ensure proper Kafka and Turbo-Flask configurations in the code.

The HTML template **(Response.html)** provides a clear representation of load test metrics.
