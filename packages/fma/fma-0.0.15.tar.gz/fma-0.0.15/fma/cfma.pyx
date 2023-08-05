
from pymongo import errors
from pymongo.objectid import ObjectId
from fma.reg import mapped_user_class_docs
from fma.exc import *
import types
import datetime

cdef _memoize_regs = {}

def my_dir(object self, object obj):
    cdef k
    cdef v
    
    k = "%d:%d" % (id(self), id(obj))
    
    if _memoize_regs.has_key(k):
        return _memoize_regs[k]
        
    v = dir(obj)
    
    if len(_memoize_regs) > 300:
        _memoize_regs.clear()
        
    _memoize_regs[k] = v
    return v


def dictarg(data):
    return dict(map(lambda x: (str(x[0]), x[1]), data.items()))


cdef class SuperDocList:
    cdef _items
    cdef _monga
    cdef _doctype
    cdef _polymorphic
    
    
    def __init__(self, _monga_instance, doctype, items, polymorphic=False):
        """Initialize DocList using the collection it belongs to and
        the items as iterator.
        """
        
        self._items = items
        self._monga = _monga_instance
        self._doctype = doctype
        self._polymorphic = polymorphic

        
    def skip(self, num):
        return SuperDocList( self._monga, self._doctype, self._items.skip(num), self._polymorphic )
    
    def limit(self, num):
        return SuperDocList(self._monga, self._doctype, self._items.limit(num), self._polymorphic)
        
    def sort(self, **kwargs):
        sort = [(k.replace('__', '.'), v) for k, v in kwargs.items()]
        return SuperDocList(self._monga, self._doctype, self._items.sort(sort), self._polymorphic)
        
    def tofirst(self):
        return SuperDocList(self._monga, self._doctype, self._items.rewind(), self._polymorphic)
        
    def count( self ):
        return self._items.count()
        
    def __len__(self):
        return self._items.count()
        
    def all(self):
        return [ x for x in self ]
    
    def distinct(self, key):
        return self._items.distinct(key)
        
    def first( self ):
        rv = SuperDocList( self._monga, self._doctype, self._items.rewind(), self._polymorphic )
        if rv.count() > 0:
            return rv.next()
        return None
        
    def __iter__(self):
        return self
        
    def __next__(self):
        try:
            rv = self._items.next()
        except errors.OperationFailure, e:
            print "An error occured when iterating. e: %s" % e
            raise StopIteration
        if rv and self._polymorphic:
            relc = mapped_user_class_docs[rv['_metaname_']]
            return relc( self._monga, **dictarg(rv) )
        return self._doctype( self._monga,  **dictarg(rv) )
        
    def copy(self):
        return copy.copy( self )


def get_siblings(rel_class):
    global mapped_user_class_docs
    cdef list siblings = [rel_class.__name__]
    cdef k
    cdef sb
    for k, sb in mapped_user_class_docs.iteritems():
        parent = sb.__bases__[0]
        while(True):
            if parent.__name__ == "SuperDoc": break
            if parent.__name__ == rel_class.__name__:
                siblings.append( sb.__name__ )
                break
            parent = parent.__bases__[0]
    return siblings


def get_condition_where(cond, parent_class):
    def mapper_(tuple x):
        if type(x[1]) not in (str, unicode):
            return x
        if not x[1][0] == ':':
            return x
        return (x[1], hasattr(parent_class.__dict__['_data'],
                              x[1][0] == ':' and x[1][1:] or x[1])
                and getattr(parent_class.__dict__['_data'], x[1][0] == ':' and x[1][1:] or x[1]) or None )
    return cond.where( **dict(map( mapper_, cond.raw.iteritems() )))


def parse_query(dict kwargs):
    cdef k
    cdef v
    cdef q = {}
    cdef str key

    # iterate over kwargs and build query dict
    for k, v in kwargs.items():
        # handle query operators
        op = k.split('__')[-1]
        if op in ('lte', 'gte', 'lt', 'gt', 'ne',
            'in', 'nin', 'all', 'size', 'exists'):

            k = k[:k.find('__' + op)]

            if op in ('in','nin'):
                v = {'$%s' % op: k == '_id' and map(lambda x: ObjectId(str(x)), v) or v }
            else:
                v = {'$%s' % op: k == '_id' and ObjectId(str(v)) or v }

        else:
            
            if k == "or__":
                
                ## $or is new in MongoDB 1.5.3
                rv = []
                for x in v:
                    rv.push(parse_query(x))
                
                q['$or'] = rv
                print q
                continue

            elif k == '_id':
                if type(v) != ObjectId and v[0] != ":":
                    v = ObjectId(str(v)) or v
            else:
                v = type(v) == ObjectId and str(v) or v

        #v = k == '_id' and  type(v) in (unicode,str) and ObjectId(str(v)) or v
        v = type(v) == list and str(v) or v

        # convert django style notation into dot notation
        key = k.replace('__', '.')

        if key[0] == '.':
            key = "__%s" % key[1:]

        if key.endswith('.'):
            key = "%s__" % key[:-1]

        q[key] = v
    return q


