'''
Created on May 11, 2012

@author: brian
'''
from BeautifulSoup import BeautifulSoup
from scrapr import extractor

from doc_attributes import TwitterAttribute,BlogAttribute,RSSFeedAttribute

class ProviderAnalyzer(extractor.Extractor):
    
    title = extractor.DocAttribute('title',return_str=True)
    
    description = extractor.DocAttribute('meta',value_attr='content',
                                         **{'name':'description'})
    
    twitter_url = TwitterAttribute()
    
    blog = BlogAttribute() 
    
    rss_feed = RSSFeedAttribute()
    