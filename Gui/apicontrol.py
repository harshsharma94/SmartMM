import imdb
from rottentomatoes import RT
import re
from bs4 import BeautifulSoup
import urllib2
from variables import KEYS_COMMONTABLE,\
    KEYS_IDSTABLE,KEYS_IMDBTABLE,\
    KEYS_RTTABLE
from imdbpie import Imdb

import sqlite3

class VideoHandler:
    """
    Handler for parsing and extracting relevant info from given Video name
    """

    def __init__(self,name):
        self.name = name

    def infodump(self):
        """
        Dump information dict witth relevant fields
        """
        idtable = dict.fromkeys(KEYS_IDSTABLE)
        rttable = dict.fromkeys(KEYS_RTTABLE)
        #Construct Common table, IMDb table
        commontable,imdbtable = self.dump_imdb()
        #Contruct IDTable
        idtable["imdb_id"] = imdbtable["imdb_id"]
        if commontable["kind"] == "movie":
            #Contruct RT table
            rttable = self.dump_rt()
            idtable["rt_id"] = rttable["rt_id"]
        return idtable,commontable,imdbtable,rttable

    def dump_imdb(self):
        commontable = dict.fromkeys(KEYS_COMMONTABLE)
        imdbtable = dict.fromkeys(KEYS_IMDBTABLE)
        ia = imdb.IMDb()
        info = ia.search_movie(self.name,results=1)[0]
        ia.update(info)
        #Basic Info
        try:
            commontable["name"] = info["long imdb canonical title"]
            commontable["year"] = info["year"]
            commontable["directors"] = ";".join([d["long imdb canonical name"] for d in info["director"]])
            commontable["kind"] = info["kind"]
            commontable["plot"] = info["plot"][0]
            commontable["image"] = self.get_image_blob(info["cover url"])
            commontable["genres"] = ";".join(info["genres"])
            commontable["cast"] = ";".join([str(c["long imdb canonical name"].encode("utf-8")) for c in info["cast"]])
            commontable["writers"] = ";".join([str(w["long imdb canonical name"].encode("utf-8")) for w in info["writer"]])
            commontable["runtime"] = onlynumbers(info["runtimes"][0])
            commontable["cinematographers"] = ";".join([str(c["long imdb canonical name"].encode("utf-8")) for c in info["cinematographer"]])
            commontable["musicians"] = ";".join([str(c["long imdb canonical name"].encode("utf-8")) for c in info["original music"]])
            commontable["languages"] = ";".join(info["languages"])
            commontable["producers"] = ";".join([str(p["long imdb canonical name"].encode("utf-8")) for p in info["producer"]])
            #changed to videoinfo table as table remains empty before internet sync
            #commontable["seen"] = 0
        except Exception as e:
            print "Error fetching common information : %s" % e
        try:
            imdbtable["imdb_id"] = ia.get_imdbID(info)
            imdbtable["url"] = ia.get_imdbURL(info)
            imdbtable["rating"] = info["rating"]
            imdbtable["votes"] = info["votes"]
            imdbtable["imdb_top250"] = info["top 250 rank"]
        except Exception as e:
            print "Error Fetching IMDb data %s" % e
        try:
            review = Imdb(anonymize=True,cache=True).\
            get_title_reviews("tt%s" % imdbtable["imdb_id"], max_results=1)[0].text
            imdbtable["review"] = review
        except Exception as e:
            print "Error Fetching IMDb reviews %s" % e
        if info["kind"] == "tv series":
            commontable["year_start"] = info["series years"].split("-")[0]
            commontable["year_end"] = info["series years"].split("-")[1] if len(info["series years"].split("-")) == 2 else "on"
            commontable["num_seasons"] = info["number of seasons"]
        return commontable,imdbtable

    def dump_rt(self):
        rttable = dict.fromkeys(KEYS_RTTABLE)
        rt = RT("")
        info =  rt.feeling_lucky(search_term=self.name)
        try:
            rttable["rt_id"] = info["id"]
            rttable["name"] = info["title"]
            rttable["url"] = info["links"]["alternate"]
            rttable["rating_audience"] = info["ratings"]["audience_score"]
            rttable["rating_critics"] = info["ratings"]["critics_score"]
            rttable["reviews_audience"] = info["ratings"]["audience_rating"]
            rttable["reviews_critics"] = info["ratings"]["critics_rating"]
        except Exception as e:
            print "Error Fetching from RT : %s" % e
        return rttable

    def get_image_blob(self,img_url):
        resource = urllib2.urlopen(img_url)
        img_binary = sqlite3.Binary(resource.read())
        return img_binary

def onlynumbers(name):
    """
    Find numbers inside a given name
    """
    return re.sub("[a-zA-Z:]\(\)\:","",name)

