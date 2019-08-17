from config.db_access import Database
import time
from speech.recorder import Record
from speech.action import Action
from gpiozero import LED, Button
from subprocess import Popen
import os
import io
from google.oauth2 import service_account
from googleapiclient import discovery
from googleapiclient.errors import HttpError
import argparse

_DATABASE_NAME = 'assignment'
_LED = None
_BUTTON = None
_SPEECH = None
_DHT11_PIN = None
_BRIGHTNESS = None


# Initialisation
def initialise(usr):
    global _LED, _BUTTON, _DATABASE_NAME, _DHT11_PIN, _SPEECH, record, conn, action

    dir_path = os.path.dirname(os.path.realpath(__file__))
    cmd_sensor = 'sudo python3 {}/equipment/sensor.py'.format(dir_path)
    cmd_listener = 'sudo python3 {}/listen/listener.py'.format(dir_path)
    Popen(cmd_sensor, shell=True)
    Popen(cmd_listener, shell=True)

    _DATABASE_NAME = 'assignment'

    data = conn.get_configuration(usr)
    _LED = LED(20)

    speed, pitch = data['speech_speed'], data['speech_pitch']
    gender = 'en+m3' if data['speech_gender'] == 'male' else 'en+f3'
    _SPEECH = 'espeak -s{} -v{} -p{} -k5 -z '.format(speed, gender, pitch)

    action = Action(conn, _SPEECH, _LED, usr)
    record = Record(conn, action)

    _BUTTON = Button(int(data['button']), pull_up=False)
    _BUTTON.when_pressed = record.start_record
    _BUTTON.when_released = record.stop_record


def get_client(service_account_json):
    """Returns an authorized API client by discovering the IoT API and creating
    a service object using the service account credentials JSON."""
    api_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    api_version = 'v1'
    discovery_api = 'https://cloudiot.googleapis.com/$discovery/rest'
    service_name = 'cloudiotcore'

    credentials = service_account.Credentials.from_service_account_file(
            service_account_json)
    scoped_credentials = credentials.with_scopes(api_scopes)

    discovery_url = '{}?version={}'.format(
            discovery_api, api_version)

    return discovery.build(
            service_name,
            api_version,
            discoveryServiceUrl=discovery_url,
            credentials=scoped_credentials)


def create_rs256_device(
        service_account_json, project_id, cloud_region, registry_id, device_id,
        certificate_file):
    """Create a new device with the given id, using RS256 for
    authentication."""
    # [START iot_create_rsa_device]
    registry_name = 'projects/{}/locations/{}/registries/{}'.format(
            project_id, cloud_region, registry_id)

    client = get_client(service_account_json)
    with io.open(certificate_file) as f:
        certificate = f.read()

    # Note: You can have multiple credentials associated with a device.
    device_template = {
        'id': device_id,
        'credentials': [{
            'publicKey': {
                'format': 'RSA_X509_PEM',
                'key': certificate
            }
        }]
    }

    devices = client.projects().locations().registries().devices()
    return devices.create(parent=registry_name, body=device_template).execute()


def re_initialise(usr):
    global conn, action, _LED, _SPEECH, _BUTTON

    data = conn.get_configuration(usr)
    speed, pitch = data['speech_speed'], data['speech_pitch']
    gender = 'en+m3' if data['speech_gender'] == 'male' else 'en+f3'
    _SPEECH = 'espeak -s{} -v{} -p{} -k5 -z '.format(speed, gender, pitch)
    try:
        _LED = LED(int(data['LED']))
    except:
        pass
    action.reload_speech(_SPEECH)
    action.reload_led(_LED)


def main():
    global conn, _DATABASE_NAME
    conn = Database(_DATABASE_NAME)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="Specify the Username", type=str, required=False)
    parser.add_argument("-p", "--password", help="Specify the Password", type=str, required=False)
    args = parser.parse_args()

    if args.user and args.password:
        if os.path.exists('{}/resource/uid.txt'.format(dir_path)):
            print('Account Exists. Do Not Need To Specify Username and Password')
            return
        else:
            #  MySQL Account
            if not conn.register(args.user, args.password):
                print("Username Exist. Use Another Username")
                return

            #  Insert Configuration
            if not conn.insert_configuration(args.user):
                print('Unknown Error Occurred. Please Contact Augustus')
                return

            #  RSA Keys & Create Device IoT Core
            generate_rsa = 'sudo {}/resource/generate_keys.sh'.format(dir_path)
            Popen(generate_rsa, shell=True)
            with open('{}/resource/uid.txt'.format(dir_path), 'w') as f:
                f.write(args.user)
                f.close()
            print("Waiting...")
            time.sleep(10)
            print("Complete")
            time.sleep(3)
            SERVICE_ACCOUNT = './resource/service_account.json'
            PROJECT_ID = 'heypi-iot'
            CLOUD_REGION = 'asia-east1'
            REGISTRY_ID = 'heypi-registry'
            DEVICE_ID = args.user
            CERTIFICATE_FILE = './resource/rsa_cert.pem'
            create_rs256_device(SERVICE_ACCOUNT, PROJECT_ID, CLOUD_REGION, REGISTRY_ID, DEVICE_ID,
                                CERTIFICATE_FILE)
            print('Created Device')

    if not os.path.exists('{}/resource/uid.txt'.format(dir_path)):
        print('Account Does Not Exists. Please Specify Username and Password to Create')
        return

    print("Starting...")
    time.sleep(5)
    with open('{}/resource/uid.txt'.format(dir_path), 'r') as f:
        uid = f.read()
        conn.set_user(uid)
        print('#' * 20)
        print(conn.user)
        print('#' * 20)
        initialise(uid)
    while True:
        time.sleep(5)

if __name__ == '__main__':
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/Downloads/resource/service_account.json"
    print('Added Environment Variable')
    main()