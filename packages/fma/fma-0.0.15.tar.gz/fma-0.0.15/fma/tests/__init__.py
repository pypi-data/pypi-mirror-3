#!/usr/bin/env python

from fma import MongoDB, SuperDoc, Collection, relation, query, this, mapper, connector
from fma.antypes import *
import datetime
from unittest import TestCase
from fma import connector

datetime_type = datetime.datetime


class PostMany(SuperDoc):
    
    _collection_name = 'test'
    
    tag_id = unicode
    sub_post_id = unicode
    isi = unicode
    nomor = int
    yatidak = bool
    
    tags = relation('Tags',pk='pm_id==_id',cascade='delete')
    posts = relation('PostMany',pk='sub_post_id==_id')
    
    _opt = dict(strict=True)
    
    
class Tags(SuperDoc):
    
    _collection_name = 'test'
    
    pm_id = unicode
    isi = list
    
    posts = relation('PostMany',pk='sub_post_id==_id')
    
    
    def get_related_tags(self):
        return Collection( connector.db_instance,Tags ).find(isi__in=self.isi,_id__ne=self._id)
        
    

class PostFlip(SuperDoc):
    
    _collection_name = 'test'
    
    
    tags = relation('TagFlip',type_='many-to-many',keyrel='_tags:_id',backref='_posts:_id')
    
    
class TagFlip(SuperDoc):
    
    _collection_name = 'test'
    
    posts = relation('PostFlip',type_='many-to-many',keyrel='_posts:_id',backref='_tags:_id')
    
    

class User(SuperDoc):

    _collection_name = 'test'
    
    name = unicode
    first_name = unicode
    last_name = unicode
    email = unicode
    birth_date = datetime_type
    pic_avatar = unicode
    age = int
    lang_id = unicode
    contact = dict
    settings = dict
    
    _creation_time = datetime_type
    _authority = int
    _pass_hash = unicode
    _last_activity = datetime_type
    _last_login_time = datetime_type
    _reputation_level = int
    _warning_level = int
    _advertiser = bool
    _banned = bool
    _banned_type = int # 1 = permanent, 2 = with expiration
    _banned_expiration_time = datetime_type
    _hash = int
    
    wallposts = relation('WallPost',pk='wuid==_id',cond=or_(wuid=':_id',ruid=':_id'),cascade="delete")
    friends = relation('User',type_='many-to-many',keyrel='_friends:_id',backref='_friends:_id')
    market = relation('Market',pk='owner_user_id==_id',type_='one-to-one',cascade='delete')
    bids = relation('Item',pk='bidder_id==_id',cond=and_(item_class='Bid'))
    warnings = relation('Item',pk='user_id==_id',cond=and_(item_class='UserWarning'),cascade='delete')
    messages = relation('Message',pk='to_user_id==_id')
    sent_messages = relation('Message',pk='from_user_id==_id')
    
    
    _opt = {
        'req' : ['name'],
        'default' : dict(name='', _creation_time=datetime.datetime.utcnow),
        'strict' : True
    }


class WallPost(SuperDoc):

    _collection_name = 'test'
    
    wuid = unicode
    ruid = unicode
    
    message = unicode
    via = unicode
    _creation_time = datetime.datetime
    
    writer = relation('User',pk='_id==wuid', type_="one-to-one")
    receiver = relation('User',pk='_id==ruid', type_="one-to-one")
    comments = relation('Comment',pk='itemid==_id', cascade='delete')
    
    _opt = {
        'req' : ['message','via'],
        'default' : dict(_creation_time=datetime.datetime.utcnow),
        'strict' : True
    }
    

        
class Message(SuperDoc):
    
    _collection_name = 'test'
    
    to_user_id = unicode
    from_user_id = unicode
    subject = unicode
    content = unicode
    
    _readed = bool
    _replied = bool
    _deleted = bool
    _deleted_time = datetime_type
    _allow_html = bool

    owner = relation('User', pk='_id==to_user_id', type_='one-to-one')
    sender =  relation('User', pk='_id==from_user_id', type_='one-to-one')

    @property
    def readed(self):
        return self._readed

    @property
    def replied(self):
        return self._replied

    @property
    def deleted(self):
        return self._deleted

    
