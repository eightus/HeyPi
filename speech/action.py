from subprocess import Popen
import re
import time
import os
from picamera import PiCamera


class Action:
    def __init__(self, conn, speech, led):
        self.conn = conn

        self.match_type = None
        self.load_condition()

        self.default = None
        self.reload_speech(speech)

        self.led = None
        self.reload_led(led)

        self.camera = PiCamera()
        self.camera.start_preview()

    def reload_speech(self, speech):
        self.default = speech

    def reload_led(self, led):
        self.led = led

    def load_condition(self):
        cfg = self.conn.get_condition()
        type_exact = []
        type_contain = []
        for i in cfg:
            if i['type'] == 'exact':
                store = [i['action'], i['match']]
                type_exact.append(store)
            elif i['type'] == 'contain':
                store = [i['action'], i['match']]
                type_contain.append(store)

        new_dict = {'exact': type_exact, 'contain': type_contain}
        self.match_type = new_dict

    def check_condition(self, user_input):
        for i in self.match_type['exact']:
            #  0 is action, 1 is condition
            if i[1] == user_input:
                return self.check_function(i[0])

        for i in self.match_type['contain']:
            #  0 is action, 1 is condition
            if i[1] in user_input:
                return self.check_function(i[0])

        return False  # reply no match

    def check_function(self, func):
        if func == 'temperature':
            return self.reply_temperature()
        elif func == 'humidity':
            return self.reply_humidity()
        elif func == 'brightness':
            return self.reply_brightness()
        elif func == 'led':
            return self.reply_led()
        elif func == 'camera':
            return self.reply_camera()

        regex = "speak='(.*)'"
        found = re.search(regex, func)
        if found:
            return self.reply_speak(found.groups()[0])

    def reply_temperature(self):
        temperature = self.conn.get_temperature()
        speech = self.default + "'{}'".format('The temperature is {} degrees celsius'.format(temperature['value']))
        Popen(speech, shell=True)
        return True

    def reply_humidity(self):
        humidity = self.conn.get_humidity()
        speech = self.default + '"{}"'.format('The humidity is {}%').format(humidity['value'])
        Popen(speech, shell=True)
        return True

    def reply_brightness(self):
        brightness = self.conn.get_brightness()
        speech = self.default + '"{}"'.format('The brightness is {}%').format(brightness['value'])
        Popen(speech, shell=True)
        return True

    def reply_led(self):
        led = self.conn.get_led(self.led)
        speech = self.default + '"{}"'.format('The LED is turned {}').format(led['value'])
        Popen(speech, shell=True)
        return True

    def reply_camera(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        print(dir_path)
        current_t = time.strftime('%Y-%m-%d %H:%M:%S')
        self.camera.capture(dir_path + '/../picture/' + current_t + '.jpg')
        speech = self.default + '"{}"'.format('Success!')
        Popen(speech, shell=True)
        return True

    def reply_speak(self, text):
        speech = self.default + '"{}"'.format(text)
        Popen(speech, shell=True)
        return True

    def reply_dont_understand(self):
        speech = self.default + '"{}"'.format('Sorry, I do not understand what you said')
        Popen(speech, shell=True)
        return True

    def reply_not_available(self):
        speech = self.default + '"{}"'.format('Sorry, Google is not available currently')
        Popen(speech, shell=True)
        return True
