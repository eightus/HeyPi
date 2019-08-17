import mysql.connector
import time


SERVICE_ACCOUNT = './resource/service_account.json'
PROJECT_ID = 'heypi-iot'
CLOUD_REGION = 'asia-east1'
REGISTRY_ID = 'heypi-registry'
DEVICE_ID = 'my-python'
CERTIFICATE_FILE = './resource/roots.pem'
PRIVATE_KEY = './resource/rsa_private.pem'
ALGORITHM = 'RS256'
MQTT_BRIDGE_HOST = 'mqtt.googleapis.com'
MQTT_BRIDGE_PORT = 8883

minimum_backoff_time = 1
MAXIMUM_BACKOFF_TIME = 32
should_backoff = False


class Database:

    def __init__(self, db, user):
        self.conn = mysql.connector.connect(user='root', password='ubuntu123',
                                            host='35.200.168.236', database=db,
                                            use_pure=True)
        self.conn.autocommit = True
        self.user = user

    def get_configuration(self):
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM configuration WHERE `user`=%s", [self.user])
        cfg = cur.fetchone()
        cur.close()
        return cfg

    def insert_dht11(self, temperature, humidity):
        current_dt = time.strftime('%Y-%m-%d %H:%M:%S')
        cur = self.conn.cursor()
        cur.execute("INSERT INTO dht11_sensor (temperature, humidity, date_time) VALUES (%s, %s, %s)",
                    [temperature, humidity, current_dt])
        cur.close()
        self.conn.commit()
        return True

    def insert_brightness(self, brightness):
        current_dt = time.strftime('%Y-%m-%d %H:%M:%S')
        cur = self.conn.cursor()
        cur.execute("INSERT INTO ldr (brightness, date_time) VALUES (%s, %s)",
                    [brightness, current_dt])
        cur.close()
        self.conn.commit()
        return True