def parse_query2(kwargs, SuperDoc, DBRef):

    q = {}
    # iterate over kwargs and build query dict
    for k, v in kwargs.items():
        
        # handle query operators
        op = k.split('__')[-1]
        if op in ('lte', 'gte', 'lt', 'gt', 'ne',
            'in', 'nin', 'all', 'size', 'exists'):
            
            k = k[:k.find('__' + op)]
            
            if op in ('in','nin'):
                v = {'$%s' % op: k == '_id' and map(lambda x: ObjectId(str(x)), v) or v }
            else:
                v = {'$%s' % op: k == '_id' and ObjectId(str(v)) or v }
        
        if k == "or__":
            
            ## $or is new in MongoDB 1.5.3
            rv = []
            for x in v:
                rv.append(parse_query(x))
            
            q['$or'] = rv
            #print q
            continue
        
        elif k == '_id':
            v = type(v) in (unicode,str) and ObjectId(str(v)) or v
        else:
            v = type(v) is ObjectId and str(v) or v
            
        #v = k == '_id' and  type(v) in (unicode,str) and ObjectId(str(v)) or v
        v = type(v) == list and str(v) or v

        # convert django style notation into dot notation
        key = k.replace('__', '.')
        
        # convert mongodbobject SuperDoc type to pymongo DBRef type.
        # it's necessary for pymongo search working correctly
        if type(v) == SuperDoc:
            v = DBRef(v._collection,v._id)
            
        
        q[key] = v
    return q


def apply_condition_query(where_value,**patch):
        
        cdef rv, k, v
        
        rv = where_value
        
        for k, v in patch.iteritems():
        
                if v is not None:
                    if type(rv) == str:
                        
                        rv = rv.replace( k, type(v) in [int,long] and str(v) or type(v) == ObjectId and str(repr(v.binary.encode('hex'))) or str(repr( type(v)==unicode and str(v) or v)))
                        
                    elif type(rv) == dict:
                        
                        def find_replace( dict_data, key, replacement ):
                            # recursively value replacement
                            for k, v in dict_data.iteritems():
                                if type(v) == dict:
                                    find_replace( v, key, replacement )
                                elif type(v) == str:
                                    if v == key:
                                        if k == '_id':
                                            return ObjectId(str(replacement))
                                        dict_data[k] = type(replacement) == ObjectId and unicode(replacement) or replacement
                                        
                            return dict_data
                        
                        rv = find_replace( rv, k, v )
                        if type( rv ) == ObjectId:
                            return rv
                        
                else:
                    return None
        
        return rv


def sanitize_superdoc(object self, object relation, object options, object variant):
    
        cdef str x
        cdef str y
        cdef object v
        cdef list _attrs
    
        # map class atribute based user definition to _data container collection
        _attrs = filter( lambda x: type(getattr(self.__class__,x)) in (types.TypeType, options, variant) and x not in ('__class__',), dir(self.__class__) )

        for x in _attrs:
        
            y = x
            if type(getattr(self,x)) != relation:
                
                if not x[:3] == '_x_':
                    
                    v = getattr(self.__class__, x)
                    setattr(self.__class__, '_x_%s' % x, v )
                    
                    try:
                        delattr(self.__class__, x)
                    except AttributeError:
                        # kalo error coba deh hapus dari super-class-nya kalo ada tapi...
                        for cl in self.__class__.__mro__[1:-2]:
                            
                            # pasang attribut di tiap class yang diturunkan
                            if hasattr(cl,x):
                                setattr(cl, '_x_%s' % x, v)
                            
                            try:
                                delattr(cl, x)
                            except:
                                pass
                else:
        
                    y = x[3:]
            
            if getattr( self.__dict__['_data'], y ) is None:
                # re-set it with None again!
                setattr( self.__dict__['_data'], y, None )
                
        self.__class__._sanitized__ = True


