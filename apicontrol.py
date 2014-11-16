import imdb
from rottentomatoes import RT
import re


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
        idtable = {}
        rttable = {}
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
        ia = imdb.IMDb()
        info = ia.search_movie(self.name,results=1)[0]
        ia.update(info)
        #Basic Info
        commontable = {
            "name" : info["long imdb canonical title"],
            "year" : info["year"],
            "directors" : ",".join([d["long imdb canonical name"] for d in info["director"]]),
            "kind" : info["kind"],
            "plot" : info["plot"][0],
            "image" : info["cover url"],
            "genres" : ",".join(info["genres"]),
            "cast" : ",".join([str(c["long imdb canonical name"].encode("utf-8")) for c in info["cast"]]),
            "writers" : ",".join([str(w["long imdb canonical name"].encode("utf-8")) for w in info["writer"]]),
            "runtime" : onlynumbers(info["runtimes"][0]),
            "cinematographers" : ",".join([str(c["long imdb canonical name"].encode("utf-8")) for c in info["cinematographer"]]),
            "musicians" : ",".join([str(c["long imdb canonical name"].encode("utf-8")) for c in info["original music"]]),
            "languages" : ",".join(info["languages"]),
            "producers" : ",".join([str(p["long imdb canonical name"].encode("utf-8")) for p in info["producer"]]),
            }
        imdbtable = {
            "imdb_id" : ia.get_imdbID(info),
            "url" : ia.get_imdbURL(info),
            "rating" : info["rating"],
            "votes" : info["votes"],
        }
        reviews = ia.get_movie_newsgroup_reviews(ia.get_imdbID(info))["data"]["newsgroup reviews"]
        reviewer_names = []
        review_urls = []
        for (name,link) in reviews:
            reviewer_names.append(name)
            review_urls.append(link)
        reviewtable = {
            "imdb_id" : ia.get_imdbID(info),
            "review_urls" : review_urls,
            "reviewers" : reviewer_names
        }
        try:
            imdbtable["imdb_top250"] = info["top 250 rank"]
        except:
            imdbtable["imdb_top250"] = None
        if info["kind"] == "tv series":
            commontable["year_start"] = info["series years"].split("-")[0]
            commontable["year_end"] = info["series years"].split("-")[1] if len(info["series years"].split("-")) == 2 else "on"
            commontable["num_seasons"] = info["number of seasons"]
        else:
            commontable["year_start"] = None
            commontable["year_end"] = None
            commontable["num_seasons"] = None
        return commontable,imdbtable,reviewtable

    def dump_rt(self):
        rt = RT("wy3s6eaj82m5ztwmsjuhnm38")
        info =  rt.feeling_lucky(search_term=self.name)
        dump = {
                "rt_id" : info["id"],
                "name" : info["title"],
                "url" : info["links"]["alternate"],
                "rating_audience" : info["ratings"]["audience_score"],
                "rating_critics" : info["ratings"]["critics_score"],
                "reviews_audience" : info["ratings"]["audience_rating"],
                "reviews_critics" : info["ratings"]["critics_rating"]
            }
        return dump

def onlynumbers(name):
    """
    Find numbers inside a given name
    """
    return re.sub("[a-zA-Z:]\(\)\:","",name)

