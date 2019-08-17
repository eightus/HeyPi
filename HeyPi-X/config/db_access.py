import mysql.connector
from config.hash import sha512hash
import time
from datetime import datetime
from operator import itemgetter


class Database:

    def __init__(self, db):
        self.conn = mysql.connector.connect(user='root', password='ubuntu123',
                                            host='35.200.168.236', database=db,
                                            use_pure=True)
        self.conn.autocommit = True
        self.user = None

    def set_user(self, usr):
        self.user = usr

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

    def register(self, usr, pwd):
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM user WHERE username = %s", [usr])
        res = cur.fetchone()
        cur.close()

        if not res:
            #  Username Does Not Exist
            hashed_pwd, salt = sha512hash(pwd)
            cur = self.conn.cursor(dictionary=True)
            cur.execute("INSERT INTO user (username, password, salt) VALUES (%s, %s, %s)", [usr, hashed_pwd, salt])
            cur.close()

            print('Adding Default Conditions...')
            cur = self.conn.cursor(dictionary=True)
            cur.execute("INSERT INTO chat_condition(`match`, `type`, `action`, `user`) VALUES('temperature','contain','temperature', %s)", [usr])
            cur.execute("INSERT INTO chat_condition(`match`, `type`, `action`, `user`) VALUES('brightness','contain','brightness', %s)", [usr])
            cur.execute("INSERT INTO chat_condition(`match`, `type`, `action`, `user`) VALUES('humidity','contain','humidity', %s)", [usr])
            cur.execute("INSERT INTO chat_condition(`match`, `type`, `action`, `user`) VALUES('led','contain','led', %s)", [usr])
            cur.execute("INSERT INTO chat_condition(`match`, `type`, `action`, `user`) VALUES('broadcast','start','broadcast', %s)", [usr])
            cur.execute("INSERT INTO chat_condition(`match`, `type`, `action`, `user`) VALUES('voicemail','contain','voicemail', %s)", [usr])
            cur.close()
            print('Added Conditions.')
            self.conn.commit()
            return True
        else:
            #  Username Exist
            return False

    def get_temperature(self):
        current_dt = time.strftime('%Y-%m-%d %H:%M:%S')
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT temperature as value FROM dht11_sensor WHERE `user`=%s ORDER BY id DESC LIMIT 1", [self.user])
        res = cur.fetchone()
        cur.close()
        res['time'] = current_dt
        return res

    def get_humidity(self):
        current_dt = time.strftime('%Y-%m-%d %H:%M:%S')
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT humidity as value FROM dht11_sensor WHERE `user`=%s ORDER BY id DESC LIMIT 1", [self.user])
        res = cur.fetchone()
        res['time'] = current_dt
        cur.close()
        return res

    def get_brightness(self):
        current_dt = time.strftime('%Y-%m-%d %H:%M:%S')
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT brightness as value FROM ldr WHERE `user`=%s ORDER BY id DESC LIMIT 1", [self.user])
        res = cur.fetchone()
        res['time'] = current_dt
        cur.close()
        return res

    def get_chat(self):
        current_dt = time.strftime('%Y-%m-%d %H:%M:%S')
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT COUNT(id) as value from chat_log WHERE `user`=%s", [self.user])
        res = cur.fetchone()
        cur.close()
        res['time'] = current_dt
        return res

    def get_log(self, _limit=None):
        cur = self.conn.cursor(dictionary=True)
        if _limit is None:
            cur.execute("SELECT * FROM chat_log WHERE `user`=%s", [self.user])
        elif _limit is not None:
            cur.execute("SELECT * FROM chat_log WHERE `user`=%s ORDER BY id DESC LIMIT {}".format(_limit), [self.user])
        log = cur.fetchall()
        cur.close()
        return log

    def get_led(self, led):
        current_dt = time.strftime('%Y-%m-%d %H:%M:%S')
        if led.value:
            led.off()
            return {'time': current_dt, 'value': 'Off'}
        else:
            led.on()
            return {'time': current_dt, 'value': 'On'}

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

    def insert_chat_log(self, chat, status):
        current_dt = time.strftime('%Y-%m-%d %H:%M:%S')
        cur = self.conn.cursor()
        cur.execute("INSERT INTO chat_log (chat, status, date_time, `user`) VALUES (%s, %s, %s, %s)",
                    [chat, status, current_dt, self.user])
        cur.close()
        self.conn.commit()
        return True

    def delete_chat_condition(self, selected):
        cur = self.conn.cursor()
        for i in selected:
            cond_id = int(i)
            cur.execute("DELETE FROM chat_condition WHERE id = {} and `user`=%s".format(cond_id), [self.user])
        cur.close()
        self.conn.commit()
        return True

    def get_humidity_stat(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, humidity, date_time from dht11_sensor ORDER BY id DESC LIMIT 8")
        res = cur.fetchall()
        cur.close()
        return res

    def get_temperature_stat(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, temperature, date_time from dht11_sensor ORDER BY id DESC LIMIT 8")
        res = cur.fetchall()
        cur.close()
        return res

    def get_brightness_stat(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, brightness, date_time from ldr ORDER BY id DESC LIMIT 8")
        res = cur.fetchall()
        cur.close()
        return res

    def get_all_stat(self):
        data_humid = self.get_humidity_stat()
        data_temp = self.get_temperature_stat()
        data_bright = self.get_brightness_stat()

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

    def insert_configuration(self, usr):
        cur = self.conn.cursor()
        cur.execute('''INSERT INTO configuration(button, dht11, LED, brightness, speech_pitch, speech_speed, speech_gender, `user`) VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s)''', [13, 21, 20, 'c0', 50, 140, 'female', usr])
        cur.close()
        self.conn.commit()
        return True

    def get_log_clean(self):
        clean = []
        for i in self.get_log(5):
            format_dt = str(i['date_time'].strftime("%Y-%m-%d %H:%M:%S"))
            status = True if i['status'] == 'True' else False
            clean.append([i['id'], i['chat'], status, format_dt])

        return clean


def clean_condition(condition):
    out_dict = {}
    for i in condition:
        value = 'ID: {:>3} Input: {:>30} Type: {:>10} Action: {:>30}'.format(i['id'], i['match'],
                                                                             i['type'], i['action'])
        key = i['id']
        out_dict[key] = value
    return out_dict

