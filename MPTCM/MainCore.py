import Tools
import DataStructure
import time


# Super Parameter：dt，w, s, n
class Attribute_Core:
    def __init__(self, stream_path, dt, s, w, n, hash_mode="classic"):
        # initialize the hash functions and them import the graph stream
        print('Working Core initialing...')
        self.hash_stack = Tools.GenerateHashPara(w, n)
        print('Hash Parameters get!')
        self.TCM = []
        self.dt = dt
        self.s = s
        self.graph_stream, l_stream = Tools.DBLPDataProcessor(stream_path)
        self.sketch_counter = n
        self.mode = hash_mode
        print("Process Core initialization finish, len of stream:", l_stream)

    def generating_sketch(self):
        print("start generating sketches")
        t1 = time.time()
        w = 0
        if self.mode == "classic":
            for i in range(self.sketch_counter):
                gs = []
                for cell in self.graph_stream:
                    a, b, w = int(self.hash_stack[i][0]), int(self.hash_stack[i][1]), int(self.hash_stack[i][2])
                    hx = (int(cell[0]) * a + b) % w
                    hy = (int(cell[1]) * a + b) % w
                    val = int(cell[2])
                    # print(hx, hy)
                    gs.append((hx, hy, val))
                self.TCM.append(DataStructure.PyramidSketch(i, w, gs, self.dt, self.s))
            ht = time.time()
            for ske in self.TCM:
                ske.start()
            for ske in self.TCM:
                ske.join()
            print("finish generating sketch")
        if self.mode == "single_hash":
            print("Single Hashing!")
            cell_list = []
            for i in range(self.sketch_counter):
                cell_list.append([])
            for cell in self.graph_stream:
                a, b, w = int(self.hash_stack[0][0]), int(self.hash_stack[0][1]), int(self.hash_stack[0][2])
                hx = (int(cell[0]) * a + b) % w
                x1 = hx << 16
                hy = (int(cell[1]) * a + b) % w
                y1 = hy << 16
                for i in range(self.sketch_counter):
                    hx = hx << 1
                    gx = (x1 ^ hx) % w
                    gy = (y1 ^ hy) % w
                    cell_list[i].append((gx, gy, cell[2]))
            ht = time.time()
            for i in range(self.sketch_counter):
                self.TCM.append(DataStructure.PyramidSketch(i, w, cell_list[i], self.dt, self.s))
            for ske in self.TCM:
                ske.start()
            for ske in self.TCM:
                ske.join()
        print(time.time() - ht, ht - t1)

    def print_all(self):
        print("Now print the image")
        for ske in self.TCM:
            Tools.trans_pyramid2pillar(ske)

    def func_on_TCM(self):
        print("***the modify stage***")
        code_info = "insert:insert an edge in to the model\ndelete:delete an edg" \
                    "e from the model\nquit:exit to the pre page"
        code = None
        while code != "quit":
            print(code_info)
            code = input("please input the modify_code:\n")
            if code == "quit":
                break
            code_dic = {
                "insert": DataStructure.PyramidSketch.insert_edge,
                "delete": DataStructure.PyramidSketch.delete_edge
            }
            x = input("x:")
            y = input("y:")
            val = input("weight:")
            cell = (x, y, val)
            if self.mode == "classic":
                for i in range(self.sketch_counter):
                    a, b, w = int(self.hash_stack[i][0]), int(self.hash_stack[i][1]), int(self.hash_stack[i][2])
                    hx = (int(cell[0]) * a + b) % w
                    hy = (int(cell[1]) * a + b) % w
                    val = int(cell[2])

                    code_dic[code](self.TCM[i], (hx, hy, val))
            if self.mode == "single_hash":
                cell_list = []
                for i in range(self.sketch_counter):
                    cell_list.append([])
                a, b, w = int(self.hash_stack[0][0]), int(self.hash_stack[0][1]), int(self.hash_stack[0][2])
                hx = (int(cell[0]) * a + b) % w
                x1 = hx << 16
                hy = (int(cell[1]) * a + b) % w
                y1 = hy << 16
                for i in range(self.sketch_counter):
                    hx = hx << 1
                    gx = (x1 ^ hx) % w
                    gy = (y1 ^ hy) % w
                    code_dic[code](self.TCM[i], (gx, gy, cell[2]))

    def search_on_TCM(self):
        print("***the query stage***")
        code_info = "edge: to query the weight of edge\ndegree:to query the in&out degree"
        code = "default"
        while code != "quit":
            print(code_info)
            code = input("please choose the search_code:\n")
            if code == "edge":
                x = int(input("x:"))
                y = int(input("y:"))
                val_list = []
                if self.mode == "classic":
                    for i in range(self.sketch_counter):
                        a, b, w = int(self.hash_stack[i][0]), int(self.hash_stack[i][1]), int(self.hash_stack[i][2])
                        hx = (x * a + b) % w
                        hy = (y * a + b) % w
                        loc = (hx, hy)
                        # print(loc)
                        val = DataStructure.PyramidSketch.query_edge_base(self.TCM[i], loc)
                        val_list.append(val)
                        # use min as the T_function
                    print("the value of sketches", val_list, "\nthe final consequence", min(val_list))
                if self.mode == "single_hash":
                    cell_list = []
                    for i in range(self.sketch_counter):
                        cell_list.append([])
                    a, b, w = int(self.hash_stack[0][0]), int(self.hash_stack[0][1]), int(self.hash_stack[0][2])
                    hx = (int(x) * a + b) % w
                    x1 = hx << 16
                    hy = (int(y) * a + b) % w
                    y1 = hy << 16
                    for i in range(self.sketch_counter):
                        hx = hx << 1
                        gx = (x1 ^ hx) % w
                        gy = (y1 ^ hy) % w
                        loc = (gx, gy)
                        val = DataStructure.PyramidSketch.query_edge_base(self.TCM[i], loc)
                        val_list.append(val)
                    print("the value of sketches", val_list, "\nthe final consequence", min(val_list))

            elif code == "quit":
                print('exit to pre level')
                break
            elif code == "degree":
                flag = -1
                while flag not in ["in", "out"]:
                    flag = input("in:In_Degree  while   out:Out_Degree")
                index = int(input("Please input the index:"))
                if self.mode == "classic":
                    if flag == "out":
                        degree_list = []
                        for i in range(self.sketch_counter):
                            a, b, w = int(self.hash_stack[i][0]), int(self.hash_stack[i][1]), int(self.hash_stack[i][2])
                            index = (index * a + b) % w
                            degree_list.append(int(self.TCM[i].query_out_degree(index)))
                        print("the estimate degree is:", min(degree_list))
                        # Out degree searching
                        # search the M[][index] and sum the array
                    elif flag == "in":
                        # search the M[index] and sum the array
                        degree_list = []
                        for i in range(self.sketch_counter):
                            a, b, w = int(self.hash_stack[i][0]), int(self.hash_stack[i][1]), int(self.hash_stack[i][2])
                            index_x = (index * a + b) % w
                            print(index_x)
                            degree_list.append(int(self.TCM[i].query_in_degree(index_x)))
                        print("the estimate degree is:", min(degree_list))
                    else:
                        break
                if self.mode == "single_hash":
                    if flag == "out":
                        degree_list = []
                        cell_list = []
                        for i in range(self.sketch_counter):
                            cell_list.append([])
                        a, b, w = int(self.hash_stack[0][0]), int(self.hash_stack[0][1]), int(self.hash_stack[0][2])
                        h_index = (int(index) * a + b) % w
                        hx = h_index << 16
                        for i in range(self.sketch_counter):
                            hx = hx < 1
                            gx = (h_index ^ hx) % w
                            degree_list.append(int(self.TCM[i].query_out_degree(gx)))
                        print("the estimate degree is:", min(degree_list))
                    elif flag == "out":
                        degree_list = []
                        cell_list = []
                        for i in range(self.sketch_counter):
                            cell_list.append([])
                        a, b, w = int(self.hash_stack[0][0]), int(self.hash_stack[0][1]), int(self.hash_stack[0][2])
                        h_index_y = (int(index) * a + b) % w
                        hy = h_index_y << 16
                        for i in range(self.sketch_counter):
                            hy = hy << 1
                            gy = (h_index_y ^ hy) % w
                            degree_list.append(int(self.TCM[i].query_out_degree(gy)))
                        print("the estimate degree is:", min(degree_list))
            else:
                continue


