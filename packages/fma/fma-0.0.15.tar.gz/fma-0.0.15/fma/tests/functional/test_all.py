#comment-02
from fma.tests import *

class mongo_test(TestCase):
    
    def setUp(self):
        db_connection = connector.connect("test", "", "", "mongodb.test", 27017)
        self.connected = db_connection
        connector.db_instance._db.test.remove({})
        self.db = connector.db_instance
        
    def test_chain_effects(self):
        
        post = self.db.col(PostMany).new(isi='root')
        post.posts.append(PostMany(isi='sub1a'))
        post.posts.append(PostMany(isi='sub1b'))
        post.tags.append(Tags(isi=['mouse','cat']))
        post.tags[0].posts.append(PostMany(isi='post at mouse and cat tags'))
        post.posts[0].posts.append(PostMany(isi='sub2a'))
        post.posts[0].posts.append(PostMany(isi='sub2b'))
        post.posts[0].posts.append(PostMany(isi='sub2c'))
        post.posts[1].tags.append(Tags(isi=['sub1b tags']))
        post.tags[0].posts[0].tags.append(Tags(isi=['anvie','luna','exa']))
        post.tags[0].posts[0].tags.append(Tags(isi=['sky','walker']))
        
        #from dbgp.client import brk; brk()
        post.save()
        
        del post
        
        post = self.db.col(PostMany).find_one(isi='root')
        
        self.assertEqual(post.isi,'root')
        self.assertTrue( hasattr(post,'_id') )
        self.assertEqual( post.posts.count(), 2 )
        self.assertEqual( post.posts[0].isi, 'sub1a')
        self.assertEqual( post.posts[1].isi, 'sub1b')
        self.assertEqual( post.tags.count(), 1 )
        self.assertEqual( post.tags[0].posts[0].isi, 'post at mouse and cat tags' )
        self.assert_( 'mouse' in post.tags[0].isi and 'cat' in post.tags[0].isi )
        self.assertEqual( post.posts[1].tags[0].isi, ['sub1b tags'] )
        self.assert_( 'exa' in post.tags[0].posts[0].tags[0].isi )
        self.assertEqual( post.posts[1].posts.count(), 0  )
        subpost = post.tags[0].posts[0]
        self.assertEqual( subpost.tags.count(), 2 )
        self.assertEqual( post.tags[0].posts.count(), 1 )
        del post.tags[0].posts[0]
        post.save()
        self.assertEqual( post.tags[0].posts.count(), 0 )
        
        
    def test_user_wallpost_comment(self):
        
        usercol = self.db.col(User)
        
        usercol.query(name='tester').remove()
        
        tester = User(name='tester')
        usercol.insert(tester)
        
        user = usercol.find_one(name='tester')
        
        self.assertTrue( user, None )
        #from dbgp.client import brk; brk()
        user.wallposts.append(WallPost(message='tester is test',via='unitest'))
        user.save()
        
        self.assertEqual( user.wallposts.count(), 1 )
        self.assertEqual( user.wallposts[0].message, 'tester is test' )
        
        del user.wallposts[0]
        user.save()
        
        self.assertEqual( user.wallposts.count(), 0 )
        user.delete()

        self.assertEqual( usercol.find(name='tester').count(), 0 )
        
        
    def test_single_relation(self):
        '''Single relation (one-to-one) test
        '''
        
        self.db._db.test.remove({})
        
        usercol = self.db.col(User)
        
        obin = usercol.new(name='Obin MF')
        obin.save()
        
        market = self.db.col(Market).new(name='Market Keren')
        market.save()
        
        #from dbgp.client import brk; brk()
        obin.market = market
        
        obin.save()
        
        self.assertEqual( obin.market.name, 'Market Keren' )
        self.assertEqual( market.owner.name, 'Obin MF' )

    def test_metaname(self):
        '''Metaname test
        '''
        
        self.db.col(PostMany).query().remove()
        self.db.col(Tags).query().remove()
        
        self.assertEqual( self.db.col(Tags).find().count() , 0 )
        
        self.db.col(User).query().remove()
        
        user = self.db.col(User).new(name='new_user')
        post = self.db.col(PostMany).new(isi='apakekdah')
        post.posts.append(PostMany(isi='apaya'))
        post.tags.append(Tags(isi=['tags ajah']))
        
        user.save()
        post.save()
        
        del user
        del post
        
        user = self.db.col(User).find_one(name='new_user')
        post = self.db.col(PostMany).find_one(isi='apakekdah')
        
        self.assertEqual( user.name, 'new_user' )
        self.assertEqual( post.isi, 'apakekdah' )
        self.assertEqual( post.posts.count(), 1 )
        self.assertEqual( post.posts[0].isi, 'apaya' )
        self.assertEqual( post.tags.count(), 1 )
        self.assertEqual( post.tags[0].isi, ['tags ajah'] )
        self.assert_( hasattr(user.__dict__['_data'], '_metaname_') )
        self.assertEqual( user.__dict__['_data']._metaname_, 'User' )
        self.assertEqual( post.__dict__['_data']._metaname_, 'PostMany' )
        self.assertEqual( post.tags[0].__dict__['_data']._metaname_, 'Tags' )
        
        self.assertEqual( self.db.col(Tags).find().count() , 1 )
        
        post.tags.append(Tags(isi=['tags ajah-2']))
        
        post.save()
        
        self.assertEqual( self.db.col(Tags).find().count() , 2 )
        
        self.db.col(User).query(user_id=55).remove()
        
        self.db.col(PostMany).query().remove()
        
        self.assertEqual( self.db.col(Tags).count(), 2 )
        
        self.db.col(Tags).query(isi='tags ajah').remove()
        
        self.assertEqual( self.db.col(Tags).count(), 1 )
        
        self.db.col(Tags).query(isi='tags ajah-2').remove()
        
        self.assertEqual( self.db.col(Tags).count(), 0 )
        
        post.tags.append( Tags(isi=['123a']) )
        post.tags.append( Tags(isi=['123a']) )
        post.tags.append( Tags(isi=['123b']) )
        post.tags.append( Tags(isi=['123b']) )
        
        post.save()
        
        self.assertEqual( post.tags.count(), 4 )
        self.assertEqual( self.db.col(Tags).count(), 4 )
        self.assertEqual( self.db.col(Tags).count(isi='123a'), 2 )
        self.assertEqual( self.db.col(Tags).count(isi='123b'), 2 )
        
        self.db.col(Tags).query(isi='123a').remove()
        
        self.assertEqual( self.db.col(Tags).count(), 2 )
        
        self.db.col(Tags).query(isi='123b').remove()
        
        self.assertEqual( self.db.col(Tags).count(), 0 )
        
        
    def test_extended(self):
        
        self.db.col(Tags).query().remove()
        
        tags1 = self.db.col(Tags).new(isi=['cat','lazy','dog'])
        tags2 = self.db.col(Tags).new(isi=['animal','cat','pet'])
        tags3 = self.db.col(Tags).new(isi=['pet','health','cat'])
        tags4 = self.db.col(Tags).new(isi=['bird','animal'])
        
        tags1.save()
        tags2.save()
        tags3.save()
        tags4.save()
        
        self.assertEqual( tags1.get_related_tags().count(), 2 )
        self.assertEqual( tags4.get_related_tags().count(), 1 )
        
    def test_flipflap_relation(self):
        
        self.db._db.test.remove({})
        
        post1 = self.db.col(PostFlip).new(isi='post-1')
        post2 = self.db.col(PostFlip).new(isi='post-2')
        post3 = self.db.col(PostFlip).new(isi='post-3')
        post4 = self.db.col(PostFlip).new(isi='post-4')
        
        cat = TagFlip(isi='cat')
        lazy = TagFlip(isi='lazy')
        dog = TagFlip(isi='dog')
        animal = TagFlip(isi='animal')
        bird = TagFlip(isi='bird')
        
        self.db.col(TagFlip).insert(cat)
        self.db.col(TagFlip).insert(lazy)
        self.db.col(TagFlip).insert(dog)
        self.db.col(TagFlip).insert(animal)
        self.db.col(TagFlip).insert(bird)
        
        post1.tags.append(cat)
        post1.tags.append(lazy)
        post1.tags.append(dog)
        
        post2.tags.append(animal)
        post2.tags.append(cat)
        post2.tags.append(bird)
        
        post3.tags.append(animal)
        post3.tags.append(bird)
        
        post4.tags.append(animal)
        
        post1.save()
        post2.save()
        post3.save()
        post4.save()
        
        self.assertEqual( post1.tags.count(), 3 )
        self.assertEqual( post2.tags.count(), 3 )
        self.assertEqual( post3.tags.count(), 2 )
        
        self.assertEqual( post1.tags[0].isi, 'cat' )
        
        post1.tags[0].refresh()
        post3.tags[0].refresh()
        
        self.assertEqual( post1.tags[0].posts.count(), 2 )
        self.assertEqual( post3.tags[0].posts.count(), 3 )
        
        post5 = PostFlip(isi='sky')
        
        self.db.col(PostFlip).insert(post5)
        
        bird.posts.append(post5)
        bird.save()
        
        self.assertEqual( bird.posts.count(), 3 )
        
        # enter same tag test
        bird.posts.append(post5)
        bird.save()
        
        # seharusnya gak nambah
        self.assertEqual( bird.posts.count(), 3 )
        
        bird.posts.append(post1)
        bird.save()
        
        # test refresh
        self.assertTrue( post1.refresh() )
        
        self.assertEqual( post1.tags.count(), 4 )
        
        #
        # test relation many-to-many but uses model it self
        #
        user = self.db.col(User).new(name='ada-deh')
        
        exa = self.db.col(User).new(name='exa-tester')
        didit = self.db.col(User).new(name='didit-tester')
        
        exa.save()
        didit.save()
        
        user.friends.append(exa)
        user.friends.append(didit)
        
        user.save()
        
        self.assertEqual( user.friends.count(), 2 )
        
        exa.refresh()
        didit.refresh()
        
        self.assertEqual( exa.friends.count(), 1 )
        self.assertEqual( didit.friends.count(), 1 )
        
        exa.friends.append( didit )
        exa.save()
        
        self.assertEqual( exa.friends.count(), 2 )
        
        exa.friends.remove( didit )
        
        exa.save()
        #exa.refresh()
        
        self.assertEqual( exa.friends.count(), 1 )
        self.assertEqual( exa.friends[0].name, 'ada-deh')
        
        self.assertTrue( exa in user.friends )
        self.assertTrue( didit in user.friends )
        
        didit.delete()
        
        user.refresh()
        
        self.assertTrue( didit not in user.friends )
        #from dbgp.client import brk; brk()
        self.assertTrue( exa in user.friends )
        
        exa.delete()
        
        user.refresh()
        
        self.assertTrue( exa not in user.friends )
        self.assertEqual( user.friends.count(), 0 )
        
        del user
        
    
    def test_data_type(self):
        
        self.db._db.test.remove({})
        
        post = self.db.col(PostMany).new(isi='test')
        post.save()
        
        post.nomor = 5
        post.yatidak = True
        post.yatidak = 1
        post.yatidak = 0
        
        
        post.save()
        del post
        
        post = self.db.col(PostMany).find_one(isi='test')
        
        self.assertEqual( post.nomor, 5 )
        
        
    def test_many_child(self):
        
        self.db._db.test.remove({})
        
        pa = self.db.col(parent).new(name='anvie-keren')
        
        pa.childs.append(child(name='c1'))
        pa.childs.append(child(name='c2'))
        pa.childs.append(child(name='c3'))
        pa.childs.append(child(name='c4'))
        pa.childs.append(child(name='c5'))
        pa.childs.append(child(name='c6'))
        pa.childs.append(child(name='c7'))
        pa.childs.append(child(name='c8'))
        pa.childs.append(child(name='c9'))
        pa.childs.append(child(name='c10'))
        pa.childs.append(child(name='c11'))
        pa.childs.append(child(name='c12'))
        pa.childs.append(child(name='c13'))
        pa.childs.append(child(name='c14'))
        pa.childs.append(child(name='c15'))
        pa.childs.append(child(name='c16'))
        
        pa.save()
        
        #from dbgp.client import brk; brk()
        
        del pa
        pa = self.db.col(parent).find_one(name='anvie-keren')
        
        self.assertEqual( pa.name, 'anvie-keren' )
        self.assertEqual( pa.childs[0].name, 'c1')
        
        #from dbgp.client import brk; brk()
        
        self.assertEqual( pa.childs[13].name, 'c14') # lazy load test memory cache
        self.assertEqual( pa.childs[12].name, 'c13') # lazy load test memory cache
        self.assertEqual( pa.childs[12].name, 'c13')
        
        # test pencarian single item
        self.assertEqual( pa.childs.find(name='c3'), pa.childs[2] )
        
        # test pencarian menggunakan metode filter
        rv = pa.childs.filter(name__in=['c5','c12']).sort(_id=1)
        self.assertEqual( rv.count(), 2 )
        self.assertEqual( rv.all()[0].name, 'c5' )
        
        # test clear all
        self.assertNotEqual(pa.childs.count(),0)
        pa.childs.clear()
        self.assertEqual(pa.childs.count(),0)
        
    def test_list_dict(self):
        
        self.db._db.test.remove({})
        
        u = self.db.col(User).new(name='anvie-keren')
        u.settings.test = 'is'
        u.save()
        
        del u
        
        #from dbgp.client import brk; brk()
        u = self.db.col(User).find_one(name='anvie-keren')
        
        self.assertEqual( u.name, 'anvie-keren' )
        
        self.assertEqual( u.settings.test, 'is')
        
        u.settings.oi = 'yeah'
        u.save()
        
        del u
        
        u = self.db.col(User).find_one(name='anvie-keren')
        
        self.assertEqual( u.settings.oi, 'yeah' )
        
    def test_default_value(self):
        """Default and required value"""
        
        self.db._db.test.remove({})
        
        wp = WallPost(message='test',via='jakarta')
        wp.save()
        
        writer = User(name='anvie')
        
        #from dbgp.client import brk; brk()
        comment = self.db.col(Comment).new(message="hai test", item_id = wp._id, writer = writer)
        
        comment.save()
        
        self.assertNotEqual( comment._creation_time , None )
        
    def test_none_type(self):
        
        self.db._db.test.remove({})
        
        #from dbgp.client import brk; brk()
        
        msg = Message(subject='subject-test',content='content-test')
        msg.save()
        
        self.assertEqual( msg.owner, None)
        
        del msg
        
        msg = self.db.col(Message).find_one( subject = 'subject-test' )
        
        self.assertEqual( msg.owner, None)
        
        user = User(name='test-user')
        
        msg.owner = user
        
        msg.save()
        
        del msg
        
        msg = self.db.col(Message).find_one( subject = 'subject-test' )
        
        self.assertEqual( msg.owner.name, 'test-user')
        
        pitem_category = ProductItemCategory(name='Elektronik', code=38, parent_code=0, active=True)
        pitem_category.save()
        
        prod = self.db.col(ProductItem).new( name='test',description='test',category_code=38 )
        prod.save()
        
        del prod
        
        prod = self.db.col(ProductItem).find_one(name='test')
        
        self.assertEqual( prod.category.name, 'Elektronik')
        
    def test_map_reduce(self):
        '''about to test map reduce functionality.
        if your mongod become crash, please update your mongo to version >= 1.2.0,
        this test work fine in 1.2.0
        '''
        
        # from dbgp.client import brk; brk()
        
        self.db._db.test.remove({})
            
        self.db.col(Item).insert(Item(name='obin',tags=['keren','cool','nerd']))
        self.db.col(Item).insert(Item(name='imam',tags=['keren','funny','brother']))
        self.db.col(Item).insert(Item(name='nafid',tags=['brother','funny','notbad']))
        self.db.col(Item).insert(Item(name='uton',tags=['smart','cool','notbad']))
        self.db.col(Item).insert(Item(name='alfen',tags=['fat','nocool','huge']))
        
        map_ = '''function () {
          this.tags.forEach(function(z) {
            emit(z, 1 );
          });
        }'''
        
        reduce_ = '''function (key, values) {
          var total = 0;
          for (var i = 0; i < values.length; i++) {
            total += values[i];
          }
          return total;
        }'''

        rv = self.db.col(Item).map_reduce( map_, reduce_ )
        
        true_result = [
            {u'_id': u'brother', u'value': 2.0},
            {u'_id': u'cool', u'value': 2.0},
            {u'_id': u'fat', u'value': 1.0},
            {u'_id': u'funny', u'value': 2.0},
            {u'_id': u'huge', u'value': 1.0},
            {u'_id': u'keren', u'value': 2.0},
            {u'_id': u'nerd', u'value': 1.0},
            {u'_id': u'nocool', u'value': 1.0},
            {u'_id': u'notbad', u'value': 2.0},
            {u'_id': u'smart', u'value': 1.0}
        ]
        
        cr = rv.find()
        
        for i, x in enumerate(cr):
            self.assertEqual( x, true_result[i] )
            
        
        # test inline mapreduce, this feaute new in MongoDB 1.7.4
        rv = self.db.col(Item).inline_map_reduce( map_, reduce_)
        
        for i, x in enumerate(rv):
            self.assertEqual( x, true_result[i] )
            
        self.db._db.drop_collection("map_reduce_result")
        

    def test_cascade(self):
        
        
        self.db._db.test.remove({})
        
        # from dbgp.client import brk; brk()
        
        obin = parent( name = 'obin' )
        
        obin.save()
        
        # from dbgp.client import brk; brk()
        anvie = child(name='anvie')
        anvie2 = child(name='anvie2')
        anvie3 = child(name='anvie3')
        
        
        obin.childs.append(anvie)
        obin.childs.append(anvie2)
        obin.childs.append(anvie3)
        
        obin.save()
        
        self.assertEqual(obin.childs.count(), 3)
        del obin.childs[-1]
        obin.save()
        #from dbgp.client import brk; brk()
        self.assertEqual(obin.childs.count(), 2)
        self.assertEqual(obin.childs[0].name,'anvie')
        self.assertEqual(obin.childs[1].name,'anvie2')
        
        self.assertEqual(self.db.col(child).find(name='anvie').count(),1)
        
        #from dbgp.client import brk; brk()
        
        obin.delete()
        
        self.assertEqual(self.db.col(child).find(name='anvie').count(),0)
        self.assertEqual(self.db.col(child).find(name='anvie2').count(),0)
        
        
    def test_many_to_one(self):
        
            self.db._db.test.remove({})
            
            
            parent1 = another_parent1(name = 'parent1')
            
            parent2 = another_parent2(name = 'parent2')
            
            
            anvie1 = child(name='anvie1')
            anvie2 = child(name='anvie2')
            
            
            parent1.childs.append(anvie1)
            parent2.childs.append(anvie2)
            
            parent1.save()
            parent2.save()
            
            
            self.assertEqual( anvie1.another_parent.name, 'parent1' )
            self.assertEqual( anvie2.another_parent.name, 'parent2' )
            
    def test_options_type(self):
        
        self.db._db.test.remove({})
        
        #from dbgp.client import brk; brk()
        
        anvie = child(name="anvie", gender="wanita")
        try:
            anvie = child(name="anvie", gender="laki-laki")
        except:
            anvie = None
            
        self.assertEqual( anvie, None )
        
        anvie = child(name="anvie", gender="pria")
        
        anvie.save()
        
        self.assertEqual( anvie.gender, "pria" )
        
        
    def test_inheritance(self):
        
        self.db._db.test.remove({})
        
        anvie = Employee(
            name = "anvie",
            age = 23
        )
        didit = Programmer(
            name = "didit",
            age = 23,
            division = "engine"
        )
        exa = Programmer(
            name = "exa",
            age = 27,
            division = "ui"
        )
        tommy = Marketing(
            name = "tommy",
            age = 31
        )
        mac = Resource(
            name = "macbook pro",
            price = 13000000
        )
        
        didit.tools.append(mac)
        
        # from dbgp.client import brk; brk()
        
        anvie.save()
        didit.save()
        exa.save()
        tommy.save()
        
        self.assertEqual(anvie.name,"anvie")
        self.assertEqual(didit.name,'didit')
        self.assertEqual(didit.sallary, 8000000)
        
        didit = self.db.col(Programmer).find_one(name="didit")
        
        self.assertNotEqual(didit, None)
        self.assertEqual(type(didit), Programmer)
        self.assertEqual(didit.get_sallary(), 8000000)
        
        self.assertEqual( didit.tools.count(), 1 )
        self.assertEqual( didit.tools[0].name, "macbook pro" )
        self.assertEqual( didit.tools[0].owner.name, "didit" )
    
        misbah = CoProgrammer(self.db,name="misbah")
        misbah.save()
        
        self.assertEqual(misbah.age,None)
        self.assertEqual(misbah.division,None)
        self.assertEqual(misbah.name,"misbah")
        self.assertEqual(misbah.position,"Co Programmer")
        self.assertEqual(misbah._credential_id,None)
        
        # test multiple inheritance
        #from dbgp.client import brk; brk()
        self.assertEqual(exa._active,True)
        
        
    def test_query(self):
        '''Test query for update and delete.
        '''
        self.db._db.test.remove({})
        
        market = Market(name = "arcane")
        post = MarketPost(
            title = "Kartu keren",
            _content = "Content of Kartu keren"
        )
        post2 = MarketPost(
            title = "Kartu keren 2",
            _content = "Content of Kartu keren 2"
        )
        
        market.posts.append(post)
        market.posts.append(post2)
        #from dbgp.client import brk; brk()
        market.save()
        
        market = self.db.col(Market).find_one(name="arcane")
        
        self.assertNotEqual(market,None)
        
        #from dbgp.client import brk; brk()
        
        posts = market.posts.all()
        
        self.assertEqual(len(posts),2)
        
        post_ids = [str(x._id) for x in posts]
        
        market.posts.query(_id__in = post_ids).remove()
        
        self.assertEqual(market.posts.count(),0)
        
        
    def test_query_relation(self):
        '''Relation query mode
        '''
        
        self.db._db.test.remove({})
        
        #from dbgp.client import brk; brk()
        
        p = parent(
            name = "robin"
        )
        p.childs.append(
            child(name = "imam",gender="pria")
        )
        p.childs.append(
            child(name = "yani",gender="wanita")
        )
        p.childs.append(child(name="anis",gender="wanita"))
        
        p.save()
        
        #from dbgp.client import brk; brk()
        
        self.assertEqual(p.childs_co.count(), 1)
        self.assertEqual(p.childs_ce.count(), 2)
        
        a = child(name="a",_teacher_ids=["ab8203faad","023984a5ee"]).save()
        b = child(name="b",_teacher_ids=["ab8203faad",str(p._id)]).save()

        
        self.assertEqual(p.childs_spec.count(),1)
        
        x = p.childs_spec.next()
        
        self.assertEqual(x,b)
        
        child(name="c",_teacher_ids=["ab8203faad",str(p._id)]).save()
        child(name="d",_teacher_ids=["ab8203faad",str(p._id)]).save()
        child(name="e",_teacher_ids=["ab8203faad",str(p._id)]).save()
        
        
        self.assertEqual(p.childs_spec.count(),4)
        
        child_names = ["b","c","d","e"]
        
        for i,son in enumerate(p.childs_spec):
            self.assertEqual(son.name, child_names[i])
            
        males = p.childs_co()
        females = p.childs_ce()
        
        self.assertEqual(males.count(), 1)
        self.assertEqual(females.count(), 2)
        
        
    def test_variant(self):
        """Variant type"""
        
        #from dbgp.client import brk; brk()
        a = VariantTest(value = 5)
        a.save()

        self.assertEqual(a.value, 5)
        
        
    def test_xx_polymorphic(self):
        """Polymorphic test"""
        
        #from dbgp.client import brk; brk()
        a = PolyParent()
        a.save()
        
        a.polies.append(PolyChild1(name="p1"))
        a.polies.append(PolyChild2(name="p2"))
        a.save()
        
        self.assertEqual(a.polies[0].__class__.__name__,"PolyChild1")
        self.assertEqual(a.polies[1].__class__.__name__,"PolyChild2")
        self.assertEqual(a.polies[0].name,"p1")
        self.assertEqual(a.polies[1].name,"p2")
        
        
    def test_object_copy(self):
        '''Object copy
        '''
        
        a = Item(name="a",tags=[1,2,3])
        rv = a.save()
        self.assertNotEqual(rv, None)
        
        b = a.copy()
        self.assertNotEqual(b, None)
        self.assertEqual(hasattr(b,'_id'),False)
        
        rv = b.save()
        self.assertNotEqual(rv, None)
        self.assertNotEqual(rv._id, None)
        
        
    def test_nested(self):
        '''Nested
        '''
        
        p = parent(name="parent1")
        self.assertNotEqual(p, None)
        c = child(name="child-of-parent1")
        c.save()
        
        #from dbgp.client import brk; brk()
        p.single_child = c
        p.save()
        
        self.assertEqual(p.single_child.name,"child-of-parent1")
        
        p2 = connector.db_instance.col(parent).find_one(name="parent1")
        self.assertNotEqual(p2, None)
        
        self.assertEqual(p.single_child.name,"child-of-parent1")
        
        #from dbgp.client import brk; brk()
        p2.single_child.name = "child-of-parent1-edited"
        p2.save()
        
        self.assertEqual(p2.single_child.name,"child-of-parent1-edited")
        
        
    def test_or_operator(self):
        
        ## $or operator New in MongoDB 1.5.3
        #from dbgp.client import brk; brk()
        # check mongodb version
        import fma
        if not fma.helpers.is_support('operator_$or'):
            print "This mongodb version not support $or operator. Test skipped."
            return
        
        
        item1 = Item(name = "item1").save()
        item2 = Item(name = "item2").save()
        item3 = Item(name = "item3").save()
        
        self.assertNotEqual(item1, None)
        self.assertNotEqual(item2, None)
        self.assertNotEqual(item3, None)
        
        #from dbgp.client import brk; brk()
        rv = self.db.col(Item).find(or__=[{'name':'item1'}])
        self.assertEqual(rv.count(), 1)
        rv = self.db.col(Item).find(or__=[{'name':'item1'},{'name':'item2'}])
        self.assertEqual(rv.count(), 2)
        rv = self.db.col(Item).find(or__=[{'name':'item1'},{'name':'item2'},{'name':'item3'}])
        self.assertEqual(rv.count(), 3)
        
        

if __name__ == "__main__":
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(mongo_test)
    unittest.TextTestRunner(verbosity=2).run(suite)
