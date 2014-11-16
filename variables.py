"""
This file contains all
Queries
Global Variable Strings
"""

DB_NAME = "test.db"

ALLOWED_EXTENSIONS = (".mp4", ".MP4", ".mkv", ".MKV", ".avi", ".AVI", ".flv", ".FLV", ".webm", ".WEBM")

CREATE_VIDEOINFO = '''CREATE TABLE VIDEOINFO
           (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
           videoname           TEXT NOT NULL UNIQUE ,
           address          TEXT    NOT NULL
           );'''

CREATE_IDSTABLE = '''CREATE TABLE IDSTABLE
           (id  INT PRIMARY KEY ,
           imdb_id INT NOT NULL,
           rt_id INT
           );'''

CREATE_COMMONTABLE = '''CREATE TABLE COMMONTABLE
           (id  INT PRIMARY KEY ,
           name     TEXT    NOT NULL,
           year     INT    NOT NULL,
           director    TEXT    NOT NULL,
           kind          TEXT    NOT NULL,
           plot    TEXT    NOT NULL,
           image    TEXT    NOT NULL,
           genres   TEXT    NOT NULL,
           cast TEXT NOT NULL,
           writers  TEXT    NOT NULL,
           runtime  TEXT    NOT NULL,
           cinematographers     TEXT    NOT NULL,
           musicians    TEXT    NOT NULL,
           languages    TEXT    NOT NULL,
           producers    TEXT    NOT NULL,
           year_start   TEXT,
           year_end TEXT,
           number_of_seasons TEXT
           );'''

CREATE_IMDBTABLE = '''CREATE TABLE IMDBTABLE
           (imdb_id INT PRIMARY KEY NOT NULL,
           url    TEXT ,
           rating    TEXT,
           votes    TEXT,
           imdb_top250 TEXT
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

CREATE_REVIEWSTABLE = """
					CREATE TABLE REVIEWS_TABLE(
						id INTEGER PRIMARY KEY AUTOINCREMENT,
						imdb_id INTEGER NOT NULL,
						review_url text,
						reviewer text,
						review text
						);
					"""

DROP_VIDEOINFO = 'DROP TABLE IF EXISTS VIDEOINFO'

DROP_IDSTABLE = 'DROP TABLE IF EXISTS IDSTABLE'

DROP_COMMONTABLE = 'DROP TABLE IF EXISTS COMMONTABLE'

DROP_IMDBTABLE = 'DROP TABLE IF EXISTS IMDBTABLE'

DROP_RTTABLE = 'DROP TABLE IF EXISTS RTTABLE'

DROP_REVIEWSTABLE = 'DROP TABLE IF EXISTS REVIEWS_TABLE'