def show_help():
    print(
        "initial:Every time you import the data, you need to initial first,you can`t use other functions without "
        "initialization\n", "print:Print the basic layer of the Pyramid\n", "modify:Enter "
                                                                            "the page to do modify to your model\n",
        "query:Enter the query page to do queries\n", "end:shut down the system\n"

    )


class OperatingSystem:
    def __init__(self, stream_path, dt, s, w, n, h_type="classic"):
        self.op = -1
        self.core = Attribute_Core(stream_path, dt, s, w, n, h_type)
        print("Warning:PLEASE INITIAL IT EVERT TIME YOU INPUT NEW STREAM")
        print("Mode:", self.core.mode)
        op_dic = {
            "initial": self.core.generating_sketch,
            "print": self.core.print_all,
            "modify": self.core.func_on_TCM,
            "query": self.core.search_on_TCM,
            "end": self.shut_system,
            "help": show_help,
            "hash": self.show_hash
        }
        while self.op != "end":
            print("******Operation List******")
            for k in op_dic.keys():
                print("----", k, "----")
            #try:
            self.op = input("*****input the operation code*****\n")
            op_dic[self.op]()
            #except:
                #print("Wrong operation code")
            #continue

    def shut_system(self):
        print("System Closed")
        self.op = "end"
        return 0

    def show_hash(self):
        print(self.core.hash_stack)
