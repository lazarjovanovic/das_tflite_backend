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


def perform_adding_new_therapy(therapy_dict):
    status_flag = db_client.add_therapy(therapy_dict)
    if status_flag:
        logging.info(f"Successful addition of therapy {therapy_dict['disease']} for doctor {therapy_dict['doctor_id']}")
    else:
        logging.info(f"Unable to add therapy {therapy_dict['disease']} for doctor {therapy_dict['doctor_id']}")
    return status_flag


def perform_updating_therapy(therapy_dict):
    status_flag, therapy_id = db_client.update_therapy(therapy_dict)
    if status_flag:
        logging.info(f"Successful update of therapy {therapy_id} for doctor {therapy_dict['doctor_id']}")
    else:
        logging.info(f"Unable to update therapy {therapy_id} for doctor {therapy_dict['doctor_id']}")
    return status_flag


def perform_get_therapies_by_doctor_id(doctor_id):
    status_flag, therapies = db_client.get_therapies_by_doctor_id(doctor_id)
    if status_flag:
        logging.info(f"Therapies for doctor {doctor_id} successfully collected")
    else:
        logging.info(f"Therapies for doctor {doctor_id} not successfully collected")
    return therapies


def perform_get_therapies_by_disease(disease):
    status_flag, therapies = db_client.get_therapies_by_disease(disease)
    if status_flag:
        logging.info(f"Therapies for disease {disease} successfully collected")
    else:
        logging.info(f"Therapies for disease {disease} not successfully collected")
    return therapies


def perform_delete_therapy_by_id(therapy_id):
    status_flag = db_client.delete_therapy_by_id(therapy_id)
    if status_flag:
        logging.info(f"Therapies with id {therapy_id} successfully deleted")
    else:
        logging.info(f"Therapies with id {therapy_id} not successfully deleted")
    return status_flag


def perform_examination(examination_dict):
    return_dict = {"resulting_disease": "", "therapies": list()}

    # TODO: IMPLEMENT FOLLOWING METHOD
    # image_processing_status_flag, resulting_disease = run_image_classification(examination_dict["image_name"])
    image_processing_status_flag = True
    resulting_disease = "Basal cell cancer"

    if image_processing_status_flag:
        return_dict["resulting_disease"] = resulting_disease
        # TODO: UPDATE TO FILTER WITH SURVEY
        status_flag, therapies = db_client.get_therapies_by_disease(resulting_disease)
        if status_flag:
            return_dict["therapies"] = therapies
        else:
            logging.warning(f"Unable to fetch therapies for disease {resulting_disease}")
    else:
        logging.warning(f"Unable to process image {examination_dict['image_name']} "
                        f"of patient {examination_dict['examination_dict']}")

    status_flag, image_id = db_client.add_image(examination_dict["image_name"], image_processing_status_flag)
    if status_flag is False:
        logging.warning("Image wasn't uploaded successfully")
        return return_dict

    status_flag = db_client.add_examination(examination_dict["patient_id"], image_id, resulting_disease)
    if status_flag is False:
        logging.warning("Examination log wasn't uploaded successfully")

    return return_dict


def perform_get_examinations_by_patient_id(patient_id):
    status_flag, examinations = db_client.get_examinations_by_patient_id(patient_id)
    if status_flag:
        logging.info(f"Examinations for patient {patient_id} successfully collected")
    else:
        logging.info(f"Examinations for patient {patient_id} not successfully collected")
    return examinations


def perform_get_examinations_images_by_ids(image_ids):
    # https://stackoverflow.com/questions/8637153/how-to-return-images-in-flask-response
    # https://stackoverflow.com/questions/69881709/downloading-multiple-files-in-flask
    pass
