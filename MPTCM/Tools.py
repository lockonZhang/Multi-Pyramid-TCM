import numpy as np
import pyunit_prime as pp
import random
import DataStructure


def Cutting(x: int, dt, s):
    # x is the input ; dt:basic datatype ;s byte len of dt
    # this function can cut x in a series number in the format of dt,and put them in a list to return
    result = []
    z = dt(1 * pow(2, s) - 1)  # 255 when dt==uint8
    while x != 0:
        t = dt(np.bitwise_and(z, x))
        result.append(t)
        x = dt(np.right_shift(x, s))
    return result


def Fusing(data_list, s):
    # this function is the reverse of function:Cutting,it can put the data list
    # with type of dt back to py.int and return it
    z = 1  # 255 when dt==uint8
    f = 1 * pow(2, s)
    val = 0
    for i in range(len(data_list)):
        val += z * data_list[i]
        z = z * f
    return val


def GenerateIPHash(w, range1=51, range2=100):
    # generate pairwise independent hash function,using the prime number
    # ax + b mod p, a,b,p are all prime numbers,p nears w,a in [range1+1,range2], b in [1,range1]
    # return a hash-function and it`s consequence range
    a = random.randint(range1 + 1, range2)
    b = random.randint(1, range1)
    pl = pp.prime_range(w - 20, w + 20)
    p = pl[int(len(pl) / 2)]
    print(a, b, p)

    def hash_func(x):
        return (a * x + b) % p

    return hash_func, p


def DBLPDataProcessor(path):
    f = open(path, 'r')
    print('get DBLP data stream')
    graph_stream = []  # 调度核心中存储的总图流
    l_stream = 0
    for e in f:
        if e == "\n":
            continue
        e = e.split(';')
        tmp = e[1]
        v = (e[0].split(',')[0], e[0].split(',')[1])
        cell = DataStructure.InfoCell(v[0], v[1], 1, tmp)
        graph_stream.append(cell)
        l_stream += 1
    f.close()
    return graph_stream, l_stream
