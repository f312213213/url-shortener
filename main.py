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
    if 'uid' not in request.headers:
        return response(urlNotFound, 404)
    data = request.get_json()
    if not checkUrl(data['url']):
        return response(notURL, 403)
    if 'customName' in data:
        try:
            customName = writeInDatabase(urlInput=data['url'], userUid=data['uid'], customName=data['customName'])
            message = {
                'message': 'success',
                'shorted': customName
            }
            return response(message, 200)
        except pymysql.err.IntegrityError:
            return response(duplicateCustomName, 406)

    try:
        hashId = writeInDatabase(urlInput=data['url'], userUid=data['uid'])
        message = {
            'message': 'success',
            'shorted': hashId
        }
        return response(message, 200)
    except pymysql.err.IntegrityError:
        return response(duplicateCustomName, 406)


@app.route('/<shortText>', methods=['GET'])
@cross_origin()
def resolveShortText(shortText):
    urlInDatabase = checkIdInDatabase(shortText)
    if urlInDatabase is None:
        return response(urlNotFound, 404)
    meta = getWebMeta(urlInDatabase)
    message = {
        'originURL': urlInDatabase,
        'meta': meta
    }
    return response(message, 200)


@app.route('/record/<userID>', methods=['GET'])
@cross_origin()
def getUserRecord(userID):
    if 'uid' not in request.headers or userID != request.headers['uid']:
        return response(urlNotFound, 404)
    urlData = getUserRecordFromDB(userID)
    message = {
        'urlData': urlData
    }
    return response(message, 200)


@app.route('/create', methods=['POST'])
@cross_origin()
def createUser():
    data = request.get_json()
    responseText = createUserInDB(data['uid'], data['userName'])
    message = {
        'msg': responseText
    }
    return response(message, 200)


@app.route('/', methods=['GET'])
@cross_origin()
def index():
    message = {
        'message': 'This is the base url of this URL Shortener api.'
    }
    return response(message, 200)


if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost', port=5001)
