"""
This script returns the outoging ip
"""

import urllib2

PROVIDER =  'http://icanhazip.com'

class OutGoingIp(object):
    def __init__(self, url=None):
        """
        The provider can be updated.
        """
        if url is None:
            url = PROVIDER
        self.url = url

    def getIP(self):
        result = urllib2.urlopen(self.url)
        ip = result.read()
        if len(ip) <= 16:
            ip = ip.rstrip()
            return ip
        else:
            return "No IP Found! Please update provider."

o = OutGoingIp()
IP = o.getIP()
