# 测试一下
import Tools
import DataStructure
import numpy as np


# Super Parameter：dt，w, s, n
class Attribute_Core:
    def __init__(self, stream_path, dt, s, w, n=1):
        # initialize the hash functions and them import the graph stream
        print('initialing...')
        self.hash_stack = []
        for i in range(n):
            self.hash_stack.append(Tools.GenerateIPHash(w))
        print('get hash functions')
        self.TCM = []
        self.dt = dt
        self.s = s
        self.graph_stream, l_stream = Tools.DBLPDataProcessor(stream_path)
        self.sketch_counter = n
        print("Process Core initialization finish, len of stream:", l_stream)

    def generating_sketch(self):
        print("start generating sketches")
        for i in range(self.sketch_counter):
            self.TCM.append(DataStructure.PyramidSketch(i, self.hash_stack[i], self.graph_stream, self.dt, self.s))
        for ske in self.TCM:
            ske.start()
        for ske in self.TCM:
            ske.join()
        print("finish generating sketch")

    def print_all(self):
        print("Now print the image")
        for ske in self.TCM:
            ske.print_M()

    def func_on_TCM(self):
        code = input("please input the modify_code:\n")
        code_dic = {
            "insert": DataStructure.PyramidSketch.insert_edge,
            "delete": DataStructure.PyramidSketch.delete_edge
        }
        x = input("x")
        y = input("y")
        val = input("weight")
        t = input("time")
        cell = DataStructure.InfoCell(x, y, val, t)
        for ske in self.TCM:
            code_dic[code](ske, cell)

    def search_on_TCM(self):
        code_dic = {
            "edge": DataStructure.PyramidSketch.query_edge_base
        }
        code = input("please input the search_code:\n")
        x = input("x")
        y = input("y")
        val_list = []
        for ske in self.TCM:
            x = ske.hfunc(int(x))
            y = ske.hfunc(int(y))
            loc = (x, y)
            val = code_dic[code](ske, loc)
            print(ske.id, val)
            val_list.append(val)
            # use min as the T_function
        print(val_list, min(val_list))


class OperatingSystem:
    def __init__(self):
        self.op = -1
        print("*****choose super_para:*****")
        stream_path, dt, s, w, n = self.initial_choose()
        self.core = Attribute_Core(stream_path, dt, s, w, n)
        op_dic = {
            "end": self.shut_system,
            "start": self.core.generating_sketch,
            "print": self.core.print_all,
            "modify": self.core.func_on_TCM,
            "query": self.core.search_on_TCM
        }
        while self.op != "end":
            self.op = input("*****input the operation code*****\n")
            op_dic[self.op]()

    def shut_system(self):
        print("System Closed")
        self.op = "end"
        return 0

    @staticmethod
    def initial_choose():
        path_dic = {
            "1": '/Users/cherudim/Desktop/DBLP/DBLPdata/1424953.txt',
            "0": '/Users/cherudim/Desktop/DBLP/DBLPdata/blank.txt'
        }
        dt_dic = {
            "0": np.uint8
        }
        s_dic = {
            "0": 8
        }
        w_dic = {
            "0": 300,
            "1": 700
        }
        stream_path, dt, w, n = 1, 1, 1, 1
        state = 1
        while state:
            try:
                stream_path = path_dic[input(path_dic)]
                break
            except:
                continue
        while state:
            try:
                dt_index = input(dt_dic)
                dt = dt_dic[dt_index]

                break
            except:
                continue
        while state:
            try:
                w = w_dic[input(w_dic)]
                break
            except:
                continue
        while state:
            try:
                n = int(input("number of pyramid"))
                break
            except:
                continue
        s = s_dic[dt_index]
        return stream_path, dt, s, w, n


op = OperatingSystem()