def superdoc_map_relation(self, relation, ONE_TO_ONE, MANY_TO_ONE):
        cdef x
        cdef rel
        cdef rv
        for x in filter( lambda x: type( getattr(self.__class__,x) ) == relation , my_dir(self, self.__class__) ):
            
            rel = getattr( self, x )
            if rel is not None and rel._type != MANY_TO_ONE:
                rv = rel.reload()
                if rel._type == ONE_TO_ONE:
                    if type(rv) == types.NoneType:
                        setattr ( self, x, None ) # null it
        
            else:
                # reload relation
                rel = getattr( self.__class__, x ).copy()
                rel._parent_class = self
                
                if rel._type != MANY_TO_ONE:
                    rv = rel.reload()
                    if rv is not None:
                        setattr( self, x, rel )
                    else:
                        setattr( self, x, None ) # null it


def parse_update(kwargs):
     
    cdef dict q = {}
    cdef dict op_list = {}
    cdef k, v
    cdef str op
     
    # iterate over kwargs
    for k, v in kwargs.items():
     
        # get modification operator
        op = k.split('__')[0]
        if op in ('inc', 'set', 'push', 'pushall', 'pull', 'pullall'):
            # pay attention to case sensitivity
            op = op.replace('pushall', 'pushAll')
            op = op.replace('pullall', 'pullAll')
            
            # remove operator from key
            k = k.replace(op + '__', '')
            
            # append values to operator list (group operators)
            if not op_list.has_key(op):
                op_list[op] = []
        
            op_list[op].append((k, v))
        # simple value assignment
        else:
            q[k] = v

    # append operator dict to mongo update dict
    for k, v in op_list.items():
        et = {}
        for i in v:
            et[i[0]] = i[1]
             
        q['$' + k] = et
     
    return q


def parse_option(self, kwargs):
    
    cdef k, v
    cdef dict q = {}

    for k, v in kwargs.items():
    
        op = k.split("__")[-1]
        if op in ('upsert',):
            k = "$%s" % op
            q[k] = v
            
    return q


def to_dict(self, obj, allowed_data_types, RelationDataType, DBRef, relation, SuperDoc):
    """Iterate over the nested object and convert it to a dict.
    """
    cdef dict d = {}
    cdef str k
    cdef value
    cdef obj_type
    
    for k in dir(obj):
        # ignore values with a beginning underscore. these are private.
        if k[:2] == '__' and k != '__meta_pcname__':
            continue

        # get value an type
        value = getattr(obj, k)
        obj_type = type(value)
        
        # process Nested objects
        if obj_type == Nested:
            d[k] = to_dict(self, value, allowed_data_types, RelationDataType, DBRef, relation, SuperDoc)
            
        # items
        elif obj_type == SuperDoc:
            d[k] = DBRef( value._collection, value._id )
            
        # lists, that can consist of Nested objects, 
        # Docs (references) or primitive values
        elif obj_type == list:
            d[k] = []
            for i in value:
                if type(i) == Nested:
                    d[k].append(self.__to_dict(i))
                elif type(i) == SuperDoc:
                    if getattr(i,'_id') is None:
                        # may unsaved object?? try to save it first
                        i.save()
                    
                    d[k].append(DBRef( i._collection, i._id ))
                else:
                    d[k].append(i)
        
        # primitive values
        elif obj_type == RelationDataType:
            continue
        
        elif obj_type == types.NoneType:
            # lookup from the bases
            for bc in self.__class__.__bases__:
                try:
                    bcv = getattr(bc, k)
                    if type(bcv) == relation:
                        break
                except:
                    pass
        
        else:
            if obj_type in allowed_data_types:
                if k == "_id" and not isinstance(value, ObjectId):
                    d[k] = ObjectId(value)
                elif hasattr(value, '__class__') and \
                hasattr(value.__class__, '__name__') and \
                value.__class__.__name__ == "date":
                    
                    d[k] = datetime.datetime.combine(value, datetime.time())
                else:
                    d[k] = value
        
    return d


