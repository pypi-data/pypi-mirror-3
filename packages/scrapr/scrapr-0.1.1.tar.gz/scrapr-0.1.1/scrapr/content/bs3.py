'''
Created on May 11, 2012

@author: brian
'''
from BeautifulSoup import BeautifulSoup

from base import BaseContent

class Content(BaseContent):
    raw_content_class = BeautifulSoup
    
    def filter(self,*args,**kwargs):
        return self.webscraper.findAll(*args,**kwargs)
    
    def get(self, *args, **kwargs):
        return self.webscraper.find(*args,**kwargs)