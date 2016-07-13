from dbmanager import *
from apicontrol import *
from extras import *
from joblib import Parallel,delayed
from ui import QCoreApplication

#TODO:Reviews,Image


def first_load():
    if not os.path.isfile("test.db"):
        SQLHandler().resetdb()

def add_folder(mov_dir):
    addressfiles = [os.path.join(root)      #addresses
    for root, dirs, files in os.walk(mov_dir)
        for file in files
            if file.endswith(ALLOWED_EXTENSIONS)]
    namefiles = [os.path.join(file)         #names
    for root, dirs, files in os.walk(mov_dir)
        for file in files
            if file.endswith(ALLOWED_EXTENSIONS)]
    for ind in range(len(addressfiles)):
        addressfiles[ind] = os.path.join(addressfiles[ind],namefiles[ind])
    namefiles = map(name_clean,namefiles)
    my_handle = SQLHandler()
    for i in range (len(namefiles)):
        my_handle.insert_into_videoinfo(namefiles[i],addressfiles[i],0)
    my_handle.close()

def add_file(file_path):
    mov_name = file_path[file_path.rfind("/") + 1:]
    mov_name = name_clean(mov_name)
    my_handle = SQLHandler()
    my_handle.insert_into_videoinfo(mov_name,file_path,0)
    my_handle.close()

def name_clean(name):
    replace = [".avi",".webm",".WEBM",".mkv",".MKV",".AVI","1.4","5.1","WEB-DL","-","DVDRip","BRRip","BRrip","XviD","1CDRip","aXXo","[","]","(",")","{","}","{{","}}"
    "x264","720p","StyLishSaLH (StyLish Release)","DvDScr","MP3","HDRip","WebRip",
    "ETRG","YIFY","StyLishSaLH","StyLish Release","TrippleAudio","EngHindiIndonesian",
    "385MB","CooL GuY","a2zRG","x264","Hindi","AAC","AC3","MP3"," R6","HDRip","H264","ESub","AQOS",
    "ALLiANCE","UNRATED","ExtraTorrentRG","BrRip","mkv","mpg","DiAMOND","UsaBitcom","AMIABLE",
    "BRRIP","XVID","AbSurdiTy","DVDRiP","TASTE","BluRay","HR","COCAIN","_",".","BestDivX","MAXSPEED",
    "Eng","500MB","FXG","Ac3","Feel","Subs","S4A","BDRip","FTW","Xvid","Noir","1337x","ReVoTT",
    "GlowGaze","mp4","Unrated","hdrip","ARCHiViST","TheWretched","www","torrentfive","com",
    "1080p","1080","SecretMyth","Kingdom","Release","RISES","DvDrip","ViP3R","RISES","BiDA","READNFO",
    "HELLRAZ0R","tots","BeStDivX","UsaBit","FASM","NeroZ","576p","LiMiTED","Series","ExtraTorrent","DVDRIP","~",
    "BRRiP","699MB","700MB","greenbud","B89","480p","AMX","007","DVDrip","h264","phrax","ENG","TODE","LiNE",
    "XVid","sC0rp","PTpower","OSCARS","DXVA","MXMG","3LT0N","TiTAN","4PlayHD","HQ","HDRiP","MoH","MP4","BadMeetsEvil",
    "XViD","3Li","PTpOWeR","3D","HSBS","CC","RiPS","WEBRip","R5","PSiG","'GokU61","GB","GokU61","NL","EE","Rel","NL",
    "PSEUDO","DVD","Rip","NeRoZ","EXTENDED","DVDScr","xvid","WarrLord","SCREAM","MERRY","XMAS","iMB","7o9",
    "Exclusive","171","DiDee","v2","Imdb","N@tive","BR","Dual Audio","TheAaax9","world4free","LOKY"
    ]
    year=0
    for y in range(1900,2017):
        if str(y) in name:
            year = str(y)
            yearind = name.find(year) + 4
            try:
                name = name[:yearind]
            except:
                pass
            name = name.replace(str(y)," ")
            break
    for value in replace:
        name = name.replace(value," ")
        name=name.lstrip()
        name=name.rstrip()
    if year == 0:
        return ("%s" % (name))
    else:
        return ("%s %s" % (name,year))

def get_mov_names():
    my_handle = SQLHandler()
    mov_cursor = my_handle.handle.execute('SELECT videoname FROM videoinfo ORDER BY videoname')
    mov_names = []
    for row in mov_cursor:
        mov_names.append(row[0])
    my_handle.close()
    return mov_names

def get_mov_ids():
    my_handle = SQLHandler()
    id_cursor = my_handle.handle.execute('SELECT id FROM videoinfo')
    ids = []
    for row in id_cursor:
        ids.append(row[0])
    my_handle.close()
    return ids

def mov_to_path(mov):
    id = mov_to_id(mov)
    my_handle = SQLHandler()
    cur_pathdetails = my_handle.handle.execute("SELECT address FROM videoinfo WHERE id==%d" % id)
    return cur_pathdetails.fetchone()[0]

