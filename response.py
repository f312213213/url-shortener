from flask import make_response, jsonify


def response(responseMsg: dict, statusCode: int):
    return make_response(jsonify(responseMsg), statusCode)
