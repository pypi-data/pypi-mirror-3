#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
from datetime import datetime, timedelta


def main():
    import logging
    from random import randint
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')

    rp = RePrint()
    for i in xrange(10):
        rp(u'мессага')
        time.sleep(0.1)
    rp.clear()
    
    for i in progress(xrange(10), logger=log.info):
        print i
        time.sleep(0.1)
        
    CNT = 10
    cnt = Progress(CNT, inline=True)
    for i in xrange(CNT):
        cnt.put(u'мессага' + ' ' + '.' * randint(1, 10))
        time.sleep(randint(1, 3) / 10.0)


class Timer(object):
    '''
    Таймер
    '''
    def __init__(self):
        self.start = time.time()
        
    def sec(self):
        return time.time() - self.start
    
    def __str__(self):
        return sec2str(self.sec())

def progress(objs, *args, **kwargs):
    '''
    Счётчик-генератор
    '''
    c = Progress(len(objs), *args, **kwargs)
    for obj in objs:
        c.put()
        yield obj

def sec2str(sec):
    '''
    Секунды в удобочитаемом вормате
    '''
    return '%2.2f s.' % sec if sec < 60 else str(
        timedelta(seconds=int(sec)))

class Progress(object):
    '''
    Счётчик
    '''

    def __init__(self, limit, step=None, start=1, inline=False, logger=None):
        self.limit = limit
        self.step = step if step else int(limit / 100) or 1
        self.cnt = start
        self.cnt_tpl = '%%(cnt_cur)%(cnt_len)si / %%(cnt_limit)%(cnt_len)si |%%(cnt_perc)3i%%%% | %%(time_step)8s | ~%%(time_left)8s | %%(speed)s/sec' % {
            'cnt_len' : len(str(limit))}
        self.tm = Timer()
        self.full_tm = Timer()
        self.logger = logger
        self.inline = not logger and inline
        self.last_msg_len = 0
        
    def log(self, msg):
        if self.logger:
            self.logger(msg)
        elif self.inline:
            if self.last_msg_len:
                #~ sys.stdout.write('\x08' * self.last_msg_len)
                sys.stdout.write('\x0D')
            sys.stdout.write(msg)
            overflow = self.last_msg_len - len(msg)
            if overflow > 0:
                sys.stdout.write(' ' * overflow)
            self.last_msg_len = len(msg)
        else:
            sys.stdout.write(msg)
            sys.stdout.write('\n')

    def put(self, msg=''):
        '''
        Выводит счётчик если пройдено нужное количество шагов
        Использование:
            if cnt.put('дополнительные данные, может быть функция'):
                # сделать что-то, если вывелся счётчик
                ...
        '''
        res = False
        if not self.cnt % self.step or self.cnt == self.limit:
            res = True
            cnt_perc = float(self.cnt) / self.limit
            time_full = self.full_tm.sec()
            time_left = sec2str((1.0 / cnt_perc) * time_full - time_full)
            #~ cur_step_cnt = self.step if not self.cnt % self.step else self.cnt - self.limit
            #~ speed = cur_step_cnt / self.tm.sec()
            speed = self.cnt / time_full
            speed = '%0.2f' % speed if speed < 10 else '%i' % speed
            m = self.cnt_tpl % {   
                'cnt_cur': self.cnt,
                'cnt_limit': self.limit,
                'cnt_perc': cnt_perc * 100,
                'time_step': self.tm,
                'time_left': time_left,
                'speed': speed,
            }
            self.tm = Timer()
            if msg:
                msg = msg() if hasattr(msg, '__call__') else unicode(msg)
                m += ' | %s' % msg
            if self.cnt == self.limit:
                m += ' | full time: %s' % self.full_tm
                if self.inline:
                    m = m + '\n'
            self.log(m)
            sys.stdout.flush()
        self.cnt += 1
        return res


class RePrint(object):
    def __init__(self, step=1, counter=True, timer=True, dots=True):
        self.step = step
        self.last_msg = ''
        self.counter = counter
        self.tm = Timer() if timer else None
        self.cnt = 0
        self.dots = dots
    
    def clear(self):
        if self.cnt:
            self.put(' ' * len(self.last_msg))
    
    def __call__(self, msg):
        self.cnt += 1
        if not self.cnt % self.step:
            if self.tm:
                msg = ' %s | %s' % (self.tm, msg) 
            if self.counter:
                msg = ' %3s | %s' % (self.cnt, msg)
            if self.dots:
                msg += ' ' + '.' * (self.cnt % 5)
            self.clear()
            self.put(msg)
        
    def put(self, msg):
        msg = msg.encode('utf-8') if isinstance(msg, unicode) else str(msg)
        sys.stdout.write(msg)
        sys.stdout.write('\x0D')
        sys.stdout.flush()
        self.last_msg = msg

if __name__ == '__main__':
    main()