class UserNotification(SuperDoc):
    
    _collection_name = 'test'
    
    TYPE_GENERAL = 0
    TYPE_COMMENT = 1
    TYPE_BID = 2
    TYPE_TESTIMONIAL = 3
    TYPE_WARNING = 4
    TYPE_ERROR = 5
    TYPE_PRODUCT_ITEM_UPDATED = 6

    user_id = unicode
    subject = unicode
    message = unicode
    email_notification = bool
    
    _received_time = datetime_type
    _expired = bool
    _closed = bool
    _closed_time = datetime_type
    _readed = bool
    _type = int # TYPE_*

    user = relation('User',pk='_id==user_id')

    _opt = {
        'default' : dict(_creation_time=datetime.datetime.utcnow,_received_time=datetime.datetime.now)
    }

    @property
    def notification_type(self):
        return self._type

    @property
    def received_time(self):
        global _standard_time_format
        return self._received_time.strftime(_standard_time_format)

class UserCart(SuperDoc):
    
    _collection_name = 'test'
    
    user_id = unicode
    product_item_id = unicode
    _added_time = datetime_type

    user = relation('User',pk='_id==user_id')
    product_item = relation('ProductItem',pk='_id==user_id')

class UserActivity(SuperDoc):
    
    _collection_name = 'test'
    
    ACCESS_PUBLIC = 0
    ACCESS_PRIVATE = 1
    ACCESS_INTERNAL = 2

    TYPE_GENERAL = 0
    TYPE_MAKE_BID = 1
    TYPE_WRITE_COMMENT = 2
    TYPE_MAKE_RECOMMENDATION = 3
    TYPE_WRITE_TESTIMONIAL = 4
    TYPE_MAKE_ABUSE = 5

    user_id = unicode
    last_time = datetime_type
    info = unicode
    
    _access = int   # ACCESS_*
    _type = int

    user = relation('User',pk='_id==user_id')

class Market(SuperDoc):
    
    _collection_name = 'test'
    
    owner_user_id = unicode
    name = unicode
    description = unicode
    pic_logo = unicode
    address = unicode
    city = unicode
    province = unicode
    country = unicode
    zip_postal_code = unicode
    phone1 = unicode
    phone2 = unicode
    fax = unicode
    email = unicode
    
    settings = dict
    bad_bidders = list  # list of User
    
    _creation_time = datetime_type
    _closed = bool
    _closed_time = datetime_type
    
    _certified = bool
    _certification_type = int
    _certified_since = datetime_type
    
    _reputation_level = int
    _popularity_level = int
    _suspended = bool
    _suspended_info = unicode
    _first_time_add_product_item = bool

    owner = relation('User',pk='_id==owner_user_id',type_='one-to-one')
    product_items = relation('ProductItem',pk='owner_market_id==_id',type_='one-to-many')
    abuser = relation('Abuser',pk='item_id==_id',type_='one-to-many')
    visitors = relation('Visitor',pk='item_id==_id',cond=and_(item_class='Visitor'),type_='one-to-many')
    posts = relation('MarketPost',pk='market_id==_id',type_="one-to-many")
    testi = relation('Testimonial',pk='market_id==_id',type_='one-to-many')



class MarketPost(SuperDoc):
    
    _collection_name = 'test'
    
    market_id = unicode
    poster_user_id = unicode
    title = unicode
    _content = unicode
    order = int
    _creation_time = datetime_type
    _closed = bool
    _closed_time = datetime_type
    _deleted = bool
    _deleted_time = datetime_type
    _allow_comment = bool
    _published = bool

    market = relation('Market',pk='_id==market_id',type_="one-to-one")
    author = relation('User', pk='poster_user_id==_id',type_="one-to-one")
    comments = relation('Comment', pk='itemid==_id')



class Testimonial(SuperDoc):
    
    _collection_name = 'test'
    
    market_id = unicode
    poster_user_id = unicode
    subject = unicode
    content = unicode
    
    _approved = bool
    _creation_date = datetime_type
    _deleted = bool
    _deletion_date = datetime_type
    _responsible_mod_id = unicode
    _deletion_reason = unicode

    poster = relation('User',pk='_id==poster_user_id')
    market = relation('Market',pk='_id==market_id')

