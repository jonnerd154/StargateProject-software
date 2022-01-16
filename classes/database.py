import pymysql
from base64 import b64decode

from ancients_log_book import AncientsLogBook
from stargate_config import StargateConfig

class Database:

    def __init__(self, base_path):

        ### Load our config file
        self.cfg = StargateConfig(base_path, "database.json")

        ### Setup the logger
        self.log = AncientsLogBook(base_path, "database.log", print_to_console=False)
        self.cfg.set_log(self.log)
        self.cfg.load()

    def connect(self):
        self.log.log("Connecting")
        self.db = pymysql.connect(  host=self.cfg.get('db_host'),
                                    user=self.cfg.get('db_user'),
                                    password=str( b64decode( self.cfg.get('db_pass') ), 'utf-8'), #TODO: password isn't secure.
                                    database=self.cfg.get('db_name') )

    def disconnect(self):
        self.log.log("Disconnecting")
        self.db.close()

    def get_fan_gates(self):
        self.log.log("Retrieving Fan Gates")

        self.connect()

        cursor = self.db.cursor()
        sql = f"SELECT * FROM `fan_gates`"
        cursor.execute(sql)
        result = cursor.fetchall()

        self.disconnect()

        return result

    def get_software_updates(self):
        self.log.log("Retrieving Software Updates")

        self.connect()

        cursor = self.db.cursor()
        sql = f"SELECT * FROM `software_update`"
        cursor.execute(sql)
        result = cursor.fetchall()

        self.disconnect()

        return result
