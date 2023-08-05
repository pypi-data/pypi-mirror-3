from urllib2 import urlopen
from urllib  import quote as urlquote

from Globals import DevelopmentMode
#from OFS.ObjectManager import BadRequestException

from quintagroup.plonegooglesitemaps import config


def ping_google(url, sitemap_id):
    """Ping sitemap to Google"""

    resurl = url + "/" + sitemap_id

    if DevelopmentMode or config.testing:
        #prevent pinging in debug or testing mode
        print "Pinged %s sitemap to Google" % resurl
        return 0

    sitemap_url = urlquote(resurl)

    g = urlopen('http://www.google.com/webmasters/tools/ping?sitemap=' + \
                sitemap_url)
    g.read()
    g.close()

    return 0
