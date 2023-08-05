from pymongo.dbref import DBRef
from pymongo.objectid import ObjectId
from pymongo.code import Code
from pymongo.errors import OperationFailure
from superdoc import SuperDoc
from doclist import SuperDocList
from exc import SuperDocError
from reg import mapped_user_class_docs
import cfma

import types

# patch DBRef to allow lazy retrieval of referenced docs
def get(self, name):

    if not hasattr(self,'_db'):
        return None
    
    col = Collection(self._db, self.collection)
    
    return getattr(SuperDoc(
        col,
        self._db[self.collection].find_one(self.id)
    ), name)

DBRef.__getattr__ = get

class Collection:
    """Represents all methods a collection can have. To create a new
    document in a collection, call new().
    """
    
    
    def __init__(self, _monga_instance, doctype, poly=False, echo=False):
        
        self._doctype = doctype
        self._monga = _monga_instance
        DBRef._db = _monga_instance._db
        self._echo = echo
        self._poly = poly
        self.__nvcol = _monga_instance._db[self._doctype._collection_name]

        
    def new(self, **datas):
        """Return empty document, with preset collection.
        """
        return self._doctype( self._monga, **datas )

    def query(self, **kwargs):
        """This method is used to first say which documents should be
        affected and later what to do with these documents. They can be
        removed or updated after they have been selected.
        
        c = Collection('test')
        c.query(name='jack').remove()
        c.query(name='jack').update(set__name='john')
        """
        
        class RemoveUpdateHandler(Collection):
            def __init__(self, _monga_instance, doctype, query):
                self._monga = _monga_instance
                self._doctype = doctype
                self.__query = query
                self.__nvcol = self._monga._db[self._doctype._collection_name]
        
            def remove(self, safe=False):
                try:
                    self.__nvcol.remove(self.__query, safe = safe)
                except:
                    return False
                return True
                
            def update(self, update, options = {}):
                
                _cond = '_id' in update and ObjectId(str(update['_id'])) or self.__query
                
                _update_param = cfma.parse_update(update)
                
                if self._echo is True:
                    print "update:", _update_param
                
                return self.__nvcol.update(
                    _cond, 
                    _update_param,
                    **options
                )
        
        if self._monga.config.get('nometaname') == False and self._poly == False:
            # hanya hapus pada record yg memiliki model yg tepat
            # untuk menjaga terjadinya penghapusan data pada beberapa model berbeda
            # dalam satu koleksi yg sama
            kwargs['_metaname_'] = self._doctype.__name__
    
        # return handler
        _query_param = cfma.parse_query2(kwargs, SuperDoc, DBRef)
        
        if self._echo is True:
            print "query:", _query_param
        
        rv = RemoveUpdateHandler( self._monga, self._doctype, _query_param)
        rv._echo = self._echo
        return rv
        
        
    def insert(self, doc):
        
        if type(doc) == self._doctype:
            doc.set_monga( self._monga )
            return doc.save()
        else:
            raise SuperDocError, "Invalid doc type %s inserted to %s collection." % (doc.__class__.__name__ ,self._doctype.__name__)
    
    
    def find(self, **kwargs):
        """Find documents based on query using the django query syntax.
        See _parse_query() for details.
        """
        
        if self._monga.config.get('nometaname') == False and self._poly == False:
            # hanya untuk record yg memiliki model yg tepat
            # untuk menjaga terjadinya pencampuran data pada beberapa model berbeda
            # dalam satu koleksi yg sama
            kwargs['_metaname_'] = self._doctype.__name__
        
        _cond = cfma.parse_query2(kwargs, SuperDoc, DBRef)
        
        if self._echo is True:
            print 'find cond:', _cond
        
        return SuperDocList(
            self._monga,
            self._doctype, 
            self.__nvcol.find( _cond ),
            polymorphic = self._poly
        )
        
    # thanks to andrew trusty
    def find_one(self, **kwargs):
        """Find one single document. Mainly this is used to retrieve
        documents by unique key.
        """

        if self._monga.config.get('nometaname') == False and self._poly == False:
            kwargs['_metaname_'] = self._doctype.__name__
        
        _cond = cfma.parse_query2(kwargs, SuperDoc, DBRef)
        docs = self.__nvcol.find_one( _cond )

        if docs is None:
            return None
        
        if self._poly == True:
            relc = mapped_user_class_docs[docs['_metaname_']]
            return relc( self._monga, **dict(map(lambda x: (str(x[0]), x[1]), docs.items())) )

        return self._doctype( self._monga, **dict(map(lambda x: (str(x[0]), x[1]), docs.items())) )
        
        
    def count(self, **kwargs):
        '''Nggo ngolehake jumlah record nang njero koleksi secara shortcut
        '''
        return self.find( **kwargs ).count()
        
    def ensure_index( self, key, ttl=600, unique=False ):
        '''nggo ngawe index nek perlu
        '''
        return self.__nvcol.ensure_index(key, ttl = ttl, unique = unique)
        
    def remove_index( self, key ):
        '''Remove index
        params:
            key: str key name
        '''
        try:
            self.__nvcol.drop_index(key)
        except OperationFailure:
            return True
        finally:
            return False
        return True
        
    def map_reduce( self, map_func, reduce_func, out_collection_name="map_reduce_result", **kwargs ):
        """Perform map reduce.
        @param map_func -- map function.
        @param reduce_func -- reduce function.
        @param out_collection_name -- output collection name for result (New in MonngoDB 1.7.4).
	@param query=dict()
        """
        map_func = Code(map_func.replace('\n',''))
        reduce_func = Code(reduce_func.replace('\n',''))
	query = kwargs.get('query', {})
        
        return self.__nvcol.map_reduce(map_func, reduce_func, out_collection_name, query=query)
        
    def inline_map_reduce( self, map_func, reduce_func, **kwargs ):
        """Perform map reduce inline. New in MongoDB 1.7.4
        @param map_func -- map function.
        @param reduce_func -- reduce function.
	@param query=dict()
        """
        
        map_func = Code(map_func.replace('\n',''))
        reduce_func = Code(reduce_func.replace('\n',''))
	query = kwargs.get('query', {})
        
        return self.__nvcol.inline_map_reduce( map_func, reduce_func, query=query )
        
    def distinct( self, key, filters ):
        """Return a list of distinct value
        for data agregation.
        for details, see:
            http://www.mongodb.org/display/DOCS/Aggregation#Aggregation-Distinct
        """
        return self.find( **filters ).distinct( key )
    
    
    def group( self, keys, filters, initial=None, reduce=None, finalize=None ):
        """Group return an array of grouped items.
        just like a SQL's GROUP.
        for details, see:
            http://www.mongodb.org/display/DOCS/Aggregation#Aggregation-Group
        """
        assert isinstance(keys, (tuple, list))
        if initial == None:
            initial = {'index':0}
        if reduce == None:
            reduce = "function(a,b){ b.index += 1; }"
        return self.__nvcol.group( keys, filters, initial, reduce, finalize=finalize )
        
        
    def clear( self ):
        '''nggo ngapus kabeh data record neng collection
        '''
        return self.__nvcol.remove({})
        
        
        
