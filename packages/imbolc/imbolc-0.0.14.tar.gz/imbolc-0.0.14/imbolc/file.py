#!/usr/bin/python
# -*- coding: utf-8 -*-
''' Файлы '''

import os
import sys
import random
import shutil
import tempfile


file = sys.modules[__name__]  # for auto-import

def main():
    import om.t
    import time
    
    #~ d = JsonDict('var/tst.json')
    #~ return
    
    #~ CNT = 1024 * 300
    #~ fn = 'var/tst/num_%i.txt' % CNT
    #~ fn = '/media/squash/num_%i.txt' % CNT
    #~ s = 'a' * 1024 + '\n'
    
    #~ cnt = om.t.Cnt(CNT)
    #~ f = open(fn, 'w')
    #~ for i in xrange(CNT):
        #~ f.write(s)
    #~ f.close()
    #~ f = NumIndex(fn)
    #~ f.index()
    
    #~ time.sleep(3)
    #~ f = NumIndex(fn)
    #~ tm = om.t.T()
    #~ for i in xrange(1000):
        #~ f.get_rnd()
        #~ f.fast_rnd_list(100)
    #~ print '%sМ %s' % (CNT / 1024, tm)


    fns = list(dir_fns('.', rec=-1, filter=[
        'isfile',
        #~ 'isdir',
        ]))
    print len(fns)
    print '\n'.join('%5s %s' % (os.path.isfile(fn), fn) for fn in fns)




def lock(filename):
    '''
    Пытается открыть файл в режиме 'r+' и залочить.
    Возвращает файл, если получилось
    '''
    import fcntl
    if not hasattr(lock, '_files'):
        lock._files = {}
    try:
        if not os.path.isfile(filename):
            open(filename, 'w').close()
        file = open(filename, 'r+')
        fcntl.flock(file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError, ex:
        if ex[0] != 11:
            raise
        return None
    lock._files[filename] = file
    return file

    
def dir_fns(dir, rec=0, filter=None):
    '''
    Все файлы папки
        *dir - папка
        **rec - уровень рекурсивного обхода вложенных папок, -1 = бесконечно
        **filter - что возвращать: ['isfile', 'isdir', 'islink', 'ismount']
    '''
    filter = filter or ['isfile']
    dirs = []
    for fn in os.listdir(dir):
        full_fn = os.path.join(dir, fn)
        if os.path.isdir(full_fn):
            dirs.append(full_fn)
        for el in filter:
            if getattr(os.path, el)(full_fn):
                yield full_fn
                break
    if rec:
        for dir in dirs:
            for fn in dir_fns(dir, rec-1, filter):
                yield fn


class NumIndex(object):
    ''' 
        Огромный спиок строк хранимый в текстовом файле.
        Поддерживает доступ к строке по номеру.
    '''
    
    def __init__(self, fn):
        self.fn = fn
        self.f = open(fn)
        self.ind_len = len(str(os.stat(self.fn)[6]))  # длина индекса
        self.fn_ind = os.path.abspath(fn) + '.om.num.index'
        try:
            self.f_ind = open(self.fn_ind)
            self.count = os.path.getsize(self.fn_ind) / self.ind_len - 1
        except:
            self.count = 0
    
    def index(self):
        '''
        Индексируем файл
        '''
        import tempfile
        
        f_ind = open(tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(self.fn_ind)))[1], 'w')
        self.f.seek(0)

        while True:
            f_ind.write(('%%0%dd' % self.ind_len) % self.f.tell())
            s = self.f.readline()
            if not s:
                break
        f_ind.close()

        os.rename(f_ind.name, self.fn_ind)
        
        self.f_ind = open(self.fn_ind)
        self.count = os.path.getsize(self.fn_ind) / self.ind_len
        
    def get(self, n, cnt=1):
        '''
        Получаем строки начиная с заданой. Нумерация с нуля.
        '''
        if n >= self.count:
            return []

        self.f_ind.seek(n * self.ind_len)
        self.f.seek(int(self.f_ind.read(self.ind_len)))
        
        ret = []
        for i in xrange(cnt):
            s = self.f.readline()
            if not s:
                break
            ret.append(s.rstrip())

        if len(ret) != cnt:
            self.f.seek(0)
            for i in xrange(cnt - len(ret)):
                s = self.f.readline()
                if not s:
                    break
                ret.append(s.rstrip())
        return ret

    def get_rnd(self, cnt=1):
        '''
        Получаем случайные строки
        '''
        n = random.randint(0, self.count - 1)
        if cnt == 1:
            return self.get(n, cnt)[0]
        return self.get(n, cnt)[0]
        
    def fast_rnd_list(self, cnt, seeks=1):
        '''
        Быстрый список случайных строк
            seeks = количество случайных смещений
        '''
        block = cnt / seeks
        res = []
        for i in xrange(seeks):
            res.extend(self.get_rnd(block * 2))
        random.shuffle(res)
        return res[:cnt]


