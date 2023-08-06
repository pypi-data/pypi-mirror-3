
class BaseContent(object):
    '''
    Base content class
    '''
    raw_content_class = None
    
    def __init__(self,content):
        '''
        Constructor
        '''
        self.content = content
        self.webscraper = self.raw_content_class(self.content)
        
    def get(self,*args,**kwargs):
        raise NotImplementedError
    
    def filter(self,*args,**kwargs):
        raise NotImplementedError