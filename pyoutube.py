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
from pytube import YouTube
URL = "https://www.youtube.com/"
RE_INT = re.compile('([0-9+])', re.UNICODE)
RE_TIME = re.compile('[0-9+]\:[0-9+]\.', re.UNICODE)

        
def create_env(name):
    #Buy default ENV is a directory composed by username
    #can be changed here
    #self.ENV = dict(self.settings["env"])

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



        


class PytubeSearch(object):
    def __init__(self, query="", user="admin@cortext.fr", project="example", filter=False):
        self.URL = "https://www.youtube.com/"
        self.user = user
        self.project = project
        self.userdir =create_env(user)
        self.filter = filter
        self.project_dir = create_env(os.path.join(self.userdir, project))
        self.query = query
        
        date = dt.today()
        self.date = date.replace(second=0, microsecond=0)
        self.date = self.date.strftime("%d/%m%/%Y %H:%M")
        self.search()
        #self.extract_on_channel()
        self.log()
        
    def search(self):
        self.articles = [] 
        for result_url in self.get_results():
            articles = self.extract(result_url)
            self.articles.extend(articles)
        return self
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
    
            
    def get_results(self):
        search_urls = []
        url = URL+"results?".encode("utf-8")
        query = {"search_query": self.query }
        #params = urllib.urlencode(encode_object(query))
        
        r = requests.get(url, query)
        if r.status_code == 200:
            html = bs(r.text, "lxml")
            results =  html.find("p", {"class":"num-results first-focus"}).text
            results_nb = get_nb(results)
            self.results_nb = results_nb
            if results_nb > 1000:
                results_nb = 1000
                logging.warning("%i Videos trouvée. Désolé, YouTube ne peut afficher plus de 1 000 résultats par requête." %results_nb)
            
            return [{"search_query":self.query, "page": page} for page in range(1, int((results_nb/20)+1))]
        else:
            logging.critical("Unable to load results: youtube is unreachable")
    def download_video(self, url):
        yt = YouTube(url)
        #~ video = yt.get('mp4')
        
        video = yt.filter('mp4')[-1]
        
        try:
            video.download(self.project_dir)
        except OSError:
            pass
        return self
    def filter_query(self, query):
        if self.filter is False:
            return True
        else:
            try:
                title_match = query["search_query"] in self.article["title"]
            except UnicodeDecodeError:
                logging.warning("Unicode Error on title")
                title_xpr = re.compile("("+query["search_query"]+")", re.U)
                title_m = re.match(title_xpr, article["title"])
                title_match = bool(title_m is not None)
            if self.article["description"] is None:
                return title_match
            else:
                try:
                    desc_match = query["search_query"] in self.article["description"]
                except UnicodeDecodeError:
                    logging.warning("Unicode Error on description")
                    title_xpr = re.compile("("+query["search_query"]+")", re.U)
                    title_m = re.match(title_xpr, article["description"])
                    desc_match = title_m is not None
                
                return any([title_match, desc_match])
        
    def extract_article(self, item, query):
        self.article = {}
        info = item.find("h3",{"class":"yt-lockup-title "})
        url = info.find("a").get("href")
        self.article["url"] = urlparse.urljoin(URL,url)
        self.article['title'] = (info.find("a").text).encode("utf-8")
        try:
            self.article["description"] = (item.find("div", {"class":"yt-lockup-description"}).text).encode("utf-8")
        except AttributeError:
            self.article["description"] = None
        
        if self.filter_query(query):
        
            desc_id = info.find("a").get("aria-describedby")
            duree = info.find("span",{"id":desc_id}).text
            #toformat
            self.article["duree"]  = duree.split(" ")[-1]
            
            desc = [n.text for n in item.find("ul", {"class":"yt-lockup-meta-info"}).find_all("li")]
            self.article['date'] = desc[0]
            try:
                self.article['vues'] = get_nb(desc[1])
            except IndexError:
                self.article['vues'] = None
            
            author = item.find("div", {"class":"yt-lockup-byline"}).find('a')
            self.article["author"] = {"url": urlparse.urljoin(URL, author.get("href")), "name": (author.text).encode("utf-8")}
            #article["file"] = os.path.join(self.project_dir, url.split("=")[0]+".txt")
            #self.write(article, article["file"])
            self.download_video(self.article["url"])
            
            self.article["downloaded"] = True
            return True
        else:
            self.article["downloaded"] = False
            return False
        
    def extract(self, query):
        self.articles = []
        url = URL+"results?".encode("utf-8")
        r = requests.get(url, query)
        if r.status_code == 200:
            html = bs(r.text, "lxml")
            
            for item in html.find_all("div", {"yt-lockup-content"}):
                self.extract_article(item, query)
                self.articles.append(self.article)
                
        return self.articles
        
    
    
        
if __name__ == "__main__":
    PytubeSearch(query='\"Harold Hyman\"', user="admin@cortext.fr", project="HH5", filter = True)

