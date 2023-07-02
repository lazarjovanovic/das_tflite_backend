from flask import Flask, request, jsonify
import flask_module.features as flask_features
import base64

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