class SList(list):
    ''' 
        Список строк хранимый в текстовом файле.
        При сохранении элеметнов они приводятся к строке.
        Пустые строки при сохранении и загрузке игнорируются.
        Пробельные символы в начале и конце строки удаляются.
    '''
    
    def __init__(self, fn, *args, **kwargs):
        super(SList, self).__init__(*args, **kwargs)
        self.fn = fn
        try:
            self.load()
        except IOError:
            pass
            
    def unique(self):
        '''
        Уникализируем список
        '''
        seen = {} 
        new = [] 
        for item in self: 
            if item in seen: continue 
            seen[item] = 1 
            new.append(item) 
        self.clear().extend(new)
        return self

    def clear(self):
        '''
        Очищаем список
        '''
        del self[:]
        return self

    def load(self):
        '''
        Загружаем список из файла
        '''
        self.clear()
        f = open(self.fn)
        for s in f:
            s = s.strip()
            if not s:
                continue
            self.append(s)
        f.close()
        return self
        
    def save(self):
        '''
        Cохраняем список в файл построчно
        '''
        data = []
        for s in self:
            s = str(s).strip()
            if not s:
                continue
            data.append(s)
        safely_write(self.fn, '\n'.join(data))
        return self

    def append(self, val):
        super(SList, self).append(val)
        return self

    def extend(self, vals):
        super(SList, self).extend(vals)
        return self

    def remove(self, val):
        super(SList, self).remove(val)
        return self

    def reverse(self):
        super(SList, self).reverse()
        return self
        
    def decode(self, enc):
        for i in xrange(len(self)):
            self[i] = self[i].decode(enc)
        return self

    def encode(self, enc):
        for i in xrange(len(self)):
            self[i] = self[i].encode(enc)
        return self


class JsonDict(dict):
    ''' 
    Словарь хранимый в файле в виде json-дампа
        - строки в файле сохраняются в указанной кодировке
        - строковые ключи декодируются
        - при загрузке все строки декодируются
    '''
    def __init__(self, fn, enc='utf-8', *args, **kwargs):
        '''
            *fn - имя файла
            **enc - кодировка файла
        '''
        global json
        import simplejson as json
        
        super(JsonDict, self).__init__(*args, **kwargs)
        self.enc = enc
        self.fn = fn
        try:
            self.load()
        except IOError:
            pass
            
    def _u(self, s):
        if isinstance(s, str):
            s = s.decode(self.enc)
        return s
            
    def __getitem__(self, name):
        return super(JsonDict, self).__getitem__(self._u(name))

    def __setitem__(self, name, val):
        super(JsonDict, self).__setitem__(self._u(name), val)

    def __delitem__(self, name):
        super(JsonDict, self).__delitem__(self._u(name))

    def load(self):
        '''
        Загружаем список из файла
        '''
        self.clear()
        self.update(json.loads(open(self.fn).read().decode(self.enc)))
        return self

    def save(self):
        '''
        Cохраняем список в файл построчно
        '''
        safely_write(self.fn, str(self))
        return self
        
    def __str__(self):
        return json.dumps(dict(self), indent='\t', sort_keys=True,
            ensure_ascii=False).encode(self.enc)


def safely_write(fn, data, make_dirs=True):
    '''
    Безопасная запись в файл (с помощью ренейма)
        *fn - имя файла
        *data - данные для сохранения
    '''
    fd, tmp_fn = tempfile.mkstemp(dir='/tmp')
    tmp = os.fdopen(fd, 'w')
    tmp.write(data)
    tmp.close()
    try:
        shutil.move(tmp_fn, fn)
    except IOError, ex:
        if ex.errno == 2 and make_dirs:
            # создаём папки
            os.makedirs(os.path.dirname(fn))
            try:
                shutil.move(tmp_fn, fn)
            except IOError:
                os.unlink(tmp_fn)
                raise
        else:
            os.unlink(tmp_fn)
            raise

if __name__ == "__main__":
    main()