def id_to_details(id):
    my_handle = SQLHandler()
    cur_imdbdetails = \
        my_handle.handle.execute(
            """
            select imdbtable.rating,imdbtable.votes,
            imdbtable.review
            FROM imdbtable,idstable
            WHERE idstable.imdb_id = imdbtable.imdb_id
            AND idstable.id = %d
            """ % id)
    cur_rtdetails = \
        my_handle.handle.execute(
            """
            select rttable.rating_audience
            FROM rttable,idstable
            WHERE idstable.rt_id = rttable.rt_id
            AND idstable.id = %d
            """ % id)
    imdb_details = cur_imdbdetails.fetchone()
    rt_details = cur_rtdetails.fetchone()
    return imdb_details[0],imdb_details[1],rt_details[0],imdb_details[2]

def id_to_recodetails(mov_id):
    my_handle = SQLHandler()
    movdetails_cursor = my_handle.handle.execute('SELECT * FROM commontable '
                                                 'WHERE id == %d' % mov_id)
    row = movdetails_cursor.fetchone()
    mov_dict = {}
    mov_dict["name"] = row[1]
    mov_dict["directors"] = row[3].split(";")
    mov_dict["genres"] = row[7].split(";")
    mov_dict["cast"] = row[8].split(";")
    mov_dict["writers"] = row[9].split(";")
    mov_dict["producers"] = row[14].split(";")
    return mov_dict

def prep_mov_details_dict(mov_id):
    my_handle = SQLHandler()
    movdetails_cursor = my_handle.handle.execute('SELECT * FROM commontable '
                                                 'WHERE id == %d' % mov_id)
    row = movdetails_cursor.fetchone()
    mov_dict = {}
    mov_dict["name"] = row[1]
    mov_dict["year"] = row[2]
    mov_dict["directors"] = row[3]
    mov_dict["kind"] = row[4]
    mov_dict["plot"] = row[5]
    mov_dict["img"] = row[6]
    mov_dict["genres"] = row[7]
    mov_dict["cast"] = row[8]
    mov_dict["languages"] = row[13]
    mov_dict["producers"] = row[14]
    mov_dict["imdb_rating"],mov_dict["votes"], \
    mov_dict["rt_rating"],mov_dict["review"] = id_to_details(mov_id)
    return mov_dict

def mov_to_id(mov_name):
    my_handle = SQLHandler()
    id_cursor = my_handle.handle.execute('SELECT id FROM videoinfo WHERE videoname == "%s"' % mov_name)
    return id_cursor.fetchone()[0]

def id_to_mov(id):
    my_handle = SQLHandler()
    movname_cursor = my_handle.handle.execute('SELECT videoname FROM videoinfo WHERE id == "%d"' % id)
    return movname_cursor.fetchone()[0]

def add_mov_details_to_db(mov):
    id = mov_to_id(mov)
    try:
        idstable,commtable,imdbtable,rttable = VideoHandler(mov).infodump()
        idstable["id"] = id
        commtable["id"] = id
        sqlite_handle = SQLHandler()
        try:
            sqlite_handle.insert_into_commontable(commtable)
        except Exception as e:
            print "Error inserting in CommonTable : %s" % e.message
        try:
            sqlite_handle.insert_into_idstable(idstable)
        except Exception as e:
            print "Error inserting in IdsTable : %s" % e.message
        try:
            sqlite_handle.insert_into_imdbtable(imdbtable)
        except Exception as e:
            print "Error inserting in IMDBTable : %s" % e.message
        try:
            sqlite_handle.insert_into_rt_table(rttable)
        except Exception as e:
            print "Error inserting in RottenTomato Table : %s" % e.message
        print "ID %s" % commtable["id"]
        print "Inserted %s" % commtable["name"]
    except Exception as e:
        print "Problem in Insertion %s : %s" % (mov,e.message)
###############
#New checkbox db queries
###############

def changeSeenValue(movie):
    handler = SQLHandler()
    id = mov_to_id(movie)
    #print str(id)
    try:
        handler.handle.execute('UPDATE videoinfo SET seen = NOT seen WHERE videoinfo.id = "%d"' % id)
        handler.handle.commit()
        print "value changed"
    except Exception as e:
        print e.message

def getSeenValue(movie):
    handler = SQLHandler()
    id = mov_to_id(movie)
    #print str(id)
    try:
        cursor = handler.handle.execute('SELECT seen FROM videoinfo where id = "%d"' % id)
        return cursor.fetchone()[0]
    except Exception as e:
        print e.message

def getSeenMovies():
    handler = SQLHandler()
    try:
        cursor = handler.handle.execute('SELECT idstable.id,idstable.imdb_id,commontable.name FROM idstable, commontable, videoinfo WHERE videoinfo.seen=1 and videoinfo.id = idstable.id and commontable.id = idstable.id')
        return cursor.fetchall()
    except Exception as e:
        print e.message

