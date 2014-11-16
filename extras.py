from cStringIO import StringIO
import urllib2
import wx

def url_to_wximage(url):
    wx.wxInitAllImageHandlers()
    try:
        fp = urllib2.urlopen(url)
        data = fp.read()
        fp.close()
        img = wx.wxImageFromStream(StringIO(data))
        return img
    except:
        # decide what you want to do in case of errors
        # there could be a problem getting the data
        # or the data might not be a valid jpeg, png...
        print "Error Decoding Image"
        return None

def check_net():
    try:
        urllib2.urlopen('http://www.google.com',timeout=1)
        return True
    except Exception as e:
        print e
        return False