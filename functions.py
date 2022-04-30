import pymysql
from hashids import Hashids
from validators import url
import requests
from bs4 import BeautifulSoup

hashids = Hashids(min_length=6, salt='y1234567890we23456u2h21fbqlkef3323456789v4g8786jh1k00787l')
db = pymysql.connect()


def checkIdInDatabase(shortText):
    connection = db.cursor()
    connection.execute('SELECT original_url, clicks FROM urls WHERE hash_id = (%s) OR custom_name = (%s)',
                       (shortText, shortText)
                       )
    url_data = connection.fetchone()

    if url_data:
        original_url = url_data[0]
        clicks = url_data[1]
        connection.execute('UPDATE urls SET clicks = (%s) WHERE hash_id = (%s) OR custom_name = (%s)',
                           (clicks + 1, shortText, shortText)
                           )
        db.commit()
        connection.close()
        return original_url
    else:
        return None


def writeInDatabase(urlInput, customName=None):
    connection = db.cursor()
    if customName:
        connection.execute('INSERT INTO urls (original_url, custom_name) VALUES (%s, %s)',
                           (urlInput, customName)
                           )
        db.commit()
        connection.close()
        return customName
    connection.execute('INSERT INTO urls (original_url) VALUES (%s)',
                       (urlInput,)
                       )
    rowId = connection.lastrowid
    hashId = hashids.encode(rowId)
    connection.execute('UPDATE urls SET hash_id = (%s) WHERE id = (%s)',
                       (hashId, rowId)
                       )
    db.commit()
    connection.close()

    return hashId


def getWebMeta(weburl):
    res = requests.get(url=weburl)
    soup = BeautifulSoup(res.text, "html.parser")

    retO = {}
    if soup.title:
        retO['title'] = soup.title.text
    meta_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_tag:
        retO['description'] = meta_tag['content']
    return retO


def checkUrl(userInput):
    return url(userInput)
