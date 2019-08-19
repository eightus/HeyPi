from google.cloud import pubsub_v1
from google.cloud import storage
from google.oauth2 import service_account
import time
import re
import os
import json
from gpiozero import LED

dir_path = os.path.dirname(os.path.realpath(__file__))
_LED = LED(20)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "{}/../resource/service_account.json".format(dir_path)
print('Added Environment Variable')
with open('{}/../resource/uid.txt'.format(dir_path), 'r') as f:
    DEVICE_ID = f.read()


def download_blob(bucket_name, source_blob_name, destination_file_name):
    global dir_path
    """Downloads a blob from the bucket."""
    try:
        cred = service_account.Credentials.from_service_account_file(
            '{}/../resource/service_account.json'.format(dir_path))
        storage_client = storage.Client(credentials=cred)
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename('{}/{}'.format(dir_path, destination_file_name))
        return True
    except:
        return False


def callback(message):
    global DEVICE_ID
    #  Pull File From Bucket
    file_name = message.data.decode('utf-8')
    user = None
    regex = "(.*)\\[.*\\]"
    found = re.search(regex, file_name)
    if found:
        user = found.groups()[0]
    if user == DEVICE_ID:
        print('Ignoring Self-Message...')
        message.ack()
    else:
        bucket_name = 'heypi-iot-audio-file'
        if download_blob(bucket_name, file_name, file_name):
            print('New Broadcast Available')
            message.ack()
        else:
            print('Download Fail')
            message.ack()

def callback_led(message):
    data = json.loads(message.data.decode('utf-8'))
    if data['device'] != DEVICE_ID:
        print('Ignoring Message... -> NOT THIS DEVICE')
        message.ack()
    else:
        if data['toggle'] == 'on':
            print('Toggle: ON LED')
            _LED.on()
        else:
            print('Toggle; OFF LED')
            _LED.off()
        message.ack()


def receive_messages():
    """Receives messages from a pull subscription."""
    global dir_path
    project_id = "heypi-iot"
    subscription_name = 'bucket'
    subscription_name_led = 'led'
    cred = service_account.Credentials.from_service_account_file(
        '{}/../resource/service_account.json'.format(dir_path))
    subscriber = pubsub_v1.SubscriberClient(credentials=cred)
    # The `subscription_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/subscriptions/{subscription_name}`
    subscription_path = subscriber.subscription_path(project_id, subscription_name)
    subscription_path_led = subscriber.subscription_path(project_id, subscription_name_led)


    subscriber.subscribe(subscription_path, callback=callback)
    subscriber.subscribe(subscription_path_led, callback=callback_led)


    # The subscriber is non-blocking. We must keep the main thread from
    # exiting to allow it to process messages asynchronously in the background.
    print('Listening for messages on {}'.format(subscription_path))
    print('Listening for messages on {}'.format(subscription_path_led))
    while True:
        time.sleep(5)


receive_messages()
