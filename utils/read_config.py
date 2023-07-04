from configparser import ConfigParser
from utils.logger import logging

PATH_STORE_EXAMINATION_IMAGES = "examination_images/"


def get_flask_config(filename='config.ini'):
    flask_config = dict()
    try:
        parser = ConfigParser()
        parser.read(filename)

        # reading flask config
        params = parser.items('FLASK')
        for param in params:
            flask_config[param[0]] = param[1]

        logging.info("Flask configuration successfully fetched")
    except Exception as e:
        logging.error(f"Unable to fetch Flask configuration properly due to error: {e}")

    return flask_config


def get_db_config(filename='config.ini'):
    db_config = dict()
    try:
        parser = ConfigParser()
        parser.read(filename)

        # reading postgres config
        params = parser.items('POSTGRESQL')
        for param in params:
            db_config[param[0]] = param[1]

        logging.info("DB configuration successfully fetched")
    except Exception as e:
        logging.error(f"Unable to fetch DB configuration properly due to error: {e}")

    return db_config
