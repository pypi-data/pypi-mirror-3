#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
KVBase (только строки) => KV (маршал) => OKV (объектные обёркти)

Скорость TC на записи строк:
=== tc ===
Запись 100000 строк: 0.11 s.
Чтение 100000 строк в случайном порядке: 0.14 s.
=== KVBase ===
Запись 100000 строк: 0.22 s.
Чтение 100000 строк в случайном порядке: 0.24 s.
=== KV ===
Запись 100000 строк: 0.33 s.
Чтение 100000 строк в случайном порядке: 0.32 s.
=== KVO ===
Запись 100000 строк: 0.33 s.
Чтение 100000 строк в случайном порядке: 0.64 s.
'''
import os
import marshal

def main():
    db = KVBase('var/test.tc', 'a+', 
        backup={'db_dir': 'var/backup/test.tc'}, compress=True)
    
    db['a'] = 'aaa'
    #~ db.restore_from_backup()
    #~ db.update_backup()
    print db['a']
    print db.backup_db['a']
    del db['a']
    
    return
    
    db = KVBase('var/test.tc', 'w')
    db['a'] = 'aaa'
    assert db['a'] == 'aaa'
    db.drop()

    db = KV('var/test.tc', 'w')
    db['a'] = {'a': 1}
    assert db['a']['a'] == 1
    db.drop()

    db = KVO('var/test.tc', 'w')
    db['a'] = {'a': 1}
    assert db['a'].a == 1
    db.drop()

    #~ speed_test(100000, 'var/test.tc')


def speed_test(row_count, db_fn):
    '''
    Тест скорости в режиме ключ-значение
    '''
    import random
    import om.t
    
    # данные для записи (ключ = значение)
    keys = [str(i) for i in xrange(row_count)]
    value = lambda key: key
    autocompress = 0

    for cls in [KVBase, UKVBase, KV, KVO]:
        print '=== %s ===' % cls.__name__
        
        # запись
        db = cls(db_fn, 'w', autocompress=autocompress)
        tm = om.t.T()
        for key in keys:
            db[key] = value(key)
        db.close()
        print 'Запись %s строк:' % len(keys), tm

        # чтение
        db = cls(db_fn, 'r', autocompress=autocompress)
        random.shuffle(keys)
        tm = om.t.T()
        for key in keys:
            val = db[key]
        db.close()
        print 'Чтение %s строк в случайном порядке:' % len(keys), tm
        print 'Размер базы:', db.size
        db.drop()


md = marshal.dumps
ml = marshal.loads


class KVBase(object):
    '''Работа со строками'''
    _opened = False
    
    def __init__(self, fn, mode='a+', db_type='tc', compress=False,
        autocompress=False, backup=None):
        '''
        *fn: файл
        **mode = режим открытия ('r', 'w', 'a', 'a+')
        **db_type: тип бд (tc, gdbm)
        **compress: сжимать данные
        **autocompress: сжимать данные если размер уменьшится
        **backup = {'db_dir': '/dir/name', **FSDBM_kwargs}
        '''
        self.fn = fn
        self.mode = mode
        self.db_type = db_type
        self._compress = compress
        if compress and db_type != 'tc':
            import zlib
            self.compress = lambda s: zlib.compress(s, 9)
            self.decompress = lambda s: zlib.decompress(s)
        elif autocompress:
            import zlib
            def compressor(s):
                compressed = zlib.compress(s, 9)
                if len(compressed) + 1 < len(s):
                    return '+' + compressed
                return '-' + s
            self.compress = compressor
            self.decompress = lambda s: (self.zlib.decompress(s[1:])
                if s.startswith('+') else s[1:])
        else:
            self.compress = lambda x: x
            self.decompress = lambda x: x
        self.backup = backup
        self.open()

    def open(self):
        dir = os.path.dirname(self.fn)
        if dir and not os.path.isdir(dir):
            os.makedirs(dir)
        if self.db_type == 'tc':
            import tc
            self.db = tc.HDB()
            if self._compress:
                self.db.tune(-1, -1, -1, tc.HDBTDEFLATE)
            self.db.open(self.fn, 
                {
                    'r': tc.HDBOREADER,
                    'w': tc.HDBOWRITER | tc.HDBOCREAT | tc.HDBOTRUNC,
                    'a': tc.HDBOWRITER,
                    'a+': tc.HDBOWRITER | tc.HDBOCREAT,
                }[self.mode]
            )
        elif self.db_type == 'gdbm':
            import gdbm
        else:
            assert 0, 'bad db type'
        if self.backup:
            import fsdbm
            self.backup_db = fsdbm.FSDBM(**self.backup)
        self._opened = True
    
    @property
    def size(self):
        return os.path.getsize(self.fn)

    def close(self):
        if self._opened:
            self.db.close()
        self._opened = False

    def drop(self):
        self.close()
        os.unlink(self.fn)
        if self.backup:
            self.backup_db.clear()
        
    def clear(self):
        self.drop()
        self.open()
    
    def __setitem__(self, key, value):
        self.db[key] = self.compress(value)
        if self.backup:
            self.backup_db[key] = value
        
    def __getitem__(self, key):
        return self.decompress(self.db[key])
        
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
            
    def __delitem__(self, key):
        del self.db[key]
        if self.backup:
            del self.backup_db[key]
        
    def __contains__(self, key):
        return key in self.db
        
    def __len__(self):
        return len(self.db)
        
    def __iter__(self):
        for k in self.db:
            yield k
    
    def iterkeys(self):
        return self.__iter__()
        
    def keys(self):
        return list(self)
        
    def itervalues(self):
        for k in self:
            yield self[k]

    def values(self):
        return list(self.itervalues())

    def iteritems(self):
        for k in self:
            yield (k, self[k])

    def items(self):
        return list(self.iteritems())

    def find(self, filter=None, order=None):
        '''
        Выборка документов
            **filter = lambda val: True|False
            **order = lambda val: True|False
        '''
        filter = filter or (lambda x: True)
        if order:
            items = [(k, order(v)) for k, v in self.iteritems() if filter(v)]
            items.sort(key=lambda x: x[1])
            return (self[k] for k, v in items)
        else:
            return (v for k, v in self.iteritems() if filter(v))

    def find_one(self, filter):
        for v in self.find(filter):
            return v
            
    def count(self, *args, **kwargs):
        '''
        Количество элементов по условию, параметры find
        '''
        i = 0
        for v in self.find(*args, **kwargs):
            i += 1
        return i
    
    def update_backup(self):
        '''Полностью обновить содержимое бэкапа'''
        if not self.backup:
            assert 0, 'backup db not found'
        self.backup_db.clear()
        for k, v in self.db.iteritems():
            self.backup_db[k] = v
    
    def restore_from_backup(self):
        '''Восстановить базу из бэкапа'''
        if not self.backup:
            assert 0, 'backup db not found'
        # clear db
        if self._opened:
            self.db.close()
        self._opened = False
        os.unlink(self.fn)
        self.open()
        for k, v in self.backup_db.iteritems():
            self.db[k] = v


class UKVBase(KVBase):
    '''Юникодные строки'''
    
    def __getitem__(self, key):
        return super(UKVBase, self).__getitem__(
            key.encode('utf-8')).decode('utf-8')
        
    def __setitem__(self, key, value):
        super(UKVBase, self).__setitem__(
            key.encode('utf-8'), value.encode('utf-8'))


class KV(KVBase):
    '''Маршализируемые данные'''
    
    def __getitem__(self, key):
        return ml(super(KV, self).__getitem__(key))
        
    def __setitem__(self, key, value):
        super(KV, self).__setitem__(key, md(value))


class ListDoc(list):
    def __init__(self, db, key, *args, **kwargs):
        super(ListDoc, self).__init__(*args, **kwargs)
        self._db = db
        self.key = key
        
    def save(self):
        self._db[self.key] = list(self)
        return self


class DictDoc(dict):
    def __init__(self, db, key, *args, **kwargs):
        super(DictDoc, self).__init__(*args, **kwargs)
        self.__dict__['_db'] = db
        self.__dict__['key'] = key
        
    def save(self):
        self._db[self.key] = dict(self)
        return self
        
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, val):
        self[name] = val

    def __delattr__(self, name):
        del self[name]


class KVObject(KV):
    '''Простенькие объектные обёртки на list и dict'''
    DOC_WRAPPERS = {dict: DictDoc, list: ListDoc}
    
    def doc_wrapper(self, key, obj):
        doc_cls = self.DOC_WRAPPERS.get(type(obj))
        return doc_cls(self, key, obj) if doc_cls else obj

    def __getitem__(self, key):
        ret = super(KVO, self).__getitem__(key)
        doc_cls = self.DOC_WRAPPERS.get(type(ret))
        if doc_cls:
            ret = doc_cls(self, key, ret)
        return ret
        


if __name__ == "__main__":
    main()
