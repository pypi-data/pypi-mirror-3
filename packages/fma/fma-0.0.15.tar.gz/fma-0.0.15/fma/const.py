from pymongo.objectid import ObjectId
import datetime, time
from antypes import Binary, options
import types

allowed_data_types = [list, dict, str, unicode, int, long, float,
                      time.struct_time, datetime.time, datetime.date, datetime.datetime, bool,
                      Binary, options, types.NoneType, ObjectId]

relation_reserved_words = ('_parent_class','listmode','_type',
                           '_keyrel','rel_class','_cond','_order','_pk',
                           '_cascade','_backref','_old_hash','_post_save','_internal_params',
                           '_current_hash','_rel_class_name','_polymorphic','get_direct_object',
                           '_relation__dirty','__dirty','_memoized_method_caches','_sanitized__'
                           )
superdoc_reserved_words = ('_monga','_id','_metaname_','_echo','_pending_ops','_current_datas','_memoized_method_caches')
restrict_attribute_names = ('_data','_type')