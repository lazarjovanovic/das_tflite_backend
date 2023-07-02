import psycopg2
from uuid import uuid4
from utils.logger import logging
from db_module.db_queries import setup_queries
from utils.read_config import get_db_config


class DBClient(object):
    def __init__(self, host="localhost", database="das_database", user="postgres", password="postgres"):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.db_config = get_db_config()

        self.conn = psycopg2.connect(
            host=self.host if "host" not in self.db_config else self.db_config["host"],
            database=self.database if "database" not in self.db_config else self.db_config["database"],
            user=self.user if "user" not in self.db_config else self.db_config["user"],
            password=self.password if "password" not in self.db_config else self.db_config["password"])

    def test_connection(self):
        db_version = None
        try:
            cur = self.conn.cursor()
            query = "SELECT version()"

            cur.execute(query)
            db_version = cur.fetchone()
            cur.close()
            logging.info(f"PostgreSQL version is: {db_version}")
        except Exception as e:
            logging.error(f"Unable to test connection due to error: {e}")
        return db_version

    def setup_database(self):
        setup_status = False
        try:
            cur = self.conn.cursor()
            for query in setup_queries:
                cur.execute(query)
            cur.close()
            self.conn.commit()
            setup_status = True
            logging.info(f"DB setup executed successfully")
        except Exception as e:
            logging.error(f"Unable to perform DB setup due to error: {e}")
        return setup_status

    def login_search(self, username, password):
        status_flag = False
        user_id = None
        query = f"SELECT * FROM das_data.users WHERE username='{username}' AND password='{password}';"
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            users = cur.fetchall()
            if len(users) == 1:
                user_id = users[0][0]
                status_flag = True
                logging.info(f"User by defined username and password found")
            else:
                logging.warning(f"User by defined username and password not found")
        except Exception as e:
            logging.error(f"Unable to query users by username and password due to error: {e}")

        return status_flag, user_id

    def register_search(self, username):
        status_flag = False
        query = f"SELECT COUNT(*) FROM das_data.users WHERE username='{username}';"
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            users = cur.fetchone()
            users_number = users[0]
            if users_number == 0:
                status_flag = True
                logging.info(f"User by defined username not registered yet")
            else:
                logging.warning(f"User by defined username already registered")
        except Exception as e:
            logging.error(f"Unable to query users by username due to error: {e}")

        return status_flag

    def register_user(self, user_dict):
        user_uuid = str(uuid4())
        user_dict_keys = list(user_dict.keys())
        user_dict_keys = ["id"] + user_dict_keys
        user_dict_keys = ",".join(user_dict_keys)

        user_dict_values = list(user_dict.values())
        user_dict_values = [user_uuid] + user_dict_values
        user_dict_values = "'" + "','".join(user_dict_values) + "'"
        query = f"INSERT INTO das_data.users ({user_dict_keys}) VALUES ({user_dict_values});"

        status = False
        return_uuid = None
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            cur.close()
            self.conn.commit()
            status = True
            return_uuid = user_uuid
            logging.info(f"New user with id {user_uuid} registered successfully")
        except Exception as e:
            logging.error(f"Unable to register new user due to error: {e}")
        return status, return_uuid


db_client = DBClient()
