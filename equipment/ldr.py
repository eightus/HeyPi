from gpiozero import MCP3008
from time import sleep
from eq_db import Database


class LDR:

    def __init__(self):
        self.conn = Database('assignment')
        self.pin = None
        self.load_config()
        self.adc = MCP3008(channel=self.pin)
        self.stop = False

    def load_config(self):
        data = self.conn.get_configuration()
        cleaned = data['brightness'][1:]
        self.pin = int(cleaned)

    def sense(self):
        try:
            while self.stop is False:
                light_value = self.adc.value
                if light_value is None:
                    continue
                inverse = 1 - round(light_value, 2)
                convert = '{:.2f}'.format(inverse * 100)
                print(convert)
                self.conn.insert_brightness(convert)
                sleep(3)
        except KeyboardInterrupt:
            return


a = LDR()
a.load_config()
a.sense()
