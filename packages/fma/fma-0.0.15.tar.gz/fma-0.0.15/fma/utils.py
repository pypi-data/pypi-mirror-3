
from antypes import ObjectId
import simplejson as json

__bool_type = ('true','false','1','0')



# taken from paste.deploy.converter
def asbool(obj):
    if isinstance(obj, (str, unicode)):
        obj = obj.strip().lower()
        if obj in ['true', 'yes', 'on', 'y', 't', '1']:
            return True
        elif obj in ['false', 'no', 'off', 'n', 'f', '0']:
            return False
        else:
            raise ValueError(
                "String is not true/false: %r" % obj)
    return bool(obj)
    
    
def type_converter(options):
    
    for k in options.keys():
        
        if options[k].lower() in __bool_type:
            options[k] = asbool(options[k])
            continue
        
        # jsonify it if possible
        jsonify_obj = None
        try:
            jsonify_obj = json.loads(options[k])
        except:
            pass
        
        if jsonify_obj:
            options[k] = jsonify_obj
        
    return options

def dump_config(configuration, prefix):
    '''Dump nilai pada konfigurasi file ini kedalam bentuk dict {}
    '''
    
    options = dict((x[len(prefix):],configuration[x]) for x in configuration if x.startswith(prefix))
    
    return type_converter(options)