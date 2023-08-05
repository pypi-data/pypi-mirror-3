# -*- coding: utf-8 -*-
try:
    import json
except ImportError:
    import simplejson as json


def pp(obj, *args, **kwargs):
    '''pprint с раскодированым выводом русских строк'''
    def default(v):
        try:
            ret = str(v)
        except Exception:
            ret = 'not json serializable'
        if len(ret) > 50:
            ret = ret[:50] + ' ...'
        return ret
    print json.dumps(obj, ensure_ascii=False, indent=4,
        default=default).encode('utf-8')