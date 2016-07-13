"""
This file contains all
Queries
Global Variable Strings
"""

DB_NAME = "test.db"

ALLOWED_EXTENSIONS = (".mp4", ".MP4", ".mkv", ".MKV", ".avi", ".AVI", ".flv", ".FLV", ".webm", ".WEBM")

KEYS_COMMONTABLE = ["id","name","year","directors","kind","plot","image",
                    "genres","cast","writers","runtime",
                    "cinematographers","musicians","languages","producers",
                    "year_start","year_end","num_seasons"]

KEYS_IDSTABLE = ['id','imdb_id','rt_id']

KEYS_IMDBTABLE = ['imdb_id','url','rating','votes','imdb_top250',"review"]

KEYS_RTTABLE = ['rt_id','name','url','rating_audience','rating_critics','reviews_audience','reviews_critics']



CREATE_VIDEOINFO = '''CREATE TABLE VIDEOINFO
           (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
           videoname           TEXT NOT NULL UNIQUE ,
           address          TEXT    NOT NULL,
           seen BOOLEAN DEFAULT 0
           );'''

CREATE_IDSTABLE = '''CREATE TABLE IDSTABLE
           (id  INT PRIMARY KEY ,
           imdb_id INT NOT NULL,
           rt_id INT
           );'''

CREATE_COMMONTABLE = '''CREATE TABLE COMMONTABLE
           (id  INT PRIMARY KEY ,
           name     TEXT    NOT NULL,
           year     INT,
           directors    TEXT,
           kind          TEXT,
           plot    TEXT,
           image    BLOB,
           genres   TEXT,
           cast TEXT,
           writers  TEXT,
           runtime  TEXT,
           cinematographers     TEXT,
           musicians    TEXT,
           languages    TEXT,
           producers    TEXT,
           year_start   TEXT,
           year_end TEXT,
           num_seasons TEXT
           );'''

CREATE_IMDBTABLE = '''CREATE TABLE IMDBTABLE
           (imdb_id INT PRIMARY KEY NOT NULL,
           url    TEXT ,
           rating    TEXT,
           votes    TEXT,
           imdb_top250 TEXT,
           review TEXT
           );'''

CREATE_RTTABLE = '''CREATE TABLE RTTABLE
           (rt_id    INT  PRIMARY KEY NOT NULL,
           name TEXT,
           url    TEXT,
           rating_audience    TEXT,
           rating_critics    TEXT,
           reviews_audience    TEXT ,
           reviews_critics    TEXT
           );'''

DROP_VIDEOINFO = 'DROP TABLE IF EXISTS VIDEOINFO'

DROP_IDSTABLE = 'DROP TABLE IF EXISTS IDSTABLE'

DROP_COMMONTABLE = 'DROP TABLE IF EXISTS COMMONTABLE'

DROP_IMDBTABLE = 'DROP TABLE IF EXISTS IMDBTABLE'

DROP_RTTABLE = 'DROP TABLE IF EXISTS RTTABLE'