class Visitor(SuperDoc):
    
    _collection_name = 'test'
    
    item_id = unicode
    user_id = unicode
    
    user = relation('User',pk='_id==user_id')
    

class Abuser(SuperDoc):
    
    _collection_name = 'test'
    
    item_id = unicode
    user_id = unicode
    
    user = relation('User',pk='_id==user_id')

class ProductItem(SuperDoc):
    
    _collection_name = 'test'
    
    # prduct state = 1.new, 2.second, 3.builtup etc

    NEW = 1
    SECOND = 2
    BUILTUP = 3

    market_id = unicode
    name = unicode
    description = unicode
    category_code = int
    _overview = unicode
    currency_code = int
    _price = float
    _stock = int
    auction = bool
    auction_expired = bool
    _starter_bid = float
    _min_bid_addition = float
    keywords = unicode
    condition = int  # prduct condition = 1.new, 2.second, 3.buuiltup etc
    related_review_link = unicode
    _permalink = unicode
    _allow_comment = bool
    pic_thumbnail = unicode
    status = int # prduct status = 1.available 2.sold 3.booked 4.delivered 5.pending 6.blank
    status_relatedto_user_id = int # ex. sold to kocakboy
    top_order = int
    _auto_approve_bid = bool
    _creation_time = datetime_type
    _last_updated = datetime_type
    _last_updated_by = unicode  # user id
    _update_reason = unicode
    
    _closed = bool
    _closed_permanently = bool
    _closed_time = datetime_type
    _sold = bool
    _sold_time = datetime_type
    _out_of_stock = bool
    _rank_level = int
    _suspended = bool
    _suspended_info = unicode
    _deleted = bool
    _deleted_time = datetime_type
    _last_bid_update = datetime_type
    _hash = int
    
    recommenders = list
    viewers = list
    guest_view_count = int

    market = relation('Market', pk='_id==market_id')
    bids = relation('Bidder', pk='product_item_id==_id')
    abuser = relation('Abuser', pk='product_item_id==_id')
    currency = relation('Currency', pk='code==currency_code',type_='one-to-one')
    comments = relation('Comment', pk='item_id==_id')
    category = relation('ProductItemCategory', pk='code==category_code',type_='one-to-one')
    last_editor = relation('User',pk='_id==_last_updated_by',type_='one-to-one')
    blacklist_user_bids = relation('BadBidder',pk='product_item_id==_id')
    subscribers = relation('ProductItemSubscription',pk='product_item_id==_id')


class Viewer(SuperDoc):
    
    _collection_name = 'test'
    
    user_id = unicode

    user = relation('User',pk='_id==user_id')


class Bidder(SuperDoc):
    
    _collection_name = 'test'
    
    product_item_id = unicode
    bidder_user_id = unicode
    _amount = float
    bid_datetime = datetime_type
    additional_info = unicode
    _approved = bool

    product_item = relation('ProductItem', pk='_id==product_item_id')
    user = relation('User',pk='_id==user_id')

    @property
    def amount(self):
        '''Synonym for _amount. get formated amount in currency format.
        for direct access, use _amount instead
        '''
        return "%s %s %s" % (self.product_item.currency.sign_first, format_numeric(self._amount), self.product_item.currency.sign_last)

    @property
    def applied_on(self):
        '''mendapatkan waktu bid (bid_datetime) yang terformat
        '''
        return self.bid_datetime.strftime("%a, %d/%m/%Y %H:%M:%S")

class Recommend(SuperDoc):
    
    _collection_name = 'test'
    
    product_item_id = unicode
    user_id = unicode

    user = relation('User',pk='_id==user_id')
    item = relation('ProductItem',pk='_id==product_item_id')


class ProductItemCategory(SuperDoc):
    
    _collection_name = 'test'
    
    name = unicode
    keywords = list
    code = int
    parent_code = unicode
    active = bool

    parent = relation('ProductItemCategory',pk='code==parent_code')
    subcategories = relation('ProductItemCategory',pk='parent_code==code',type_='one-to-many')
    product_items = relation('ProductItem',pk='category_code==code',type_='one-to-many')


class ProductItemSubscription(SuperDoc):
    
    _collection_name = 'test'
    
    user_id = unicode
    product_item_id = unicode
    active = bool

    user = relation('User',pk='_id==user_id',type_='one-to-one')
    item = relation('ProductItem',pk='_id==product_item_id',type_='one-to-one')

