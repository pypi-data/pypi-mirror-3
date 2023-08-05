#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Испльзование:

from gevent import monkey; monkey.patch_all()
import om.gthread
import om.url

def print_head(host):
    print 'Starting %s' % host
    r = om.url.query(host)
    print '<-- %s: %s bytes: %r' % (host, len(r.body), r.body[:50])

urls = (h for h in ['www.google.com', 'www.yandex.ru', 'www.python.org', 'dev.pooqle.com'])
om.gthread.run(print_head, urls, 2)

'''
import gevent
from gevent.queue import JoinableQueue


gthread = sys.modules[__name__]  # for auto-import


def main():
    from gevent import monkey; monkey.patch_all()
    import om.url
    
    def print_head(host):
        print 'Starting %s' % host
        r = om.url.query(host)
        print '<-- %s: %s bytes: %r' % (host, len(r.body), r.body[:50])

    urls = ['www.google.com', 'www.yandex.ru', 'www.python.org', 'dev.pooqle.com']
    run(print_head, urls, 2)
    

def run(func, tasks, thread_limit):
    tasks = iter(tasks)
    queue = JoinableQueue()
    for i in xrange(thread_limit):
         gevent.spawn(worker, func, queue, tasks)
    queue.put(tasks.next())
    queue.join()  # block until all tasks are done


def worker(func, queue, tasks):
    while True:
        try:
            queue.put(tasks.next())
        except StopIteration:
            pass
        task = queue.get()
        try:
            func(task)
        finally:
            queue.task_done()


if __name__ == '__main__':
    main()
