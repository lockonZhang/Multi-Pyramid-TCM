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


def GenerateIPHash(w, n, range1=51, range2=100):
    # generate pairwise independent hash function,using the prime number
    # ax + b mod p, a,b,p are all prime numbers,p nears w,a in [range1+1,range2], b in [1,range1]
    # return a hash-function and it`s consequence range
    hash_functions = []
    al = pp.prime_range(range1 + 1, range2)
    bl = pp.prime_range(1, range1)
    pl = pp.prime_range(w - 30, w)
    for i in range(n):
        a = al[random.randint(0, len(al) - 1)]
        b = bl[random.randint(0, len(bl) - 1)]
        p = pl[random.randint(0, len(pl) - 1)]
        print("(", a, "x + ", b, ") mod", p)

        def hash_func(x):
            h = (a * x + b)
            return h

        hash_functions.append([hash_func, p])
    return hash_functions


def DBLPDataProcessor(path):
    f = open(path, 'r')
    print('Processing DBLP data stream')
    graph_stream = []  # 调度核心中存储的总图流
    l_stream = 0
    for e in f:
        if e == "\n":
            continue
        e = e.split(';')
        v = (e[0].split(',')[0], e[0].split(',')[1])
        cell = DataStructure.InfoCell(v[0], v[1], 1)
        graph_stream.append(cell)
        l_stream += 1
    f.close()
    return graph_stream, l_stream


def SingleHashGenerator(w, n, range1=51, range2=100):
    # these generator make n hash functions at ones with a faster speed
    hash_functions = []
    al = pp.prime_range(range1 + 1, range2)
    bl = pp.prime_range(1, range1)
    pl = pp.prime_range(w - 30, w)
    p = pl[-1]
    for i in range(n):
        a = al[random.randint(0, len(al) - 1)]
        b = bl[random.randint(0, len(bl) - 1)]
        p = pl[random.randint(0, len(pl) - 1)]

        def hash_func(x):
            h = (a * x + b)
            p1 = h >> 16
            p2 = h << i
            return (p1 ^ p2) % p

        hash_functions.append([hash_func, p])
    return hash_functions