class Currency(SuperDoc):
    
    _collection_name = 'test'
    
    name = unicode
    sign_first = unicode
    sign_last = unicode


class BadBidder(SuperDoc):
    
    _collection_name = 'test'
    
    user_id = unicode
    _active = bool

    
class Comment(SuperDoc):
    
    _collection_name = 'test'
    
    item_id = unicode
    writer_id = unicode
    message = unicode
    _creation_time = datetime_type
    _last_edited = datetime_type
    
    writer = relation('User',pk='_id==writer_id',type_='one-to-one')
    
    _opt = {
        'req' : ['item_id','writer_id','message','_creation_time'],
        'default' : {'_creation_time':datetime.datetime.utcnow}
    }
    

class parent(SuperDoc):
    _collection_name = 'test'

    name = unicode

    childs = relation('child',pk='parent_id==_id',type_='one-to-many',cascade='delete')
    childs_spec = query("child",dict(_teacher_ids = this("_id")))
    childs_co = query("child",dict(gender="pria"))
    childs_ce = query("child",dict(gender="wanita"))
    single_child = relation('child',pk='parent_id==_id',type_='one-to-one')

# untuk test many-to-one
class another_parent1(SuperDoc):
    _collection_name = 'test'
    
    
    childs = relation('child',pk='another_parent_id==_id',type_='one-to-many',cascade='delete', backref = 'another_parent')

class another_parent2(SuperDoc):
    _collection_name = 'test'
    
    childs = relation('child',pk='another_parent_id==_id',type_='one-to-many',cascade='delete', backref = 'another_parent')



class child(SuperDoc):
    
    _collection_name = 'test'
    
    parent_id = unicode
    name = unicode
    another_parent_id = unicode
    gender = options("pria","wanita")
    _teacher_ids = list
    
    parent = relation('child',pk='_id==parent_id',type_='one-to-one')
    another_parent = relation(pk='another_parent_id',type_='many-to-one')
    
    
#
# test inheritance
#
class Employee(SuperDoc):
    
    _collection_name = "test"
    
    name = unicode
    age = int
    _position = unicode
    _credential_id = unicode
    
    def get_sallary(self):
        return self.sallary
    
class OutSourcer(SuperDoc):
    
    _active = bool
    
    _opt = {
        "default" : {
            "_active" : True
        }
    }
    
    def set_active(self,active):
        self._active = active
        
    
class Programmer(Employee, OutSourcer):
    
    sallary = 8000000
    
    division = unicode
    
    tools = relation("Resource",pk="user_id==_id",type_="one-to-many")
    
    
class Marketing(Employee):
    
    sallary = 5000000
    
class CoProgrammer(Programmer):
    
    salarry = 5000000
    _position = "Co Programmer"
    
    @property
    def position(self):
        return self._position
    
class Resource(SuperDoc):
    
    _collection_name = "test"
    
    user_id = unicode
    name = unicode
    price = long
    
    
    owner = relation("Programmer",pk="_id==user_id",type_="one-to-one")
    
    
class VariantTest(SuperDoc):
    _collection_name = "test"
    
    value = variant()



class Item(SuperDoc):
    _collection_name = 'test'
    
    name = unicode
    tags = list
    
    
class PolyParent(SuperDoc):
    _collection_name = 'test'
    
    
    polies = relation("Poly",pk="_parent_id==_id",poly=True)
    
    
class Poly(SuperDoc):
    _collection_name = 'test'
    
    _parent_id = unicode
    name = unicode

class PolyChild1(Poly):
    pass

class PolyChild2(Poly):
    pass
    

mapper(User,
       WallPost,
       Message,
       UserNotification,
       UserCart,
       UserActivity,
       Market,
       MarketPost,
       Testimonial,
       Visitor,
       Abuser,
       ProductItem,
       Viewer,
       Bidder,
       Recommend,
       ProductItemCategory,       
       ProductItemSubscription,
       Currency,
       BadBidder, Comment, PostMany, Tags,
       PostFlip, TagFlip, parent, child,
       another_parent1, another_parent2,
       Employee, Programmer, CoProgrammer, Marketing, Resource,
       Item, PolyParent, Poly, PolyChild1, PolyChild2
       )
