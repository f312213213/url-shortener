import json
import pymysql
import requests
import configparser

from hashids import Hashids
from validators import url
from bs4 import BeautifulSoup

cf = configparser.ConfigParser()
cf.read("config.ini")

hashids = Hashids(min_length=6, salt=cf.get("HASH", "salt"))


def checkIdInDatabase(shortText):
    db = pymysql.connect(
        host=cf.get("DATABASE", "host"),
        port=int(cf.get("DATABASE", "port")),
        user=cf.get("DATABASE", "user"),
        passwd=cf.get("DATABASE", "passwd"),
        db=cf.get("DATABASE", "db")
    )
    connection = db.cursor()
    connection.execute('SELECT original_url, clicks FROM urls_table WHERE hash_id = (%s) OR custom_name = (%s)',
                       (shortText, shortText)
                       )
    url_data = connection.fetchone()

    if url_data:
        original_url = url_data[0]
        clicks = url_data[1]
        connection.execute('UPDATE urls_table SET clicks = (%s) WHERE hash_id = (%s) OR custom_name = (%s)',
                           (clicks + 1, shortText, shortText)
                           )
        db.commit()
        connection.close()
        return original_url
    else:
        return None


def writeInDatabase(urlInput, userUid, customName=None):
    db = pymysql.connect(
        host=cf.get("DATABASE", "host"),
        port=int(cf.get("DATABASE", "port")),
        user=cf.get("DATABASE", "user"),
        passwd=cf.get("DATABASE", "passwd"),
        db=cf.get("DATABASE", "db")
    )
    connection = db.cursor()
    if customName:
        connection.execute('INSERT INTO urls_table (original_url, custom_name, user_uid) VALUES (%s, %s, %s)',
                           (urlInput, customName, userUid)
                           )
        db.commit()
        connection.close()
        return customName
    connection.execute('INSERT INTO urls_table (original_url, user_uid) VALUES (%s, %s)',
                       (urlInput, userUid)
                       )
    rowId = connection.lastrowid
    hashId = hashids.encode(rowId)
    connection.execute('UPDATE urls_table SET hash_id = (%s) WHERE id = (%s)',
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


def getUserRecordFromDB(userUid):
    db = pymysql.connect(
        host=cf.get("DATABASE", "host"),
        port=int(cf.get("DATABASE", "port")),
        user=cf.get("DATABASE", "user"),
        passwd=cf.get("DATABASE", "passwd"),
        db=cf.get("DATABASE", "db")
    )
    connection = db.cursor()
    connection.execute('SELECT * FROM urls_table WHERE user_uid = (%s)', userUid)
    row_headers = [x[0] for x in connection.description]
    rv = connection.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    connection.close()
    return json.dumps(json_data, sort_keys=True, default=str)


def createUserInDB(userUid, userName):
    try:
        db = pymysql.connect(
            host=cf.get("DATABASE", "host"),
            port=int(cf.get("DATABASE", "port")),
            user=cf.get("DATABASE", "user"),
            passwd=cf.get("DATABASE", "passwd"),
            db=cf.get("DATABASE", "db")
        )
        connection = db.cursor()
        connection.execute('INSERT INTO user_table (user_name, uid) VALUES (%s, %s)', (userName, userUid))
        db.commit()
        connection.close()
        return 'user create'
    except:
        return 'user already create'

def checkUrl(userInput):
    return url(userInput)
