'''
Created on May 11, 2012

@author: brian
'''
import requests,re
from scrapr.content.bs3 import Content

from scrapr import extractor


class CustomAttribute(extractor.DocAttribute):
    def __init__(self):
        pass
    
    def convert_relative_url(self,url,rel_url):
        if rel_url and rel_url.startswith('/'):
            return '{0}/{1}'.format(url,rel_url[1:])
        return rel_url
    
    def add_content(self,content,**kwargs):
        url = kwargs.get('url',None)
        self.value = self.get_value(content,url)
        
    def visit_blog_page(self,content,url):
        blog = BlogAttribute()
        blog.add_content(content,url=url)
        if blog.value:
            content = Content(requests.get(blog.value).content)
            target_value = self.get_regex_values(content)
            if target_value:
                return target_value.get('href')
        return None
    
    def get_regex_values(self,content):
        for i in self.regexes:
            content_find = content.get('a',href=i)
            if content_find:
                return content_find
                
class TwitterAttribute(CustomAttribute):
    
    regexes = (
        re.compile(r'http://twitter.com/(?P<slug>[-\w]+)$'),
        re.compile(r'http://www.twitter.com/(?P<slug>[-\w]+)$'),
        re.compile(r'http://twitter.com/#!/(?P<slug>[-\w]+)$'),
        re.compile(r'http://www.twitter.com/#!/(?P<slug>[-\w]+)$'),
        re.compile(r'http://twitter.com/(?P<slug>[-\w]+)/$'),
        re.compile(r'http://www.twitter.com/(?P<slug>[-\w]+)/$'),
        re.compile(r'http://twitter.com/#!/(?P<slug>[-\w]+)/$'),
        re.compile(r'http://www.twitter.com/#!/(?P<slug>[-\w]+)/$'),
               )
    
    def get_value(self, content,url):
        twitter = content.get('a',{'class':'twitter-follow-button'})
        if twitter:
            return twitter.get('href')
        twitter = self.get_regex_values(content)
        if twitter:
            return twitter.get('href')
        return self.visit_blog_page(content, url)
    
def find_blog_a(tag):
    regex = re.compile('blog|Blog')
    content = tag.text or ''
    if regex.search(content) and tag.name == 'a':
        return True
    
class BlogAttribute(CustomAttribute):
    
    def get_value(self, content,url):
        blog_url = content.get(find_blog_a)
        if blog_url:
            return self.convert_relative_url(url, blog_url.get('href'))
        blog_url = content.get('a',href=re.compile('blog'))
        if blog_url:
            return self.convert_relative_url(url, blog_url.get('href'))
        return self.convert_relative_url(url, blog_url)
    
class RSSFeedAttribute(CustomAttribute):

    regexes = (
        re.compile(r'http://feeds.feedburner.com/(?P<slug>[-\w]+)$'),
        re.compile(r'http://feeds.feedburner.com/(?P<slug>[-\w]+)/$'),
               )        
    
    def get_rss_xml(self,content):
        return content.get('link',type=re.compile('rss'))
    
    def get_regex_values(self, content):
        target_value = CustomAttribute.get_regex_values(self, content)
        if target_value:
            return target_value
        target_value = self.get_rss_xml(content)
        if target_value:
            return target_value
        
    def get_value(self,content,url):
        rss_feed = self.get_regex_values(content)
        if rss_feed:
            return self.convert_relative_url(url, rss_feed.get('href'))
        rss_feed = self.get_rss_xml(content)
        if rss_feed:
            return self.convert_relative_url(url,rss_feed.get('href'))
        rss_feed = self.visit_blog_page(content,url)
        return self.convert_relative_url(url, rss_feed)