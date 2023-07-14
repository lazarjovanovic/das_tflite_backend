import psycopg2
from uuid import uuid4
from utils.logger import logging
from db_module.db_queries import setup_queries
from utils.read_config import get_db_config
from datetime import datetime


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
        user_role = None
        query = f"SELECT * FROM das_data.users WHERE username='{username}' AND password='{password}';"
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            users = cur.fetchall()
            if len(users) == 1:
                user_id = users[0][0]
                user_role = users[0][7]
                status_flag = True
                logging.info(f"User by defined username and password found")
            else:
                logging.warning(f"User by defined username and password not found")
        except Exception as e:
            logging.error(f"Unable to query users by username and password due to error: {e}")

        return status_flag, user_id, user_role

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
        return_role = None
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            cur.close()
            self.conn.commit()
            status = True
            return_uuid = user_uuid
            return_role = user_dict["role"]
            logging.info(f"New user with id {user_uuid} registered successfully")
        except Exception as e:
            logging.error(f"Unable to register new user due to error: {e}")
        return status, return_uuid, return_role

    def add_therapy(self, therapy_dict):
        therapy_dict_keys = list(therapy_dict.keys())
        therapy_dict_keys = ",".join(therapy_dict_keys)

        therapy_dict_values = list(therapy_dict.values())
        therapy_dict_values = [str(value) for value in therapy_dict_values]
        therapy_dict_values = "'" + "','".join(therapy_dict_values) + "'"
        query = f"INSERT INTO das_data.therapies ({therapy_dict_keys}) VALUES ({therapy_dict_values});"

        status = False
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            cur.close()
            self.conn.commit()
            status = True
            logging.info(f"New therapy for disease {therapy_dict['disease']} "
                         f"added successfully by doctor {therapy_dict['doctor_id']}")
        except Exception as e:
            logging.error(f"Unable to add new therapy due to error: {e}")
        return status

    def update_therapy(self, therapy_dict):
        therapy_id = therapy_dict["id"]
        del therapy_dict["id"]

        update_string = [str(k) + "='" + str(v) + "'" for k, v in therapy_dict.items()]
        update_string = ", ".join(update_string)
        query = f"UPDATE das_data.therapies SET {update_string} WHERE id={therapy_id};"

        status = False
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            cur.close()
            self.conn.commit()
            status = True
            logging.info(f"New therapy for disease {therapy_dict['disease']} "
                         f"added successfully by doctor {therapy_dict['doctor_id']}")
        except Exception as e:
            logging.error(f"Unable to add new therapy due to error: {e}")
        return status, therapy_id

    def get_therapies_by_doctor_id(self, doctor_id):
        status_flag = False
        therapies_list = list()
        try:
            cur = self.conn.cursor()
            query = f"SELECT * FROM das_data.therapies WHERE doctor_id = '{doctor_id}';"

            cur.execute(query)
            therapies = cur.fetchall()
            cur.close()

            for therapy in therapies:
                therapy_dict = dict()
                therapy_dict["id"] = therapy[0]
                therapy_dict["disease"] = therapy[1]
                therapy_dict["location"] = therapy[2]
                therapy_dict["length_of_existence_weeks_from"] = therapy[3]
                therapy_dict["length_of_existence_weeks_to"] = therapy[4]
                therapy_dict["dimension_width_mm"] = therapy[5]
                therapy_dict["dimension_height_mm"] = therapy[6]
                therapy_dict["patient_age_from"] = therapy[7]
                therapy_dict["patient_age_to"] = therapy[8]
                therapy_dict["gender"] = therapy[9]
                therapy_dict["number_of_instances_from"] = therapy[10]
                therapy_dict["number_of_instances_to"] = therapy[11]
                therapy_dict["doctor_id"] = therapy[12]
                therapies_list.append(therapy_dict)

            status_flag = True
            logging.info(f"Therapies for doctor {doctor_id} successfully fetched")
        except Exception as e:
            logging.error(f"Unable to fetch therapies for doctor {doctor_id} due to error: {e}")
        return status_flag, therapies_list

    def get_therapies_by_disease(self, disease_id):
        status_flag = False
        therapies_list = list()
        try:
            cur = self.conn.cursor()
            query = f"SELECT * FROM das_data.therapies WHERE disease = '{disease_id}';"

            cur.execute(query)
            therapies = cur.fetchall()
            cur.close()

            for therapy in therapies:
                therapy_dict = dict()
                therapy_dict["id"] = therapy[0]
                therapy_dict["disease"] = therapy[1]
                therapy_dict["location"] = therapy[2]
                therapy_dict["length_of_existence_weeks_from"] = therapy[3]
                therapy_dict["length_of_existence_weeks_to"] = therapy[4]
                therapy_dict["dimension_width_mm"] = therapy[5]
                therapy_dict["dimension_height_mm"] = therapy[6]
                therapy_dict["patient_age_from"] = therapy[7]
                therapy_dict["patient_age_to"] = therapy[8]
                therapy_dict["gender"] = therapy[9]
                therapy_dict["number_of_instances_from"] = therapy[10]
                therapy_dict["number_of_instances_to"] = therapy[11]
                therapy_dict["doctor_id"] = therapy[12]
                therapies_list.append(therapy_dict)

            status_flag = True
            logging.info(f"Therapies for disease {disease_id} successfully fetched")
        except Exception as e:
            logging.error(f"Unable to fetch therapies for disease {disease_id} due to error: {e}")
        return status_flag, therapies_list

    def delete_therapy_by_id(self, therapy_id):
        query = f"DELETE FROM das_data.therapies WHERE id={therapy_id};"

        status = False
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            cur.close()
            self.conn.commit()
            status = True
            logging.info(f"Therapy with id {therapy_id} successfully deleted")
        except Exception as e:
            logging.error(f"Unable delete therapy id {therapy_id} due to error: {e}")
        return status

    def add_image(self, image_name, processed_flag):
        added_time = str(datetime.now())
        query = f"INSERT INTO das_data.images (name, added_at, processed) " \
                f"VALUES ('{image_name}', '{added_time}', '{processed_flag}');"

        status = False
        image_id = None
        try:
            cur = self.conn.cursor()
            cur.execute(query)

            image_id_query = f"SELECT id FROM das_data.images WHERE name = '{image_name}'"
            cur.execute(image_id_query)
            image_id = cur.fetchone()[0]

            cur.close()
            self.conn.commit()

            status = True
            logging.info(f"New image {image_name} successfully added")
        except Exception as e:
            logging.error(f"Unable to add new image {image_name} due to error: {e}")
        return status, image_id

    def add_examination(self, user_id, image_id, disease):
        processed_time = str(datetime.now())
        query = f"INSERT INTO das_data.examinations (user_id, image_id, image_class, processed_at) " \
                f"VALUES ('{user_id}', '{image_id}', '{disease}', '{processed_time}');"

        status = False
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            cur.close()
            self.conn.commit()

            status = True
            logging.info(f"New examination for user {user_id} and image {image_id} successfully added")
        except Exception as e:
            logging.error(f"Unable to add new examination for user {user_id} and image {image_id} due to error: {e}")
        return status

    def get_examinations_by_patient_id(self, patient_id):
        status_flag = False
        examinations_list = list()
        try:
            cur = self.conn.cursor()
            query = f"""
            SELECT examinations.id, user_id, image_id, images.name, image_class, processed_at
            FROM das_data.examinations examinations
            JOIN das_data.images images ON examinations.image_id = images.id
            WHERE user_id = '{patient_id}'
            ORDER BY processed_at;
            """

            cur.execute(query)
            therapies = cur.fetchall()
            cur.close()

            for therapy in therapies:
                examination_dict = dict()
                examination_dict["id"] = therapy[0]
                examination_dict["user_id"] = therapy[1]
                examination_dict["image_id"] = therapy[2]
                examination_dict["image_name"] = therapy[3]
                examination_dict["image_class"] = therapy[4]
                examination_dict["processed_at"] = therapy[5]
                examinations_list.append(examination_dict)

            status_flag = True
            logging.info(f"Examinations for patient {patient_id} successfully fetched")
        except Exception as e:
            logging.error(f"Unable to fetch examinations for patient {patient_id} due to error: {e}")
        return status_flag, examinations_list


db_client = DBClient()
