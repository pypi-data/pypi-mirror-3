'''
Created on May 11, 2012

@author: brian
'''
from bs4 import BeautifulSoup

from base import BaseContent

class Content(BaseContent):
    raw_content_class = BeautifulSoup
    
    def filter(self,*args,**kwargs):
        return self.webscraper.find_all(*args,**kwargs)
    
    def get(self, *args, **kwargs):
        return self.webscraper.find(*args,**kwargs)