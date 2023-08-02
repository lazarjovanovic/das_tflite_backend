from db_module.db_client import db_client, logging
from image_processing.image_processing import ImageProcessing
from glob import glob
from io import BytesIO
from zipfile import ZipFile
from datetime import date
import os

img_processing_class = ImageProcessing()
DEFAULT_DOCTOR_ID = "00000000-0000-0000-0000-000000000000"


def perform_registration(user_dict):
    user_id = None
    user_role = None
    dob = user_dict["dob"]
    date_now = str(date.today())
    if dob >= date_now:
        logging.warning(f"Unable to create user with DOB in the future")
        return user_id, user_role
    status_flag = db_client.register_search(user_dict["username"])
    if status_flag:
        logging.info(f"Starting user registration")
        status, return_uuid, return_role = db_client.register_user(user_dict)
        if status:
            user_id = return_uuid
            user_role = return_role
        else:
            logging.warning(f"User not registered properly")
        logging.info(f"End of user registration")
    else:
        logging.warning(f"Unable to register user")
    return user_id, user_role


def perform_login(user_dict):
    status_flag, user_id, user_role = db_client.login_search(user_dict["username"], user_dict["password"])
    if status_flag:
        logging.info(f"Successful login for user with username: {user_dict['username']}")
    else:
        logging.info(f"Unable to login user with username: {user_dict['username']}")
    return user_id, user_role


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


def filter_therapies(list_of_therapies, examination_dict):
    filtered_therapies = list()
    for therapy in list_of_therapies:
        if examination_dict["location"] != therapy["location"]:
            continue
        if not (therapy["length_of_existence_weeks_from"]
                <= int(examination_dict["length_of_existence_weeks"])
                < therapy["length_of_existence_weeks_to"]):
            continue
        if therapy["dimension_width_mm"] != int(examination_dict["dimension_width_mm"]):
            continue
        if therapy["dimension_height_mm"] != int(examination_dict["dimension_height_mm"]):
            continue
        if not (therapy["patient_age_from"]
                <= int(examination_dict["patient_age"])
                < therapy["patient_age_to"]):
            continue
        if therapy["gender"] != examination_dict["gender"]:
            continue
        if not (therapy["number_of_instances_from"]
                <= int(examination_dict["number_of_instances"])
                < therapy["number_of_instances_to"]):
            continue
        filtered_therapies.append(therapy)
    if len(filtered_therapies) == 0:
        filtered_therapies = [item for item in list_of_therapies if item["doctor_id"] == DEFAULT_DOCTOR_ID]

    for therapy in filtered_therapies:
        if therapy["location"] == "":
            therapy["location"] = "All locations"
        if therapy["gender"] == "":
            therapy["gender"] = "All genders"

        loe_weeks_start = therapy["length_of_existence_weeks_from"]
        loe_weeks_end = therapy["length_of_existence_weeks_to"]
        if loe_weeks_end == 200:
            if loe_weeks_start == 0:
                therapy["length_of_existence_weeks"] = "All lengths of existence"
            else:
                therapy["length_of_existence_weeks"] = str(loe_weeks_start) + "+"
        else:
            therapy["length_of_existence_weeks"] = str(loe_weeks_start) + "-" + str(loe_weeks_end)
        del therapy["length_of_existence_weeks_from"]
        del therapy["length_of_existence_weeks_to"]

        age_start = therapy["patient_age_from"]
        age_end = therapy["patient_age_to"]
        if age_end == 200:
            if age_start == 0:
                therapy["patient_age"] = "All ages"
            else:
                therapy["patient_age"] = str(age_start) + "+"
        else:
            therapy["patient_age"] = str(age_start) + "-" + str(age_end)
        del therapy["patient_age_from"]
        del therapy["patient_age_to"]

        number_of_instances_start = therapy["number_of_instances_from"]
        number_of_instances_end = therapy["number_of_instances_to"]
        if number_of_instances_end == 200:
            if number_of_instances_start == 0:
                therapy["number_of_instances"] = "All numbers of occurrences"
            else:
                therapy["number_of_instances"] = str(number_of_instances_start) + "+"
        else:
            therapy["number_of_instances"] = str(number_of_instances_start) + "-" + str(number_of_instances_end)
        del therapy["number_of_instances_from"]
        del therapy["number_of_instances_to"]

    return filtered_therapies


def perform_examination(examination_dict):
    return_dict = {"resulting_disease": "", "therapies": list()}

    status_flag, result_disease, result_confidence = \
        img_processing_class.run_odt_and_draw_results(examination_dict["image_name"])
    # status_flag = True
    # result_disease = "Basal cell cancer"
    # result_confidence = 99.6

    if status_flag:
        logging.info(f"Image {examination_dict['image_name']} "
                     f"classified as {result_disease} with confidence {result_confidence}%")

        return_dict["resulting_disease"] = result_disease
        status_flag, therapies = db_client.get_therapies_by_disease(result_disease)
        therapies = filter_therapies(therapies, examination_dict)
        if status_flag:
            return_dict["therapies"] = therapies
        else:
            logging.warning(f"Unable to fetch therapies for disease {result_disease}")
    else:
        logging.warning(f"Unable to process image {examination_dict['image_name']} "
                        f"of patient {examination_dict['examination_dict']}")

    status_flag, image_id = db_client.add_image(examination_dict["image_name"], status_flag)
    if status_flag is False:
        logging.warning("Image wasn't uploaded successfully")
        return return_dict

    status_flag = db_client.add_examination(examination_dict["patient_id"], image_id, result_disease)
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

    stream = BytesIO()
    with ZipFile(stream, 'w') as zf:
        for file in image_ids:
            zf.write("examination_images/" + file, file + '.jpg')
    stream.seek(0)
    return stream
