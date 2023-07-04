import os.path
from flask_module.endpoints import app
from flask_module.features import db_client, logging
from utils.read_config import get_flask_config, PATH_STORE_EXAMINATION_IMAGES


if __name__ == '__main__':
    try:
        flask_config = get_flask_config()
        if flask_config:
            version = db_client.test_connection()
            if version is not None:
                logging.info(f"App starting")
                db_setup_status = db_client.setup_database()
                if db_setup_status:
                    if os.path.exists(PATH_STORE_EXAMINATION_IMAGES) is False:
                        os.mkdir(PATH_STORE_EXAMINATION_IMAGES)

                    app.run(host=flask_config["host"],
                            port=int(flask_config["port"]),
                            debug=eval(flask_config["debug"]))
                else:
                    logging.error(f"DB setup not performed properly")
            else:
                logging.error(f"Unable to run app as DB connection is not established properly")
        else:
            logging.error(f"Unable to run app as Flask config is not read properly")
    except Exception as e:
        logging.error(f"Service terminated due to error: {e}")
