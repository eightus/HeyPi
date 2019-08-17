import mysql.connector
from config.hash import sha512hash
import time
from datetime import datetime
from operator import itemgetter
import os
from google.cloud import pubsub_v1
import json

class Database:

    def __init__(self, db):

        try:
            CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
            CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
            CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')
            cloudsql_unix_socket = os.path.join('/cloudsql', str(CLOUDSQL_CONNECTION_NAME))
            self.conn = mysql.connector.connect(user=CLOUDSQL_USER, password=CLOUDSQL_PASSWORD,
                                                unix_socket=cloudsql_unix_socket, database=db)

            print('Connected to Google Cloud SQL (Unix Socket)')
        except mysql.connector.errors.InterfaceError:
            self.conn = mysql.connector.connect(user='root', password='ubuntu123',
                                                host='35.200.168.236', database=db,
                                                use_pure=True)
            print('Connected to Google Cloud SQL (Public IP)')

        self.conn.autocommit = True
        self.led_status = 'off'

    def login(self, usr, pwd):
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM user WHERE username = %s", [usr])
        res = cur.fetchone()
        cur.close()

        if not res:
            #  Username Does Not Exist
            return False

        hashed_pwd = sha512hash(pwd, res['salt'])

        if hashed_pwd != res['password']:
            #  Wrong Password
            return False
        else:
            #  Correct Credentials
            return True

    def register(self, usr, pwd, num):
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM user WHERE username = %s", [usr])
        res_user = cur.fetchone()
        cur.execute("SELECT * FROM user WHERE `number` = %s", [num])
        res_num = cur.fetchone()
        cur.close()

        if not res_user and not res_num:
            #  Username & Number Does Not Exist
            hashed_pwd, salt = sha512hash(pwd)
            cur = self.conn.cursor(dictionary=True)
            cur.execute("INSERT INTO user (username, password, salt, number) VALUES (%s, %s, %s, %s)", [usr, hashed_pwd, salt, num])
            cur.close()
            self.conn.commit()
            return True
        else:
            #  Username Exist
            return False

    def get_temperature(self, usr):
        current_dt = time.strftime('%Y-%m-%d %H:%M:%S')
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT temperature as value FROM dht11_sensor WHERE `user`=%s ORDER BY id DESC LIMIT 1", [usr])
        res = cur.fetchone()
        cur.close()
        res['time'] = current_dt
        return res

    def get_humidity(self, usr):
        current_dt = time.strftime('%Y-%m-%d %H:%M:%S')
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT humidity as value FROM dht11_sensor WHERE `user`=%s ORDER BY id DESC LIMIT 1", [usr])
        res = cur.fetchone()
        res['time'] = current_dt
        cur.close()
        return res

    def get_brightness(self, usr):
        current_dt = time.strftime('%Y-%m-%d %H:%M:%S')
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT brightness as value FROM ldr WHERE `user`=%s ORDER BY id DESC LIMIT 1", [usr])
        res = cur.fetchone()
        res['time'] = current_dt
        cur.close()
        return res

    def get_chat(self, usr):
        current_dt = time.strftime('%Y-%m-%d %H:%M:%S')
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT COUNT(id) as value from chat_log WHERE `user`=%s", [usr])
        res = cur.fetchone()
        cur.close()
        res['time'] = current_dt
        return res

    def get_log(self, usr, _limit=None):
        cur = self.conn.cursor(dictionary=True)
        if _limit is None:
            cur.execute("SELECT id, chat, status, date_time FROM chat_log WHERE `user`=%s", [usr])
        elif _limit is not None:
            cur.execute("SELECT id, chat, status, date_time FROM chat_log WHERE `user`=%s ORDER BY id DESC LIMIT {}".format(_limit), [usr])
        log = cur.fetchall()
        cur.close()
        return log

    def get_led(self, usr):
        if self.led_status == 'off':
            self.led_status = 'on'
        elif self.led_status == 'on':
            self.led_status = 'off'

        current_dt = time.strftime('%Y-%m-%d %H:%M:%S')
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path('heypi-iot', 'led')
        data = {'device': usr, 'toggle': self.led_status}
        data = json.dumps(data)
        data = data.encode('utf-8')
        for i in range(1, 10):
            future = publisher.publish(topic_path, data=data)
            print(future.result())
        return {'time': current_dt, 'value': self.led_status}

    def get_configuration(self, usr):
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM configuration WHERE `user`=%s", [usr])
        cfg = cur.fetchone()
        cur.close()
        return cfg

    def get_condition(self, usr):
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM chat_condition WHERE `user`=%s", [usr])
        condition = cur.fetchall()
        cur.close()
        return condition

    def get_condition_clean(self, usr):
        condition = self.get_condition(usr)
        return clean_condition(condition)

    def insert_chat_log(self, chat, status, usr):
        current_dt = time.strftime('%Y-%m-%d %H:%M:%S')
        cur = self.conn.cursor()
        cur.execute("INSERT INTO chat_log (chat, status, date_time, `user`) VALUES (%s, %s, %s, %s)",
                    [chat, status, current_dt, usr])
        cur.close()
        self.conn.commit()
        return True

    def insert_chat_condition(self, text, match_type, action, usr):
        check = self.get_condition(usr)

        for i in check:
            if i['match'] == text and i['type'] == match_type and i['action'] == action:
                return False
        cur = self.conn.cursor()
        cur.execute("INSERT INTO chat_condition (`match`, `type`, `action`, `user`) VALUES (%s, %s, %s, %s)",
                    [text, match_type, action, usr])
        cur.close()
        self.conn.commit()
        return True

    def delete_chat_condition(self, selected, usr):
        cur = self.conn.cursor()
        for i in selected:
            cond_id = int(i)
            cur.execute("DELETE FROM chat_condition WHERE id = {} AND `user`=%s".format(cond_id), [usr])
        cur.close()
        self.conn.commit()
        return True

    def get_humidity_stat(self, usr):
        cur = self.conn.cursor()
        cur.execute("SELECT id, humidity, date_time from dht11_sensor WHERE `user`=%s ORDER BY id DESC LIMIT 8", [usr])
        res = cur.fetchall()
        cur.close()
        return res

    def get_temperature_stat(self, usr):
        cur = self.conn.cursor()
        cur.execute("SELECT id, temperature, date_time from dht11_sensor WHERE `user`=%s ORDER BY id DESC LIMIT 8", [usr])
        res = cur.fetchall()
        cur.close()
        return res

    def get_brightness_stat(self, usr):
        cur = self.conn.cursor()
        cur.execute("SELECT id, brightness, date_time from ldr WHERE `user`=%s ORDER BY id DESC LIMIT 8", [usr])
        res = cur.fetchall()
        cur.close()
        return res

    def get_all_stat(self, usr):
        data_humid = self.get_humidity_stat(usr)
        data_temp = self.get_temperature_stat(usr)
        data_bright = self.get_brightness_stat(usr)

        combined = [data_humid, data_temp, data_bright]

        new_list = []
        for i in combined:
            tmp2_list = []
            for data in i:
                tmp_list = list(data)
                del tmp_list[-1]
                tmp_list.append(str(data[2].strftime("%H:%M:%S")))
                tmp2_list.append(tmp_list)
            tmp2_list = sorted(tmp2_list, key=itemgetter(0))
            new_list.append(tmp2_list)

        data_h = [[i[2], i[1]] for i in new_list[0]]
        data_t = [[i[2], i[1]] for i in new_list[1]]
        data_b = [[i[2], i[1]] for i in new_list[2]]
        return {'data_humidity': data_h, 'data_temperature': data_t, 'data_brightness': data_b}

    def update_configuration(self, form, usr):
        default = self.get_configuration(usr)
        res = {}
        for k, v in form.items():
            if v == '':
                res[k] = default[k]
            else:
                res[k] = v

        if 'c' not in res['brightness']:
            res['brightness'] = 'c' + res['brightness']

        cur = self.conn.cursor()
        cur.execute('''UPDATE configuration SET button=%s, dht11=%s, LED=%s, 
                    brightness=%s, speech_pitch=%s, speech_speed=%s, speech_gender=%s''',
                    [res['button'], res['dht11'], res['LED'], res['brightness'],
                     res['speech_pitch'], res['speech_speed'], res['speech_gender']])
        cur.close()
        self.conn.commit()
        return res

    def get_log_clean(self, usr):
        clean = []
        for i in self.get_log(usr, 5):
            format_dt = str(i['date_time'].strftime("%Y-%m-%d %H:%M:%S"))
            status = True if i['status'] == 'True' else False
            clean.append([i['id'], i['chat'], status, format_dt])

        return clean

    def get_update_all(self, usr):
        temperature = self.get_temperature(usr)
        brightness = self.get_brightness(usr)
        humidity = self.get_humidity(usr)
        return {'temperature': temperature, 'brightness': brightness, 'humidity': humidity}


def clean_condition(condition):
    out_dict = {}
    for i in condition:
        value = 'ID: {:>3} Input: {:>30} Type: {:>10} Action: {:>30}'.format(i['id'], i['match'],
                                                                             i['type'], i['action'])
        key = i['id']
        out_dict[key] = value
    return out_dict

