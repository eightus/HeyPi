import mysql.connector
import time


class Database:

    def __init__(self, db):
        self.conn = mysql.connector.connect(user='august', password='ubuntu123',
                                            host='localhost', database=db,
                                            use_pure=True)
        self.conn.autocommit = True

    def get_configuration(self):
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM configuration")
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
