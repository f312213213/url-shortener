from flask import Flask, redirect, make_response, jsonify, request
from flask_cors import cross_origin


from functions import *
from ERROR import *

app = Flask(__name__)


@app.route('/short', methods=['GET', 'POST'])
@cross_origin()
def short():
    if request.method != 'POST':
        return make_response(jsonify(onlyPost), 400)
    url = request.get_json()
    if not checkUrl(url['url']):
        return make_response(jsonify(notURL), 403)
    hashId = writeInDatabase(url['url'])
    message = {
        'message': 'success',
        'hashId': hashId
    }
    return make_response(jsonify(message), 200)


@app.route('/<shortText>', methods=['GET'])
@cross_origin()
def resolveShortText(shortText):
    url = checkIdInDatabase(shortText)
    if url:
        message = {
            'originURL': url
        }
        return make_response(jsonify(message), 200)
    return make_response(jsonify(urlNotFound), 404)


if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost', port=5001)
