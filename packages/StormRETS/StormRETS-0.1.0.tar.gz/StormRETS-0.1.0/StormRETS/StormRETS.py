#!/usr/bin/env python

__author__ = "Paul Trippett"
__copyright__ = "Copyright 2012, StormRETS, Inc"
__credits__ = ["Paul Trippett"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Paul Trippett"
__email__ = "paul@stormrets.com"
__status__ = "Development"

import requests

class StormRETS:
    
    SUBDOMAIN = ""
    APIKEY = ""
    ENDPOINT = ""
    FORMAT = "json"
    
    def __init__(self, sub_domain, api_key, end_point, format = "json"):
        """
        Initialize the StormRETS object with required details for connection
        """
        self.SUBDOMAIN = sub_domain
        self.APIKEY = api_key
        self.ENDPOINT = end_point
        self.FORMAT = format
    
    def search(self, options = {}):
        """
        Search a StormRETS endpoint
        """
        options.update({'apikey': self.APIKEY})
        return requests.get("http://%s.stormrets.com/%s.%s" % (self.SUBDOMAIN, self.ENDPOINT, self.FORMAT), params=options)
