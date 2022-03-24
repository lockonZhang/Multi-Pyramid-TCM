# 测试一下
import Tools
import DataStructure
import numpy as np


# Super Parameter：dt，w, s, n
class Attribute_Core:
    def __init__(self, stream_path, dt, s, w, n=1, hash_mode="classic"):
        # initialize the hash functions and them import the graph stream
        print('Working Core initialing...')
        self.hash_stack = []
        if hash_mode == "classic":
            self.hash_stack = Tools.GenerateIPHash(w, n)
        if hash_mode == "single hash":
            self.hash_stack = Tools.SingleHashGenerator(w, n)
        print('Hash functions get!')
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
        print("***the modify stage***")
        code_info = "insert:insert an edge in to the model\ndelete:delete an edg" \
                    "e from the model\nquit:exit to the pre page"
        code = None
        while code != "quit":
            print(code_info)
            code = input("please input the modify_code:\n")
            code_dic = {
                "insert": DataStructure.PyramidSketch.insert_edge,
                "delete": DataStructure.PyramidSketch.delete_edge
            }
            x = input("x:")
            y = input("y:")
            val = input("weight:")
            # recommend to deal with the time on the data stage
            # t = input("time")
            cell = DataStructure.InfoCell(x, y, val)
            for ske in self.TCM:
                code_dic[code](ske, cell)

    def search_on_TCM(self):
        print("***the query stage***")
        code_info = "edge: to query the weight of edge\ndegree:to query the in&out degree"
        code = "default"
        while code != "quit":
            print(code_info)
            code = input("please choose the search_code:\n")
            if code == "edge":
                x = input("x:")
                y = input("y:")
                val_list = []
                for ske in self.TCM:
                    x = ske.hfunc(int(x))
                    y = ske.hfunc(int(y))
                    loc = (x, y)
                    val = DataStructure.PyramidSketch.query_edge_base(ske, loc)
                    val_list.append(val)
                    # use min as the T_function
                print("the value of sketches", val_list, "\nthe final consequence", min(val_list))
            elif code == "quit":
                print('exit to pre level')
                break
            elif code == "degree":
                flag = -1
                while flag not in ["in", "out"]:
                    flag = input("in:In_Degree  while   out:Out_Degree")
                index = input("Please input the index:")

                if flag == "out":
                    degree_list = []
                    for ske in self.TCM:
                        index = ske.hfunc(int(index))
                        print(index, "index")
                        degree_list.append(int(ske.query_out_degree(index)))
                    print("the estimate degree is:", min(degree_list))
                    # Out degree searching
                    # search the M[][index] and sum the array
                elif flag == "in":
                    # search the M[index] and sum the array
                    degree_list = []
                    for ske in self.TCM:
                        index = ske.hfunc(int(index))
                        degree_list.append(int(ske.query_in_degree(index)))
                    print("the estimate degree is:", min(degree_list))
                else:
                    break
            else:
                continue


class OperatingSystem:
    def __init__(self, stream_path, dt, s, w, n, htype="classic"):
        self.op = -1
        self.core = Attribute_Core(stream_path, dt, s, w, n, htype)
        print("Warning:PLEASE INITIAL IT EVERT TIME YOU INPUT NEW STREAM")
        op_dic = {
            "initial": self.core.generating_sketch,
            "print": self.core.print_all,
            "modify": self.core.func_on_TCM,
            "query": self.core.search_on_TCM,
            "end": self.shut_system,
            "help": self.show_help
        }
        while self.op != "end":
            print("******Operation List******")
            for k in op_dic.keys():
                print("----", k, "----")
            # try:
            self.op = input("*****input the operation code*****\n")
            op_dic[self.op]()
            # except:
            print("Wrong operation code")
            continue

    def shut_system(self):
        print("System Closed")
        self.op = "end"
        return 0

    def show_help(self):
        print(
            "initial:Every time you import the data, you need to initial first,you can`t use other functions without "
            "initialization\n", "print:Print the basic layer of the Pyramid\n", "modify:Enter "
                                                                                "the page to do modify to your model\n",
            "query:Enter the query page to do queries\n", "end:shut down the system\n"

        )
