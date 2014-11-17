import imdb
from rottentomatoes import RT
import re
from variables import KEYS_COMMONTABLE,\
    KEYS_IDSTABLE,KEYS_IMDBTABLE,\
    KEYS_REVIEWTABLE,KEYS_RTTABLE


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
        #Construct Common table, IMDb table, Review table
        commontable,imdbtable,reviewtable = self.dump_imdb()
        #Contruct IDTable
        idtable["imdb_id"] = imdbtable["imdb_id"]
        if commontable["kind"] == "movie":
            #Contruct RT table
            rttable = self.dump_rt()
            idtable["rt_id"] = rttable["rt_id"]
        return idtable,commontable,imdbtable,rttable,reviewtable

    def dump_imdb(self):
        commontable = dict.fromkeys(KEYS_COMMONTABLE)
        imdbtable = dict.fromkeys(KEYS_IMDBTABLE)
        reviewtable = dict.fromkeys(KEYS_REVIEWTABLE)
        ia = imdb.IMDb()
        info = ia.search_movie(self.name,results=1)[0]
        ia.update(info)
        #Basic Info
        try:
            commontable["name"] = info["long imdb canonical title"]
            commontable["year"] = info["year"]
            commontable["directors"] = ",".join([d["long imdb canonical name"] for d in info["director"]])
            commontable["kind"] = info["kind"]
            commontable["plot"] = info["plot"][0]
            commontable["image"] = info["cover url"]
            commontable["genres"] = ",".join(info["genres"])
            commontable["cast"] = ",".join([str(c["long imdb canonical name"].encode("utf-8")) for c in info["cast"]])
            commontable["writers"] = ",".join([str(w["long imdb canonical name"].encode("utf-8")) for w in info["writer"]])
            commontable["runtime"] = onlynumbers(info["runtimes"][0])
            commontable["cinematographers"] = ",".join([str(c["long imdb canonical name"].encode("utf-8")) for c in info["cinematographer"]])
            commontable["musicians"] = ",".join([str(c["long imdb canonical name"].encode("utf-8")) for c in info["original music"]])
            commontable["languages"] = ",".join(info["languages"])
            commontable["producers"] = ",".join([str(p["long imdb canonical name"].encode("utf-8")) for p in info["producer"]])
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
            reviews = ia.get_movie_newsgroup_reviews(ia.get_imdbID(info))["data"]["newsgroup reviews"]
            reviewer_names = []
            review_urls = []
            for (name,link) in reviews:
                reviewer_names.append(name)
                review_urls.append(link)
            reviewtable["imdb_id"] = ia.get_imdbID(info)
            reviewtable["review_urls"] = review_urls
            reviewtable["reviewers"] = reviewer_names
        except Exception as e:
            print "Error Fetching Reviews : %s" % e
        if info["kind"] == "tv series":
            commontable["year_start"] = info["series years"].split("-")[0]
            commontable["year_end"] = info["series years"].split("-")[1] if len(info["series years"].split("-")) == 2 else "on"
            commontable["num_seasons"] = info["number of seasons"]
        return commontable,imdbtable,reviewtable

    def dump_rt(self):
        rttable = dict.fromkeys(KEYS_RTTABLE)
        rt = RT("wy3s6eaj82m5ztwmsjuhnm38")
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

def onlynumbers(name):
    """
    Find numbers inside a given name
    """
    return re.sub("[a-zA-Z:]\(\)\:","",name)

