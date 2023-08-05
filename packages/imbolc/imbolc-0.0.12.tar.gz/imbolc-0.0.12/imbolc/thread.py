# -*- coding: utf-8 -*-
'''
om_thread.py - многопоточный генератор
'''
import sys
import threading
import time
import Queue
import traceback

thread = sys.modules[__name__]  # for auto-import
END = object()  # стоп-значение для потока


def main():
    '''
    Пример использования
    '''
    import logging
    from imbolc import om
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')
    
    def tst(i):
        1/0
        print om.url.load('zenpad.ru').body[:10]
        print '-> %i' % i
        time.sleep(0.1)
        return '<- %i' % i
    
    # получаем результаты по ходу вычислений
    for s in run(tst, xrange(10), 3, err_logger=logging.error):
        print s
        
    #~ # если результаты не нужны
    #~ list(run(tst, xrange(100), 3))
        

def run(callback, tasks, thread_limit, queue_limit=None, err_logger=None,
        sleep=0.01):
    '''
    Многопоточный генератор, на вход:
        callback        - рабочая функция (или запускаемый объект)
        tasks           - задачи для callback, любой итерируемый тип
        thread_limit    - количество потоков
        queue_limit     - максимальный размер очереди заданий
        err_logger      - логгер ошибок, например logging.error
        sleep           - время сна в цикле (для уменьшения загрузки процессора)
    '''
    queue = Queue.Queue(queue_limit)
    tasks = iter(tasks)
    pool = []
    ret_queue = Queue.Queue()
    queue_limit = queue_limit if queue_limit else thread_limit * 5
    
    while True:
        # возвращаем результат
        while not ret_queue.empty():
            yield ret_queue.get()
                
        # проверяем работоспособность потоков
        pool = filter(lambda x: x.isAlive(), pool)

        # добавляем недостающие потоки
        while len(pool) < thread_limit:
            th = Th(callback, queue, ret_queue, err_logger)
            th.setDaemon(True)
            th.start()
            pool.append(th)
            
        # заполняем очередь заданий
        while queue.qsize() < queue_limit:
            try:
                task = tasks.next()
            except StopIteration:
                break
            queue.put(task)
        else:
            # задания ещё не кончились
            time.sleep(sleep)
            continue
        break
        
    # отключаем потоки
    for th in pool:
        queue.put(END)

    # ожидаем завершения потоков
    for th in pool:
        th.join()
    
    # отдаём остатки
    while not ret_queue.empty():
        yield ret_queue.get()


class Th(threading.Thread):
    '''
    Поток
    '''
    def __init__(self, callback, queue, ret_queue=None, err_logger=None):
        self.callback = callback
        self.queue = queue
        self.ret_queue = ret_queue
        self.err_logger = err_logger
        threading.Thread.__init__(self)
        
    def run(self):
        while True:
            args = self.queue.get()
            if args is END:
                break
            try:
                ret = self.callback(args)
            except Exception:
                if self.err_logger:
                    self.err_logger(''.join(
                        traceback.format_exception(*sys.exc_info())[1:]))
                raise
            if self.ret_queue:
                self.ret_queue.put(ret)


if __name__ == "__main__":
    main()
