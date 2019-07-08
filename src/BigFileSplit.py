# -*- coding: utf-8 -*-
import os
def split_txt(filename, size):
    fp = open(filename, 'rb')
    i = 0
    n = 0
    temp = open(filename + '.part' + str(i), 'wb')
    buf = fp.read(1024)
    while (True):
        temp.write(buf)
        buf = fp.read(1024)
        if (buf == ''):
            print filename + '.part' + str(i) + ';'
            temp.close()
            fp.close()
            return
        n += 1
        if (n == size):
            n = 0
            print filename + '.part' + str(i) + ';'
            i += 1
            temp.close()
            temp = open(filename + '.part' + str(i), 'wb')


if __name__ == '__main__':
    # wenjian路径
    name = path = os.path.abspath('../datas/cars.csv')
    # 切割后每个文件的大小，单位KB
    size = 25000
    split_txt(name, size)