class Nested(object):
    
    def __init__(self, d={}):
        """Convert dict to class attributes.
        """
        cdef a, b
        for a, b in d.items():
            # handle lists and tuples
            if isinstance(b, (list, tuple)):
                setattr(self, a, 
                    [Nested(x) if isinstance(x, dict) else x for x in b])
            # the rest
            else:
                setattr(self, a, Nested(b) if isinstance(b, dict) else b)
                
        self.__my__dir = None
                
    def __getitem__(self, k):
        return getattr(self, k)
        
    def __getattr__(self, k):
        cdef rv = None
        try:
            rv = object.__getattribute__(self, k)
        except:
            pass
        return rv
    
    def _my_dir(self):
        if self.__my__dir == None:
            self.__my__dir = dir(self)
        return self.__my__dir
    
    def _hasattr(self, k):
        cdef object rv
        rv = k[:2] != '__' and k in self._my_dir()
        if rv == False:
            rv = self.__getattr__(k)
            if rv != None:
                return True
        return rv
        
    def __getstate__(self):
        return self.to_dict(self)


cdef class this(object):
    cdef str at
    
    def __init__(self,at):
        self.at = at
        
    def __repr__(self):
        return str(self.at)


cdef class query(object):
    cdef _rel_class_name
    cdef rel_class
    cdef _filter
    cdef order
    cdef _parent_class
    cdef _poly
    
    def __init__(self,str rel_class_name,filter_={},poly=False,dict order={'_id':1}):
        self._rel_class_name = rel_class_name
        self.rel_class = None
        self._filter = filter_
        self.order = order
        self._parent_class = None
        self._poly = poly
        
    def _get_rel_class(self):
        global mapped_user_class_docs
        if self.rel_class == None:
            try:
                self.rel_class = type(self._rel_class_name) == str and mapped_user_class_docs[self._rel_class_name] or self._rel_class_name
            except KeyError:
                raise RelationError, "Resource class `%s` not mapped. try to mapper first." % self._rel_class_name
        return self.rel_class
    
    def _set_parent_class(self, parent_class):
        self._parent_class = parent_class
        
    def _get_parent_class(self):
        return self._parent_class
    
    def _get_cond(self):
        
        _cond = {}
        
        for k, v in self._filter.iteritems():
            if type(v) == this:
                at = getattr(self._parent_class,str(v))
                if at != None:
                    _cond[k] = type(at) == ObjectId and unicode(at) or at
            else:
                _cond[k] = v
        
        if self._get_parent_class()._monga.config.get('nometaname') == False and self._poly == False:
            _cond["_metaname_"] = self._rel_class_name
        
        rv = parse_query(_cond)
    
        return rv
        
    def __call__(self):

        _cond = self._get_cond()
        rel_class = self._get_rel_class()
        
        return SuperDocList (
            self._parent_class._monga,
            rel_class,
            self._parent_class._monga._db[rel_class._collection_name].find( _cond )
        ).sort(**self.order)
        
        
    def find(self, **cond):
        _cond = self._get_cond()
        _cond.update(cond)
        
        rel_class = self._get_rel_class()
        return self._parent_class._monga.col(rel_class).find_one( **cond )
        
        
    def filter(self,**cond):
        _cond = self._get_cond()
        _cond.update(cond)
        
        rel_class = self._get_rel_class()
        return self._parent_class._monga.col(rel_class, poly=self._poly).find( **_cond ).sort(**self.order)
        
        
    def __iter__(self):
        
        _cond = self._get_cond()
        rel_class = self._get_rel_class()

        return SuperDocList (
                self._parent_class._monga,
                rel_class,
                self._parent_class._monga._db[rel_class._collection_name].find( _cond )
        ).sort(**self.order).__iter__()
        
        
    def copy(self):
        return query(self._rel_class_name, filter_=self._filter, poly=self._poly, order=self.order)
        
    def __getattr__(self,key):
        
        if key in ("filter","find","copy"):
            return object.__getattr__(self,key)
        
        _cond = self._get_cond()
        rel_class = self._get_rel_class()
        
        sdl = SuperDocList (
                self._parent_class._monga,
                rel_class,
                self._parent_class._monga._db[rel_class._collection_name].find( _cond )
        ).sort(**self.order)
        return getattr(sdl,key)
        
    def __repr__(self):
        return "<Dynamic Query Load [%s]>" % self._rel_class_name



def superdoc_assign_attirbutes(self, datas, options):
    cdef k, v, ov
    
    for k, v in datas.iteritems():
        
        # except bad options types
        try:
            ov = getattr(self.__class__, k)
        except:
            ov = None
            
        if ov and type(ov) is options:
            if v not in ov:
                raise SuperDocError, "`%s` cannot assign entryname for `%s = %s` invalid options, can only: `%s`" % (
                    self.__class__.__name__,
                    k,
                    v,
                    str(', '.join([str(x) for x in ov]))
                )
        
        self.__setattr__( k, v )
        


