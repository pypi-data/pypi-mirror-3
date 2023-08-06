'''
Created on Apr 18, 2012

@author: brian
'''
from doc_attributes import *
from content.bs3 import Content

def get_declared_variables(bases, attrs):
    doc_attributes = dict()
    da_update = doc_attributes.update
    attrs_pop = attrs.pop
    for variable_name, obj in attrs.items():
        if isinstance(obj, DocAttribute):
            da_update({variable_name:attrs_pop(variable_name)})
        
    for base in bases:
        if hasattr(base, 'base_variables'):
            if len(base.base_doc_attributes) > 0:
                da_update(base.base_doc_attributes)
    return doc_attributes

class DeclarativeVariablesMetaclass(type):
    """
    Partially ripped off from Django's forms.
    http://code.djangoproject.com/browser/django/trunk/django/forms/forms.py
    """
    def __new__(cls, name, bases, attrs):
        attrs['base_doc_attributes'] = get_declared_variables(bases, attrs)
        new_class = super(DeclarativeVariablesMetaclass,
            cls).__new__(cls, name, bases, attrs)

        return new_class


class BaseExtractor(object):
    """
    Base class for all Scrapr extractor classes.
    """       
    
    def __init__(self,content,*args,**kwargs):
        self.args = args
        self.kwargs = kwargs
        self.content = self.Meta.content_class(content)
        
    def __new__(cls,content,*args, **kwargs):
        extractor = cls.new(content,*args, **kwargs)
        extractor.get_response()
        return extractor
        
    @classmethod
    def new(cls,content,*args, **kwargs):
        obj = object.__new__(cls)
        obj.__init__(content,*args, **kwargs)
        return obj
    
    def get_response(self):
        self._doc_attributes = dict()
        self.load_base_doc_attributes()
    
    def load_base_doc_attributes(self):
        for key,value in self.base_doc_attributes.items():
            value.add_content(self.content,**self.kwargs)
            setattr(self, key, value.value)
    
    class Meta(object):
        content_class = Content
        
class Extractor(BaseExtractor):
    __metaclass__ = DeclarativeVariablesMetaclass 