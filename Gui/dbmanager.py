import sqlite3
from variables import *
import os

class SQLHandler:

    def __init__(self):
        if os.path.isfile(DB_NAME) is False:
            open(DB_NAME,"w").close()
            self.handle = sqlite3.connect(DB_NAME)
            self.resetdb()
        self.handle = sqlite3.connect(DB_NAME)
        self.handle.text_factory = str

    def execute(self,query,params = ()):
        self.handle.execute(query,params)

    def resetdb(self):
        try:
            self.execute(DROP_VIDEOINFO)
            self.execute(DROP_IDSTABLE)
            self.execute(DROP_COMMONTABLE)
            self.execute(DROP_IMDBTABLE)
            self.execute(DROP_RTTABLE)
        except:
            "First setup of tables!"
        self.execute(CREATE_VIDEOINFO)
        self.execute(CREATE_IDSTABLE)
        self.execute(CREATE_COMMONTABLE)
        self.execute(CREATE_IMDBTABLE)
        self.execute(CREATE_RTTABLE)
        self.handle.commit()

    def insert_into_videoinfo(self,name,address,seen):
        try:
            self.execute('INSERT INTO videoinfo (videoname , address, seen) values(?,?,?) ',(name,address,seen))
            self.handle.commit()
        except:
            print "WARNING : Old values found ... not added"

    def insert_into_idstable(self,dic):
        self.execute('INSERT INTO idstable values(?,?,?)',(dic['id'],dic['imdb_id'],dic['rt_id']))
        self.handle.commit()

    def insert_into_commontable(self,dic):
        self.execute('INSERT INTO commontable values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(dic['id'],dic['name'],dic['year'],dic['directors'],dic['kind'],dic['plot'],dic['image'],dic['genres'],dic['cast'],dic['writers'],dic['runtime'],dic['cinematographers'],dic['musicians'],dic['languages'],dic['producers'],dic['year_start'],dic['year_end'],dic['num_seasons']))
        self.handle.commit()

    def insert_into_imdbtable(self,dic):
        self.execute('INSERT INTO imdbtable  values(?,?,?,?,?,?)',(dic['imdb_id'],dic['url'],dic['rating'],dic['votes'],dic['imdb_top250'],dic['review']))
        self.handle.commit()

    def insert_into_rt_table(self,dic):
        self.execute('INSERT INTO rttable values(?,?,?,?,?,?,?)',(dic['rt_id'],dic['name'],dic['url'],dic['rating_audience'],dic['rating_critics'],dic['reviews_audience'],dic['reviews_critics']))
        self.handle.commit()

    def delete_record(self,id):
        """Delete entry of all records with id corresponding to this one"""
        self.handle.execute("DELETE FROM VIDEOINFO WHERE id == %d" % id)
        self.handle.execute("DELETE FROM COMMONTABLE WHERE id == %d" % id)
        try:
            imdb_id = self.handle.execute("select imdb_id from idstable where id == %d" % id).fetchone()[0]
            rt_id = self.handle.execute("select rt_id from idstable where id == %d" % id).fetchone()[0]
            self.handle.execute("DELETE FROM RTTABLE WHERE rt_id == %d" % rt_id)
            self.handle.execute("DELETE FROM IMDBTABLE WHERE imdb_id == %d" % imdb_id)
            self.handle.execute("DELETE FROM IDSTABLE WHERE id == %d" % id)
        except Exception as e:
            print e
        self.handle.commit()


    def close(self):
        self.handle.close()