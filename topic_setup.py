from kafka import KafkaAdminClient
from kafka.admin import NewTopic

bootstrap_servers = 'localhost:9092'  # Replace with your Kafka broker's address

admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)

# Create a NewTopic object with the topic name and other settings

topic1 = NewTopic(name= 'metrics',num_partitions=1,replication_factor=1)
topic2 = NewTopic(name= 'Test_config',num_partitions=1,replication_factor=1)
topic3 = NewTopic(name= 'Trigger',num_partitions=1,replication_factor=1)
topic4 = NewTopic(name= 'Heartbeat',num_partitions=1,replication_factor=1)
topic5 = NewTopic(name= 'Register',num_partitions=1,replication_factor=1)

# Create the topic
admin_client.create_topics([topic1,topic2,topic3,topic4,topic5])
