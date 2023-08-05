
from pymongo.objectid import ObjectId
from exc import RelationError
from pymongo.binary import Binary
import cfma

__all__ = [
    'ObjectId', 'Binary', 'RelationError',
    'options', 'ConditionQuery', 'or_', 'and_',
    'rawcond', 'dictarg', 'RawType', 'variant',
    'ONE_TO_ONE','ONE_TO_MANY','MANY_TO_ONE','MANY_TO_MANY','relation_types'
]

ONE_TO_ONE = 1
ONE_TO_MANY = 2
MANY_TO_ONE = 3
MANY_TO_MANY = 4

relation_types= {
    'one-to-one': ONE_TO_ONE,
    'one-to-many': ONE_TO_MANY,
    'many-to-one': MANY_TO_ONE,
    'many-to-many': MANY_TO_MANY
}

class RawType(object):
    
    def __init__(self, val):
        self.val = val

class ConditionQuery(object):
    
    def __init__(self, **conds):
        self._cond = conds
        
    def update(self,conds):
        self._cond.update(conds)

    @property
    def raw(self):
        return self._cond

    @property
    def where_value(self):
        return None
    
    def __setitem__(self, k, v):
        self._cond[k] = v

    def where(self,**params):

        rv = self.apply(**params)

        return rv and { '$where': rv } or None


    def apply(self,**patch):
        return cfma.apply_condition_query(self.where_value, **patch)
            

    def __repr__(self):
        return '<%s>' % self.__class__.__name__
    
    
class or_(ConditionQuery):

    def __init__(self, **conds):
        self._cond = conds
        
    @property
    def where_value(self):

        return ' || '.join( map(lambda x: 'this.%s == %s' % x, self._cond.items()) )

    def __repr__(self):
        return '<or_ ConditionQuery [%s]>' % self.where_value


class and_(ConditionQuery):

    @property
    def where_value(self):
        
        return cfma.parse_query( self._cond )
        
    def where(self,**params):
        
        rv = self.apply(**params)

        return rv


    def __repr__(self):
        return '<and_ ConditionQuery [%s]>' % self.where_value
    
    
class rawcond(ConditionQuery):
    
    
    @property
    def where_value(self):
        return cfma.parse_query( self._cond )
        

    def __repr__(self):
        return '<or_ ConditionQuery [%s]>' % self.where_value
    

class options(list):
    
    def __call__(self, value):
        '''berguna untuk mengisi data dan konversi
        '''
        if value not in self:
            raise TypeError, "Cannot assign value `%s`. Accept only `%s`" % (value, str(self))
        self.value = value
        return value
    
    def __init__(self,*args):
        list.__init__(self,args)
        self.value = None


class variant(object):
    pass
    

dictarg = cfma.dictarg


if __name__ == '__main__':
    
    
    import unittest
    
    class test(unittest.TestCase):
        
        def test_rawcond(self):
            
            cond = rawcond(name__in=':namatamu')
            tamu = ['cat','bird','wind']
            
            self.assertEqual( cond.where(namatamu=tamu), {'$where': {'name': {'$in': ['cat', 'bird', 'wind']}}} )
            
            
        def test_where_stringcond(self):
            
            cond = or_(name=':name',age=':age')
            
            self.assertEqual( cond.where(name='anvie',age=15), {'$where': "this.age == 15 || this.name == 'anvie'"} )
            
    
    suite = unittest.TestLoader().loadTestsFromTestCase(test)
    unittest.TextTestRunner(verbosity=2).run(suite)

    
    
    

