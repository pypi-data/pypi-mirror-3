# -*- coding: utf-8 -*-
import sys

from decorators import cached_property

SUBMODULE_OBJECTS = {
    # module : [objects],
    'pp': ['pp'],
    'daemon': ['Daemon'],
    'debug': ['Timer', 'progress', 'Progress', 'RePrint'],
    'decorators': ['cached_function', 'cached_property', 'cached_classmethod',
        'safely', 'replay', 'single_access'],
    'file': ['file'],
    'gthread': ['gthread'],
    'kv': ['KVBase', 'UKVBase', 'KV', 'KVObject'],
    'memory': ['MemoryTracker'],
    'send': ['send'],
    'structures': ['BigStringList'],
    'thread': ['thread'],
}

ALLOWED = {}
for mod, obj_list in SUBMODULE_OBJECTS.iteritems():
    for obj in obj_list:
        ALLOWED[obj] = mod


class OM(object):
    '''Auto-import'''

    @cached_property
    def goto(self):
        import goto
        return goto

    def __getattr__(self, name):
        try:
            mod_name = '%s.%s' % (__name__, ALLOWED[name])
            __import__(mod_name)
            mod = sys.modules[mod_name]
            ret = getattr(mod, name)
        except (KeyError, ImportError, AttributeError):
            raise AttributeError('om has no attribute %s' % name)
        setattr(self, name, ret)
        return ret


om = OM()
    
    