def superdoc_internal_load(self, _monga_instance, relation, options, variant, ONE_TO_ONE, MANY_TO_MANY, RawType, **datas):
    
    cdef i, cl, _opt, o, ot, x, _t, sx
    
    self._monga = _monga_instance
    
    self.__dict__['_data'] = Nested(datas)
    
    if hasattr( self, '_opt' ):
        if self._opt.get('strict') == True:
            for k in datas.keys():
                if not self._has_entryname(k):
                    raise SuperDocError, "`%s` is strict model. Cannot assign entryname for `%s`" % ( self.__class__.__name__,k )

    
    sanitize_superdoc(self, relation, options, variant)
    superdoc_assign_attirbutes(self, datas, options)
    
    if hasattr( self, '_opt' ):
        
        cls_bases = self.__class__.__mro__[:-2]
    
        # from dbgp.client import brk; brk()
        
        # invokes multiple inheritance _opt
        
        for i,cl in enumerate(cls_bases):
            if i > 0 and not hasattr(cl, "_opt"):
                continue
            if i > 0:
                _opt = getattr(cl,"_opt")
            else:
                _opt = getattr(self,"_opt")
            
            if not self._saved() and _opt.has_key('default'):
                for k, v in _opt['default'].iteritems():
                    if self._has_entryname(k):
                        if getattr(self.__dict__['_data'], k) is None:
                            if type( v ) in [types.FunctionType, types.BuiltinFunctionType]:
                                setattr( self.__dict__['_data'], k, apply( v ) )
                            else:
                                setattr( self.__dict__['_data'], k, v )
                    else:
                        raise SuperDocError, \
                            '`%s` has no entryname `%s` for default value assignment' \
                            % (self.__class__.__name__,k)


    def _filter(y):
        cdef o
        
        if y[:2] == '__':
            return False
        
        o = getattr( self.__class__, y )
        ot = type( o )
        if ot == property or ot not in (relation, query, variant, types.TypeType, dict):
            return False
        if getattr( self, y ) == None:
            return False
        return True
        
    for x in filter( _filter, dir(self.__class__)):
        
        o = getattr( self.__class__, x )
        ot = type( o )
        
        if ot == relation:
        
            _t = getattr(self,x)
            
            if type(_t) == types.NoneType:
                continue
            
            if _t._type == ONE_TO_ONE and self._monga is not None:
                
                # lookup for existance relation in db
                # if not exists, then None it!
                rv = None
                try:
                    rv = getattr(self,_t._pk[1])
                except:
                    pass
                
                if rv is not None:
                    rv = _t._pk[0] == '_id' and ObjectId(str(rv)) or type(rv) is ObjectId and str(rv) or rv
                    rv = self._monga._db[_t._get_rel_class()._collection_name].find({_t._pk[0]: rv}).count()
                    
                if rv is None or rv == 0:
                    setattr( self, x, RawType(None) )
                    setattr( self.__dict__['_data'], x, None )
                    continue
            
            _t = _t.copy()
            _t._parent_class = self
            
            setattr(self,x,_t)
            
            if _t._type == MANY_TO_MANY:
                if not self._hasattr( _t._keyrel[0] ):
                    setattr( self, _t._keyrel[0], [] ) # reset m2m relation meta list
        
        elif ot == query:
            
            _t = getattr(self,x)
            
            if type(_t) == types.NoneType:
                continue
            
            _t = _t.copy()
            _t._set_parent_class(self)
            
            setattr(self,x,_t)
        
        elif ot == variant:
            
            sx = x[:3] == '_x_' and x[3:] or x
            setattr( self, x, datas[sx] )
        
        elif ot == types.TypeType:
            
            # khusus buat inisialisasi empty list, default is []
            sx = x[:3] == '_x_' and x[3:] or x
            
            try:
                sot = type( getattr( self, sx ) )
            except AttributeError:
                continue
            
            if o == list and sot != list:
                setattr( self.__dict__['_data'], sx, [] )
                
            elif o == dict and sot != Nested:
                setattr( self.__dict__['_data'], sx, Nested() )
                

    self.__dict__['_modified_childs'] = []

