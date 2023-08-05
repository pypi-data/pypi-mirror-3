#@TODO: finish this code
#from doc import Doc
from pymongo.dbref import DBRef
from pymongo.objectid import ObjectId
from antypes import *
from exc import *
from orm import *
from const import *
from pendingop import PendingOperation
import cfma
import connector
import types


class SuperDoc(object):
    '''Advanced document for mongo ORM data model
    '''
    
    def __init__(self, _monga_instance=None, **datas):
        
        # build reserved entry name
        self.__dict__['_reserved_entry_name'] = []
        
        rel_names = filter( lambda x: x[:2] != "__" and x[:9] != '_SuperDoc' and type( getattr(self.__class__, x) ) == relation, dir(self.__class__) )

        x = self.__dict__['_reserved_entry_name'].append
        for reln in rel_names:
            rel = getattr( self, reln )
            if rel._type == MANY_TO_MANY:
                x(rel._keyrel[0])
            else:
                x(reln)
        
        self._pending_ops = PendingOperation(self)
        
        if _monga_instance:
            if isinstance(_monga_instance, SuperDoc):
                pass
            else:
                _monga_instance = _monga_instance
        else:
            _monga_instance = connector.db_instance
        
        cfma.superdoc_internal_load( self, _monga_instance, relation, options, variant, ONE_TO_ONE, MANY_TO_MANY, RawType, **datas )
        self._echo = False
        self._current_datas = datas
        
        
    def copy(self):
        doc = self.__class__(self._monga, **self._current_datas)
        doc.__dict__['_data']._id = None
        return doc
        
        
    def set_monga(self, _monga):
        self._monga = _monga
            
    def validate(self):
        
        if not hasattr( self, '_opt' ):
            return 'not checked'
        
        req = self._opt.get('req')
        if req is not None:
            for x in req:
                
                if getattr( self, x ):
                    if getattr(self,x) is None:
                        raise SuperDocError, "%s require value for %s" % (self.__class__.__name__,x)
                else:
                    raise SuperDocError, "%s has no required value for %s" % (self.__class__.__name__,x)

        return 'OK'

    def save(self):
        '''Save/insert doc
        @TODO: buat acknowledge biar tau save/insert-nya berhasil atau gak?
        '''

        self.validate()
        
        if self._monga is None:
            raise SuperDocError, "This res not binded to monga object. Try to bind it first use set_monga(<monga instance>)"
        
        if self._monga.config.get('nometaname') == False:
            # buat metaname untuk modelnya
            
            setattr( self.__dict__['_data'], '_metaname_', self.__class__.__name__ )
        
        # reset dulu error tracknya, buat jaga kalo2 dibutuhkan buat error checking
        self._monga._db.reset_error_history()

        self.__dict__['_data']._id = self._monga._db[self._collection_name].save(self.to_dict())
        self.__dict__['_data']._id is not None and True or False
        
        if self.get_last_error() is not None:
            print "Cannot save document into database!"
            print "last_error: %s" % self.get_last_error()
            return None
        
        self._id = self.__dict__['_data']._id
        
        global RELATION_RECURSION_DEEP, MAX_RECURSION_DEEP
        
        RELATION_RECURSION_DEEP += 1
        
        if RELATION_RECURSION_DEEP < MAX_RECURSION_DEEP:
            
            self._call_relation_attr( '_save' )
            self._call_relation_attr( '_update_hash' )
            
            RELATION_RECURSION_DEEP -= 1
        else:
            raise SuperDocError, "Recursion limit reached, max %d" % MAX_RECURSION_DEEP
        
        # eksekusi pending ops
        if not self._pending_ops.empty():
            self._pending_ops.apply_op_all()
        
        # refresh relation state
        #self.__map_relation()
        cfma.superdoc_map_relation(self, relation, ONE_TO_ONE, MANY_TO_ONE)
        
        return self
        
    
    def get_last_error(self):
        '''Kanggo ngolehake informasi errore.
        nek raono error yo None lah return-ne.
        '''
        return self._monga._db.previous_error()

    def _call_relation_attr(self, attr, *args, **kwargs):
        
        def _filter(x):
            if type(getattr(self.__class__,x)) != relation: return False
            t = getattr( self, x )
            if t == None: return False
            # jangan save many-to-one relation
            if t._type == MANY_TO_ONE: return False
            return True
        
        for x in filter( _filter, cfma.my_dir(self, self.__class__) ):
            t = getattr( self, x )
            if hasattr(t, attr):
                getattr(t, attr)( *args, **kwargs )
                
                
    def refresh(self):
        '''Reload data from database, for keep data up-to-date
        '''
        
        if self._id == None:
            raise SuperDocError, "Cannot refresh data from db, may unsaved document?"
        
        doc = self._monga._db[self._collection_name].find_one(self._id)
        
        if not doc:
            return False
        
        cfma.superdoc_internal_load( self, self._monga, relation, options, variant, ONE_TO_ONE, MANY_TO_MANY, RawType, **dictarg(doc) )
        cfma.superdoc_map_relation(self, relation, ONE_TO_ONE, MANY_TO_ONE)
        #self.__map_relation()
        
        return True

    
    def __cmp__(self, other):
        if other is None:
            return -1
        
        if self.__dict__['_data']._id is None:
            return -1
        
        # lazy load bug fix in iteration comparison
        if other.__dict__["_data"] == None or other.__dict__["_data"]._id != None:
            other.refresh()
        
        if other.__dict__['_data']._id is None:
            return -1
        
        return cmp( self._id, other._id)
        
    
    def __hash__(self):
        return hash(unicode(self.__dict__['_data']._id))

    def __getitem__(self, k):
        return getattr(self.__dict__['_data'], k)
        
    
    def __getattr__(self, k):
        
        if k in ('_opt','__methods__', '_hasattr'):
            if getattr(self.__dict__['_data'], k) is not None:
                
                obj = getattr(self.__dict__['_data'], k)
                
                if type( obj ) == RelationDataType:
                    return object.__getattribute__(self, k)
        
                return obj
            
        v = getattr(self.__dict__['_data'], k)
        
        if v != None:
            
            if ( type( v ) == relation ):
                return getattr( v, k )
        
        #print "type(__dict__['_data']): %s" % type(self.__dict__['_data'])
        
        if k[:2] != '__' and self.__dict__['_data']._hasattr(k): # k in cfma.my_dir(self, self.__dict__['_data']):
            return v
            
        
        if getattr(self.__dict__['_data'], k) is not None:
            
            obj = getattr(self.__dict__['_data'], k)
            
            if type( obj ) == RelationDataType:
                return object.__getattribute__(self, k)
    
            return obj
        
        return object.__getattribute__(self, k)
    
    
    def _has_entryname(self, name):
        if name in superdoc_reserved_words: return True
        
        # periksa apakah meta name, terutama pada relation many-to-many
        # kembalikan True apabila berupa meta name khusus
        if name in self.__dict__['_reserved_entry_name']: return True
        
        return (hasattr(self.__class__, name) and \
                type(getattr(self.__class__, name)) in [relation, types.TypeType, options]) or \
                hasattr(self.__class__, '_x_%s' % name)
        
        
    def __setattr__(self, k, v):

        # check is keyname not in restrict_attribute_names
        if k in restrict_attribute_names:
            raise SuperDocError, "`%s` have restricted keyword `%s`. Please put another name." % (self.__class__.__name__,k)
        
        if k in superdoc_reserved_words or k[:3] == '_x_':
            if k in superdoc_reserved_words:
                return object.__setattr__(self, k, v)
            
            obj_type = type(v)
            
            if obj_type == dict:
                setattr(self.__dict__['_data'], k, cfma.Nested(v))
                
            elif obj_type == relation:
                object.__setattr__(self, k, v)
                value = RelationDataType(v)
                setattr(self.__dict__['_data'], k, v)
                
            else:
                global allowed_data_types
                
                if obj_type in allowed_data_types:
                    setattr(self.__dict__['_data'], k, v)
                    
                elif obj_type == RawType:
                    object.__setattr__(self, k, v.val)
                    
                else:    
                    object.__setattr__(self, k, v)
            return
        
        if self.__dict__.has_key('_opt') and self._opt.get('strict') == True:
            if self._has_entryname( k ) == False:
                raise SuperDocError, "`%s` is strict model. Cannot assign entryname for `%s`" % ( self.__class__.__name__,k )
        
        if hasattr( self.__class__, '_x_%s' % k ):
            typedata = getattr( self.__class__, '_x_%s' % k )
            vt = type(v)
            if typedata != vt and vt is not types.NoneType:
                
                if typedata is bool and v not in (1,0):
                    raise SuperDocError, "mismatch data type `%s`=%s and `%s`=%s" % (k,typedata,v,type(v))
                
                if isinstance(v, datetime.date):
                    # convert it back to date
                    v = datetime.datetime.combine(v, datetime.time())
                    
                else:
                    if type(typedata) != variant:
                        # try to convert it if possible
                        try:
                            v = typedata(v)
                        except:
                            raise SuperDocError, "mismatch data type `%s`=%s and `%s`=%s" % (k,typedata,v,type(v))
                        
            
        # check if one-to-one relation
        # just map it to pk==fk
        if hasattr(self.__class__,k) and type( getattr(self.__class__,k) ) == relation and isinstance(v,(SuperDoc,relation)):
            
            if type(v) == relation:
                if k in superdoc_reserved_words:
                    return object.__setattr__(self, k, v)
                
                obj_type = type(v)
                
                if obj_type == dict:
                    setattr(self.__dict__['_data'], k, cfma.Nested(v))
                    
                elif obj_type == relation:
                    object.__setattr__(self, k, v)
                    value = RelationDataType(v)
                    setattr(self.__dict__['_data'], k, v)
                    
                else:
                    
                    if obj_type in allowed_data_types:
                        setattr(self.__dict__['_data'], k, v)
                        
                    elif obj_type == RawType:
                        object.__setattr__(self, k, v.val)
                        
                    else:    
                        object.__setattr__(self, k, v)
                if v._type != ONE_TO_ONE or v._data is None:
                    return
            
            r = getattr(self.__class__, k)
            
            if r._type == ONE_TO_ONE:
                
                if r._pk[0] == '_id':
                    if not hasattr(v,'_id') or v._id == None:
                        if self._monga is None:
                            raise RelationError, "cannot auto-save one-to-one relation in smart object assignment. is object not binded with monga instance?"
                        # may unsaved doc, save it first
                        v.set_monga(self._monga)
                        v.save()

                elif not v._has_entryname(r._pk[0]):
                    raise RelationError, "relation model `%s` have no keyname `%s`" % (v.__class__.__name__, r._pk[0])
                        
                try:
                    fkey = getattr( v, r._pk[0] )
                except AttributeError:
                    fkey = None
                if fkey is not None:
                    if r._pk[1] == '_id':
                        setattr( self.__dict__['_data'], r._pk[1], type(fkey) != ObjectId and ObjectId(fkey) or fkey )
                    else:
                        setattr( self.__dict__['_data'], r._pk[1], type(fkey) == ObjectId and r._pk[1] != "_id" and str(fkey) or fkey )
                else:
                    # relasi terbalik berarti masukin ke pending ops ajah...
                    fkey = getattr( self.__dict__['_data'], r._pk[1] )
                    if fkey == None:
                        # parent lum di-save, save dulu
                        self.save()
                        fkey = self._id
                    self._pending_ops.add_op( v, 'setattr', key=r._pk[0], value= type(fkey) == ObjectId and r._pk[1] != "_id" and str(fkey) or fkey )
                    self._pending_ops.add_op( v, 'save' )
                    
            elif r._type == MANY_TO_ONE:
                
                if getattr( self.__dict__['_data'],'__meta_pcname__' ) == None:
                    setattr( self.__dict__['_data'], '__meta_pcname__', v.__class__.__name__ )
                else:
                    
                    # multi keys support
                    pcn = getattr( self.__dict__['_data'], '__meta_pcname__' )
                    if type(pcn) == types.ListType:
                        pc_names = pcn
                    else:
                        pc_names = [pcn]
                    pc_names.append(v.__class__.__name__)
                    setattr( self.__dict__['_data'], '__meta_pcname__', pc_names )
                    
                setattr( self.__dict__['_data'], r._pk, unicode(v._id) )
                
        else:
            if k in superdoc_reserved_words:
                return object.__setattr__(self, k, v)
            
            obj_type = type(v)
            
            if obj_type == dict:
                setattr(self.__dict__['_data'], k, cfma.Nested(v))
                
            elif obj_type == relation:
                object.__setattr__(self, k, v)
                value = RelationDataType(v)
                setattr(self.__dict__['_data'], k, v)
                
            else:
                
                if obj_type in allowed_data_types:
                    setattr(self.__dict__['_data'], k, v)
                    
                elif obj_type == RawType:
                    object.__setattr__(self, k, v.val)
                    
                else:    
                    object.__setattr__(self, k, v)


    def __delitem__(self, k):
        delattr(self.__dict__['_data'], k)

    
    def _saved(self):
        return getattr(self.__dict__['_data'],'_id') is not None
        
    
    def _changed(self):
        return not self._saved() or len(self.__dict__['_modified_childs']) > 0
        
        
    def delete(self):
        
        # hapus juga semua anak yg menjadi relasi di dalamnya
        # yang diset sebagai cascade=delete
        # fitur cascade tidak support many-to-many relation
        self._call_relation_attr('_delete_cascade')
        
        # update relation list metadata
        rels = filter( lambda x: type( getattr( self.__class__, x ) ) == relation, dir(self.__class__) )
        for rel in rels:
            
            vrela = getattr( self.__class__, rel )
            
            if vrela._type != MANY_TO_MANY:
               break
            
            keyrel = getattr( vrela, '_keyrel' )
            
            if getattr(self, keyrel[0]) is None:
                break
            
            backref = getattr( vrela, '_backref' )
            
            rela = getattr( vrela, '_get_rel_class' )()
            mykey = getattr(self.__dict__['_data'],backref[1])
            
            all_rela_obj = self._monga._db[rela._collection_name].find({ keyrel[0]: mykey })
            
            col_save = self._monga._db[rela._collection_name].save
            
            for rela_obj in all_rela_obj:
                
                rela_obj[keyrel[0]].remove(mykey)
                col_save(rela_obj)
                
        rv = False
        
        if getattr(self.__dict__['_data'], '_id') is not None:
            rv = self._monga._db[self._collection_name].remove(
                {'_id': self.__dict__['_data']['_id']}
            )
            self.__dict__['_data']._id = None
            
        return rv
    
    # support pickle protocol
    def __getstate__(self):
        return self.__dict__['_data']
    
    # support pickle protocol    
    def __setstate__(self,d):
        self.__dict__['_data'] = d

    def __repr__(self):
        
        if self._saved():
            return '<SuperDoc(id=%s)>' % self.__dict__['_data']._id
        else:
            return '<SuperDoc(id=Unsaved)>'

    def to_dict(self):
        """Public wrapper for converting an Nested object into a dict.
        """
        
        d = cfma.to_dict(self, self.__dict__['_data'], allowed_data_types, RelationDataType, DBRef, relation, SuperDoc)

        d_id = d.get("_id")
        
        if d_id is not None:
            d['_id'] = d_id

        return d

    def keys(self):
        """Get a list of keys for the current level.
        """
        
        keys = []
        for i in dir(self.__dict__['_data']):
            # skip private members
            if not i.startswith('_') and i != '_id':
                keys.append(i)

        return keys



