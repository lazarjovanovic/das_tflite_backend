import os
from flask import Flask, request, jsonify, send_file
import flask_module.features as flask_features
import base64
from utils.read_config import PATH_STORE_EXAMINATION_IMAGES
from datetime import datetime

app = Flask(__name__)


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    data["password"] = base64.b64encode(data["password"].encode("utf-8"))
    data["password"] = base64.b64decode(data["password"]).decode("utf-8")

    user_id = flask_features.perform_login(data)
    return_dict = {"user_id": user_id}
    return jsonify(return_dict)


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    data["password"] = base64.b64encode(data["password"].encode("utf-8"))
    data["password"] = base64.b64decode(data["password"]).decode("utf-8")

    user_id = flask_features.perform_registration(data)
    return_dict = {"user_id": user_id}
    return jsonify(return_dict)


@app.route("/add_therapy", methods=["POST"])
def add_therapy():
    authorization_id = request.headers.get("Authorization", "")
    if authorization_id == "":
        return "Authorization failed", 401

    data = request.json
    status_flag = flask_features.perform_adding_new_therapy(data)
    return_dict = {"status_flag": status_flag}
    return jsonify(return_dict)


@app.route("/update_therapy", methods=["PUT"])
def update_therapy():
    authorization_id = request.headers.get("Authorization", "")
    if authorization_id == "":
        return "Authorization failed", 401

    data = request.json
    status_flag = flask_features.perform_updating_therapy(data)
    return_dict = {"status_flag": status_flag}
    return jsonify(return_dict)


@app.route("/get_therapies_by_doctor_id/<doctor_id>", methods=["GET"])
def get_therapies_by_doctor_id(doctor_id: str):
    authorization_id = request.headers.get("Authorization", "")
    if authorization_id == "":
        return "Authorization failed", 401

    therapies = flask_features.perform_get_therapies_by_doctor_id(doctor_id)
    return jsonify(therapies)


@app.route("/get_therapies_by_disease/<disease_id>", methods=["GET"])
def get_therapies_by_disease(disease_id: str):
    authorization_id = request.headers.get("Authorization", "")
    if authorization_id == "":
        return "Authorization failed", 401

    therapies = flask_features.perform_get_therapies_by_disease(disease_id)
    return jsonify(therapies)


@app.route("/delete_therapy_by_id/<therapy_id>", methods=["DELETE"])
def delete_therapy_by_id(therapy_id: str):
    authorization_id = request.headers.get("Authorization", "")
    if authorization_id == "":
        return "Authorization failed", 401

    status_flag = flask_features.perform_delete_therapy_by_id(therapy_id)
    return_dict = {"status_flag": status_flag}
    return jsonify(return_dict)


@app.route("/process_examination", methods=["POST"])
def process_examination():
    authorization_id = request.headers.get("Authorization", "")
    if authorization_id == "":
        return "Authorization failed", 401

    examination_dict = dict()
    examination_dict["location"] = request.form["location"]
    examination_dict["length_of_existence_weeks"] = request.form["length_of_existence_weeks"]
    examination_dict["dimension_width_mm"] = request.form["dimension_width_mm"]
    examination_dict["dimension_height_mm"] = request.form["dimension_height_mm"]
    examination_dict["patient_age"] = request.form["patient_age"]
    examination_dict["gender"] = request.form["gender"]
    examination_dict["number_of_instances"] = request.form["number_of_instances"]
    examination_dict["patient_id"] = request.form["patient_id"]

    image = request.files.get('image', '')
    image_filename = image.filename
    store_path = PATH_STORE_EXAMINATION_IMAGES + "/" + image_filename
    image.save(store_path)

    datetime_now = str(datetime.now()).replace(":", "-").replace(".", "-").replace(" ", "_")
    new_image_filename = str(examination_dict["patient_id"]) + "_" + datetime_now
    update_store_path = PATH_STORE_EXAMINATION_IMAGES + "/" + new_image_filename
    os.rename(store_path, update_store_path)

    examination_dict["image_name"] = new_image_filename
    return_dict = flask_features.perform_examination(examination_dict)
    return jsonify(return_dict)


@app.route("/get_examinations_by_patient_id/<patient_id>", methods=["GET"])
def get_examinations_by_patient_id(patient_id: str):
    authorization_id = request.headers.get("Authorization", "")
    if authorization_id == "":
        return "Authorization failed", 401

    examinations = flask_features.perform_get_examinations_by_patient_id(patient_id)
    return jsonify(examinations)


@app.route("/get_examination_images", methods=["POST"])
def get_examination_images():
    authorization_id = request.headers.get("Authorization", "")
    if authorization_id == "":
        return "Authorization failed", 401

    image_ids = request.json
    images = flask_features.perform_get_examinations_images_by_ids(image_ids)
    return send_file(images, as_attachment=True, download_name="images.zip")
