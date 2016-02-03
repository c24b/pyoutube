#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(file="./wos.log", format=FORMAT, level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
import sys
import os
import urllib
import urlparse
import requests
import re
import json
from datetime import datetime as dt
from bs4 import BeautifulSoup as bs
#from pytube import YouTube

URL = "http://www.dailymotion.com/fr/relevance/universal/search/"
RE_INT = re.compile('([0-9+])', re.UNICODE)
RE_TIME = re.compile('[0-9+]\:[0-9+]\.', re.UNICODE)

        
def create_env(name):
    #Buy default ENV is a directory composed by username
    #can be changed here
    
    directory = os.path.join(os.getcwd(), name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory
        
def encode_object(object):
  for k,v in object.items():
    if type(v) in (str, unicode):
      object[k] = v.encode('utf-8')
  return object

def get_nb(results):
    m = [n.group() for n in re.finditer(RE_INT, results)]
    return int("".join(m))

urldedepart = "/video/x291uv4_harold-a-la-carte-burkina-faso-est-ce-le-debut-d-un-printemps-africain-31-10_news"
urldarrivee = "http://www.dailymotion.com/embed/video/x291uv4"
        


class PyMotionSearch(object):
    def __init__(self, query="Harold à la carte", user="admin@cortext.fr", project="example", filter=False):
        self.URL = "http://www.dailymotion.com/"
        self.user = user
        self.project = project
        self.userdir =create_env(user)
        self.filter = filter
        self.project_dir = create_env(os.path.join(self.userdir, project))
        self.query = query
        
        date = dt.today()
        self.date = date.replace(second=0, microsecond=0)
        self.date = self.date.strftime("%d/%m%/%Y %H:%M")
        #self.search()
        #self.extract_on_channel()
        #self.log()
        self.search_videos()
        
    def search_videos(self):
        #max_page is set to 100 = 1800 result max
        max_page = 100
        pertinent = True
        self.articles = [] 
        
        for i in range(1, max_page):
            url = "http://www.dailymotion.com/fr/relevance/search/%s/%i" %(self.query.replace(" ", "+"), i)
            r =  requests.get(url)
            if r.status_code == 200:
                html = bs(r.text, "lxml")
                results = get_nb(html.find("li", {"class": "pull-start mrg-end-lg active"}).text)
                print "estimated results", results
                print "estimatedpages", results/18
                #18 per pages
                videos = html.find_all("div", {"class": "media-block"})
                for n, v in enumerate(videos):
                    href = v.find("a").get("href").split("_")
                    download_url =  "http://www.dailymotion.com/embed"+href[0]
                    filename = href[1]
                    title = v.find("a").text
                    
                    if self.query in title.encode("utf-8"):
                        print "Ok"
                        author = v.find("div", {"class": "owner"}).find("a")
                        author = {"author_url":author.get("data-user-uri"), "author_name": author.text}
                        date = v.find("div", {"class": "owner"}).find("span", {"class": "date"}).text.replace("- ", "")
                        vues = get_nb(v.find("div", {"class": "views"}).text)
                        r = requests.get(download_url, stream=True)
                        fname = os.path.join(self.project_dir, filename)+".mp4"
                        if os.path.exists(fname):
                            pass
                        else:
                            self.write(r.content, fname)
        
                    
                #print title
            
    
    def log(self):
        self.params = {"query": self.query, 
                        "date": self.date, 
                        "user": self.user, 
                        "results_nb": self.results_nb,
                        "pertinent_results": len(self.articles),
                        "videos": self.articles
        }
        
        self.write(self.params, os.path.join(self.userdir, self.project+"-log.json"))
        return self.params
        
    def write(self, data, fname):
        if not os.path.exists(fname):
            with open(fname, "w") as f:
                f.write("")
        with open(fname, "w+") as f:
            data = json.dumps(data, indent=4)
            f.write(unicode(data))
    
            
    
    def search_by_channel():
        #http://www.dailymotion.com/relevance/user/BFMTV/search/Harold/1
        pass
    
        
if __name__ == "__main__":
    PyMotionSearch(query='Blockchain bitcoin', user="admin@cortext.fr", project="BB", filter = True)

