import sqlite3
from hashids import Hashids
from os import path

hashids = Hashids(min_length=6, salt='y1234567890weu2h21fbqlkef3323456789v4g8786jh1k00787l')


def init_db():
    connection = sqlite3.connect('database.db')
    with open('schema.sql') as f:
        connection.executescript(f.read())
    connection.commit()
    connection.close()


def get_db_connection():
    if not path.exists('database.db'):
        init_db()
    connect = sqlite3.connect('database.db')
    connect.row_factory = sqlite3.Row
    return connect


def checkIdInDatabase(shortText):
    connection = get_db_connection()
    original_id = hashids.decode(shortText)
    if original_id:
        try:
            original_id = original_id[0]
            url_data = connection.execute(
                'SELECT original_url, clicks FROM urls WHERE id = (?)',
                (original_id,)
            ).fetchone()
            original_url = url_data['original_url']
            if original_url:
                clicks = url_data['clicks']
                connection.execute('UPDATE urls SET clicks = ? WHERE id = ?', (clicks + 1, original_id))
                connection.commit()
                connection.close()
                return original_url
        except:
            return None


def writeInDatabase(url):
    connection = get_db_connection()
    url_data = connection.execute('INSERT INTO urls (original_url) VALUES (?)', (url,))
    hashId = hashids.encode(url_data.lastrowid)
    connection.execute('UPDATE urls SET hash_id = ? WHERE original_url = ?', (hashId, url))
    connection.commit()
    connection.close()

    return hashId
