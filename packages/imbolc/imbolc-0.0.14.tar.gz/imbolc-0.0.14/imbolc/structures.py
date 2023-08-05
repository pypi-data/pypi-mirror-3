# -*- coding: utf-8 -*-
import array


def main():
    import random
    
    a = BigStringList()
    a.append('Утол')
    a.append('Мар')
    print len(a)
    print a[1]
    print random.choice(a)


class BigStringList(object):
    '''
    Экономичный к памяти список строк
    Использование:
        a = BigStringList()
        a.append('Утол')
        a.append('Мар')
        print len(a)
        print a[1]
        print random.choice(a)
    '''
    def __init__(self):
        self.data = array.array('c')
        self.index = array.array('L')
    
    def append(self, s):
        self.index.append(len(self.data))
        self.data.fromstring(s)
        
    def __getitem__(self, id):
        start = self.index[id]
        try:
            end = self.index[id + 1]
        except IndexError:
            end = len(self.data)
        return self.data[start:end].tostring()
        
    def __len__(self):
        return len(self.index)


if __name__ == "__main__":
    main()
