#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Полезные декораторы '''
import os
import sys
import time
import traceback


def main():
    import logging
    
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')

    @safely(default='foo', logger=log.error)
    @replay(3, logger=log.info)
    def test():
        pass
        1 / 0
    
    print test()


def cached_function(func):
    '''
    Кешируемая функция
    '''
    def _func(*args, **kwargs):
        try:
            return _func._retval
        except AttributeError:
            _func._retval = func(*args, **kwargs)
            return _func._retval
    return _func


class cached_property(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, instance, owner):
        value = self.f(instance)
        setattr(instance, self.f.__name__, value)
        return value


class cached_classmethod(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, instance, owner):
        value = self.f(owner)
        setattr(owner, self.f.__name__, value)
        return value


def safely(default=None, logger=None):
    '''
    Декоратор, игнорируем исключения
        **default = значение возвращаемое при ошибке
        **logger = функция для логгинга трейсбэков (например logging.error)
    '''
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception, ex:
                if logger:
                    logger('SAFELY %s\n%s' %
                        (func.__name__, ''.join(traceback.format_exception(*sys.exc_info())[1:])))
                return default
        return wrapper
        wrapper.__name__ = func.__name__
    return decorator

def replay(cnt, sleep=0.1, logger=None):
    '''
    Декоратор, n-кратный перезапуск при исключении
        *cnt = сколько раз перезапускать
        **sleep = задержка между перезапусками, растёт с перезапусками
        **logger = функция для логгинга трейсбэков (например logging.debug)
    '''
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in xrange(cnt + 1):
                if i:
                    s = sleep * i
                    if logger:
                        logger('REPLAY %s (%i / %i), sleep %0.2f sec.\n%s' %
                            (func.__name__, i, cnt, s, ''.join(
                            traceback.format_exception(*sys.exc_info())[1:])))
                    if sleep:
                        time.sleep(s)
                try:
                    return func(*args, **kwargs)
                except Exception, e:
                    pass
            raise
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

def single_access(func=None, filename=None):
    '''
    Декоратор. Запускает, только если удаётся залочить файл.
    '''
    import file
    def decorator(func):
        lock_filename = filename or _func_loc_filename(func)
        def wrapper(*args, **kwargs):
            if file.lock(lock_filename):
                return func(*args, **kwargs)
            sys.stdout.write('Can\'t lock file: %s\n' % lock_filename)
        return wrapper
    if func:
        return decorator(func)
    else:
        return decorator

def _func_loc_filename(func):
    filename = sys.modules[func.__module__].__file__
    filename = os.path.abspath(filename)# + '.om.lock'
    return filename


if __name__ == "__main__":
    main()
