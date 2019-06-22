import Adafruit_DHT
from eq_db import Database
from time import sleep


class DHT11:

    def __init__(self):
        self.pin = None
        self.sensor = Adafruit_DHT.DHT11
        self.stop = False
        self.conn = Database('assignment')

    def load_config(self):
        data = self.conn.get_configuration()
        self.pin = int(data['dht11'])

    def sense(self):
        try:
            while self.stop is False:
                humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin)
                if humidity is None or temperature is None:
                    print('None')
                    continue
                print(str(humidity) + " | " + str(temperature))
                self.conn.insert_dht11(temperature, humidity)
        except KeyboardInterrupt:
            return

    def stop_sensor(self):
        self.stop = True


a = DHT11()
a.load_config()
a.sense()
