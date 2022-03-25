import pymysql
from hashids import Hashids
from validators import url
hashids = Hashids(min_length=6, salt='y1234567890we23456u2h21fbqlkef3323456789v4g8786jh1k00787l')
db = pymysql.connect(your database information)


# def init_db():
#     cursor = db.cursor()
#     connection.commit()
#     connection.close()


# def get_db_connection():
#     # if not path.exists('database.db'):
#     #     init_db()
#     connect = mysql.connect()
#     connect.row_factory = connect.Row
#     return connect


def checkIdInDatabase(shortText):
    connection = db.cursor()
    try:
        connection.execute(
            'SELECT original_url, clicks FROM urls WHERE hash_id = (%s)',
            shortText
        )
        url_data = connection.fetchone()
        original_url = url_data[0]
        if original_url:
            clicks = url_data[1]
            connection.execute('UPDATE urls SET clicks = (%s) WHERE hash_id = (%s)', (clicks + 1, shortText))
            db.commit()
            connection.close()
            return original_url
    except:
        return None


def writeInDatabase(url):
    connection = db.cursor()
    connection.execute('INSERT INTO urls (original_url) VALUES (%s)', (url, ))
    hashId = hashids.encode(connection.lastrowid)
    connection.execute('UPDATE urls SET hash_id = (%s) WHERE original_url = (%s)', (hashId, url))
    db.commit()
    connection.close()

    return hashId


def checkUrl(userInput):
    return url(userInput)
