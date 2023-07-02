from db_module.db_client import db_client, logging


def perform_registration(user_dict):
    user_id = None
    status_flag = db_client.register_search(user_dict["username"])
    if status_flag:
        logging.info(f"Starting user registration")
        status, return_uuid = db_client.register_user(user_dict)
        if status:
            user_id = return_uuid
        else:
            logging.warning(f"User not registered properly")
        logging.info(f"End of user registration")
    else:
        logging.warning(f"Unable to register user")
    return user_id


def perform_login(user_dict):
    status_flag, user_id = db_client.login_search(user_dict["username"], user_dict["password"])
    if status_flag:
        logging.info(f"Successful login for user with username: {user_dict['username']}")
    else:
        logging.info(f"Unable to login user with username: {user_dict['username']}")
    return user_id
