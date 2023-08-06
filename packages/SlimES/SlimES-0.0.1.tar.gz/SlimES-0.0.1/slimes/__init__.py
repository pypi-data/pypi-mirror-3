#!/usr/bin/env python

import requests         #for HTTP requests
import json             #for loading JSONs in dictionaries

#######CLASSES##########
class HTTPElasticsearchException(BaseException):
    """This is for throwing exceptions when a non-2XX error code
    is returned from an HTTP request. Just raise this exception
    with whatever message you want the client to get"""

class Requester():
    def __init__(self, address=["localhost:9200"]):
        """
        address - this is where we should find Elasticsearch
        """
        self.address = address
    def _buildURL(self, address, myindex, mytype, myID, mysuffix):
        """Makes an URL out of the given parameters"""
        url = "http://%s" % address
        for argument in (str(myindex), str(mytype), str(myID)):
            if argument <> "":
                url += "/" + argument
        #suffix will not have a / before it if it starts with ?
        #this is for additional parameters like "op_type=create"
        if str(mysuffix):
            if (mysuffix).startswith("?"):
                url += str(mysuffix)
            else:
                url += "/" + str(mysuffix)
        return url
    def request(self, method="get", myindex="", mytype="",
                myID="", mysuffix="", mydata={}, jsonnize=True):
        """
        This is the meat. You need to specify a method here, otherwise
        GET is default.

        The procedure is similar to all methods:
        - an URL is built from the specified index, type, ID and suffix (none are mansdatory)
        - your dictionary of data is dumped in a JSON. Unless you specify jsonnize=False (good for bulks)
        - a request with the specified method will be done with the URL and the JSON

        If the resulting code is 2XX, it will load the received JSON
        into a dictionary and return it.

        Exceptions will be raised if something goes wrong (eg: given data can't be loaded in JSON),
        and an HTTPElasticsearchException will be raised if the status code is not 2XX. In that
        case, the exception message will be the HTTP response contents.
        """
        #encode the given dict to JSON
        if jsonnize:
            my_doc = json.dumps(mydata)
        else:
            my_doc = mydata
        #do the request based on the chosen method
        success = False
        #try all the given addresses
        for item in self.address:
            #make the URL
            myURL = self._buildURL(item,myindex,mytype,myID,mysuffix)
            try:
                result = requests.request(method=method, url=myURL, data=my_doc)
                success = True
                break
            except:
                pass
        if not success:
            #re-raise the last exception in nothing worked
            raise
        #check if the status code is what we expect
        if result.status_code<200 or result.status_code>299:
            raise HTTPElasticsearchException(result.content)
        #return a dict
        return json.loads(result.content)
