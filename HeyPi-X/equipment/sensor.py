import Adafruit_DHT
from gpiozero import MCP3008
from eq_db import Database
from time import sleep
import datetime
import random
import ssl
import time
import json
import jwt
import paho.mqtt.client as mqtt
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

SERVICE_ACCOUNT = './resource/service_account.json'
PROJECT_ID = 'heypi-iot'
CLOUD_REGION = 'asia-east1'
REGISTRY_ID = 'heypi-registry'
with open('{}/../resource/uid.txt'.format(dir_path), 'r') as f:
    DEVICE_ID = f.read()
CERTIFICATE_FILE = './resource/roots.pem'
PRIVATE_KEY = './resource/rsa_private.pem'
ALGORITHM = 'RS256'
MQTT_BRIDGE_HOST = 'mqtt.googleapis.com'
MQTT_BRIDGE_PORT = 8883

minimum_backoff_time = 1
MAXIMUM_BACKOFF_TIME = 32
should_backoff = False


class Sensor:

    def __init__(self):
        self.conn = Database('assignment', DEVICE_ID)
        self.pin_dht11 = None
        self.pin_ldr = None
        self.load_config()
        self.sensor_dht11 = Adafruit_DHT.DHT11
        self.sensor_ldr = MCP3008(channel=self.pin_ldr)
        self.stop = False

    def load_config(self):
        global DEVICE_ID
        data = self.conn.get_configuration()
        self.pin_dht11 = int(data['dht11'])
        cleaned = data['brightness'][1:]
        self.pin_ldr = int(cleaned)

    def publish(self, subFolder):
        global minimum_backoff_time
        global MAXIMUM_BACKOFF_TIME

        sub_topic = 'events/' + subFolder
        mqtt_topic = '/devices/{}/{}'.format(DEVICE_ID, sub_topic)
        jwt_iat = datetime.datetime.utcnow()
        jwt_exp_mins = 20
        client = get_client(PROJECT_ID, CLOUD_REGION, REGISTRY_ID, DEVICE_ID, PRIVATE_KEY,
                            ALGORITHM, CERTIFICATE_FILE, MQTT_BRIDGE_HOST, MQTT_BRIDGE_PORT)
        while self.stop is not True:
            if should_backoff:
                if minimum_backoff_time > MAXIMUM_BACKOFF_TIME:
                    print('Exceeded maximum backoff time. Giving up.')
                    break
                delay = minimum_backoff_time + random.randint(0, 1000) / 1000.0
                print('Waiting for {} before reconnecting.'.format(delay))
                time.sleep(delay)
                minimum_backoff_time *= 2
                client.connect(MQTT_BRIDGE_HOST, MQTT_BRIDGE_PORT)

            humidity, temperature, brightness = self.sense()
            payload = json.dumps({'humidity': humidity, 'temperature': temperature, 'brightness': brightness})
            print('Publishing message: \'{}\''.format(payload))
            seconds_since_issue = (datetime.datetime.utcnow() - jwt_iat).seconds
            if seconds_since_issue > 60 * jwt_exp_mins:
                print('Refreshing token after {}s'.format(seconds_since_issue))
                jwt_iat = datetime.datetime.utcnow()
                client = get_client(PROJECT_ID, CLOUD_REGION, REGISTRY_ID, DEVICE_ID, PRIVATE_KEY,
                                    ALGORITHM, CERTIFICATE_FILE, MQTT_BRIDGE_HOST, MQTT_BRIDGE_PORT)

            client.publish(mqtt_topic, payload, qos=1)

            # Send events every second. State should not be updated as often
            time.sleep(5)

    def sense(self):
        try:
            humidity, temperature = Adafruit_DHT.read_retry(self.sensor_dht11, self.pin_dht11)
            light_value = self.sensor_ldr.value
            if humidity is None or temperature is None or light_value is None:
                sleep(1)
                return self.sense()
            else:
                inverse = 1 - round(light_value, 2)
                convert = '{:.2f}'.format(inverse * 100)
                # print("Humidity:" + str(humidity) + " | " + "Temperature" + str(temperature))
                return humidity, temperature, convert
        except KeyboardInterrupt:
            return

    def stop_sensor(self):
        self.stop = True


def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))


def on_connect(unused_client, unused_userdata, unused_flags, rc):
    """Paho callback for when a device connects."""
    print('on_connect', mqtt.connack_string(rc))
    global should_backoff
    global minimum_backoff_time
    should_backoff = False
    minimum_backoff_time = 1


def on_disconnect(unused_client, unused_userdata, rc):
    """Paho callback for when a device disconnects."""
    print('on_disconnect',error_str(rc))
    global should_backoff
    should_backoff = True


def get_client(
        project_id, cloud_region, registry_id, device_id, private_key_file,
        algorithm, ca_certs, mqtt_bridge_hostname, mqtt_bridge_port):
    client_id = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(
            project_id, cloud_region, registry_id, device_id)
    print('Device client_id is \'{}\''.format(client_id))

    client = mqtt.Client(client_id=client_id)

    # With Google Cloud IoT Core, the username field is ignored, and the
    # password field is used to transmit a JWT to authorize the device.
    client.username_pw_set(
            username='unused',
            password=create_jwt(
                    project_id, private_key_file, algorithm))

    # Enable SSL/TLS support.
    client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

    # Register message callbacks. https://eclipse.org/paho/clients/python/docs/
    # describes additional callbacks that Paho supports. In this example, the
    # callbacks just print to standard out.
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # Connect to the Google MQTT bridge.
    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)
    return client


def create_jwt(project_id, private_key_file, algorithm):
    token = {
            # The time that the token was issued at
            'iat': datetime.datetime.utcnow(),
            # The time the token expires.
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            # The audience field should always be set to the GCP project id.
            'aud': project_id
    }

    # Read the private key file.
    with open(private_key_file, 'r') as f:
        private_key = f.read()

    print('Creating JWT using {} from private key file {}'.format(
            algorithm, private_key_file))

    return jwt.encode(token, private_key, algorithm=algorithm)


a = Sensor()
a.load_config()
a.publish('sensor')
