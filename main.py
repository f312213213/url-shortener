from flask import Flask, request
from flask_cors import cross_origin


from functions import *
from ERROR import *
from response import *

app = Flask(__name__)


@app.route('/short', methods=['GET', 'POST'])
@cross_origin()
def short():
    if request.method != 'POST':
        return response(onlyPost, 405)
    data = request.get_json()
    if not checkUrl(data['url']):
        return response(notURL, 403)
    if len(data['customName']) > 0:
        try:
            customName = writeInDatabase(data['url'], data['customName'])
            message = {
                'message': 'success',
                'shorted': customName
            }
            return response(message, 200)
        except pymysql.err.IntegrityError:
            return response(duplicateCustomName, 406)

    hashId = writeInDatabase(data['url'])
    message = {
        'message': 'success',
        'shorted': hashId
    }
    return response(message, 200)


@app.route('/<shortText>', methods=['GET'])
@cross_origin()
def resolveShortText(shortText):
    url = checkIdInDatabase(shortText)
    if url:
        message = {
            'originURL': url
        }
        return response(message, 200)
    return response(urlNotFound, 404)


if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost', port=5001)
