from google.cloud import pubsub_v1
import json

DEVICE_ID = ''

def publish_message():
    publisher = pubsub_v1.PublisherClient()
    # The `topic_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/topics/{topic_name}`
    topic_path = publisher.topic_path('heypi-iot', 'led')
    data = {'device': DEVICE_ID, 'toggle': 'on'}
    data = json.dumps(data)
    data = data.encode('utf-8')
    for i in range(1, 10):
        future = publisher.publish(topic_path, data=data)
        print(future.result())

publish_message()