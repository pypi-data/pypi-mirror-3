'''
Created on May 11, 2012

@author: brian
'''
import requests

from extractors import ProviderAnalyzer

def scrape_site(url):
    req = requests.get(url)
    pa = ProviderAnalyzer(req.content,url=url)
    return dict(title=pa.title,description=pa.description,
        twitter_url=pa.twitter_url,blog=pa.blog,rss_feed=pa.rss_feed,
        )