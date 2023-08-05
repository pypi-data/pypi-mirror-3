
from pymongo.dbref import DBRef
from collection import Collection
from monga import MongoDB
from superdoc import SuperDoc
from orm import mapper, relation, RelationDataType, query, this
from pymongo import ASCENDING, DESCENDING
from const import allowed_data_types
from antypes import options, variant
from connector import connect
import helpers
import cfma

VERSION = "0.0.15"
COPYRIGHT = 'AnLab Software'
CONTACT = 'robin@nosql.asia'


__all__ = [
    "DBRef", "Collection", "MongoDB",
    "SuperDoc", "relation", "RelationDataType",
    "ASCENDING", "DESCENDING", "options", "connect",
    "query", "this", "variant"
]

def to_dict(self, obj):
    """Iterate over the nested object and convert it to an dict.
    """
    
    d = {}
    
    for k in dir(obj):
        # ignore values with a beginning underscore. these are private.
        if k.startswith('__') and k != '__meta_pcname__' or k in ('_Nested__hash',):
            continue

        # get value an type
        value = getattr(obj, k)
        obj_type = type(value)
        
        # process Nested objects
        if obj_type == cfma.Nested:
            d[k] = self.__to_dict(value)

        # lists, that can consist of Nested objects, 
        # Docs (references) or primitive values
        elif obj_type == list:
            d[k] = []
            for i in value:
                if type(i) == cfma.Nested:
                    d[k].append(self.__to_dict(i))

                else:
                    d[k].append(i)
                    
        # primitive values
        elif obj_type == RelationDataType:
            d[k] = str(value)
        
        else:
            if obj_type in allowed_data_types:
                d[k] = value
        
    return d

cfma.Nested.to_dict = to_dict




