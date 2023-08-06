'''
Created on Apr 18, 2012

@author: brian
'''
__all__ = ('DocAttribute','MultipleDocAttribute')

class DocAttribute(object):
    
    def __init__(self,tag,value_attr=None,return_str=None,text=None,**kwargs):
        self.tag = tag
        self.value_attr = value_attr
        self.kwargs = kwargs
        self.return_str = return_str
        self.text = text
    
    def get_value(self,content,**kwargs):
        content_find = content.get(self.tag,self.kwargs,text=self.text)
        if self.value_attr and content_find:
            return content_find.get(self.value_attr,None)
        if self.return_str and content_find:
            return content_find.string
        
        return content_find
     
    def add_content(self,content,*args,**kwargs):
        self.value = self.get_value(content)
        
class MultipleDocAttribute(DocAttribute):
    
    def __init__(self,tag,**kwargs):
        self.tag = tag
        self.kwargs = kwargs
        
    def get_multiple_value(self,content,**kwargs):
        return content.filter(self.tag,self.kwargs)
    
    def get_value(self,content,**kwargs):
        return self.get_multiple_value(content)
    