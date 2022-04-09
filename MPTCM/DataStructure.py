import numpy as np
from threading import Thread
import Tools
import tqdm


class InfoCell:
    # InfoCell is the basic structure of a flow in GraphStream
    def __init__(self, from_index, to_index, weight):
        self.edge = (from_index, to_index)
        self.weight = weight


class brick:
    # the brick is a tree node,an array of bricks is a layer,several layers come to be a Slice and a pyramid is
    # consists of layers,pyramid projects in the y-axis is several slices.
    def __init__(self, dt, i):
        self.parent = -1  # parent = -1 means no parent now
        self.val = dt(0)
        self.Lflag = 0
        self.Rflag = 0
        self.id = i  # means its index of the Slice


class PyramidSlice:
    # use to manage the bricks in a pyramid slice
    def __init__(self, dt):
        # dt means the basic datatype of the whole Slice,bricks is a list consisted of several dict,they are used to
        # map bricks with their index,each dict means a layer of the pyramid-slice.
        self.bricks = []
        self.dt = dt
        self.height = -1
        # height = 0 means it is the first layer upper the basic layer

    def create_brick(self, dep, index):
        # Step 0:if the Slice now have the enough height,initialize a new brick and add it to the right height-dict with
        # it`s index.
        # Step 1:if the Slice now don`t have enough height,add a new dict and the height,then go Step 0.
        # Step 2:Every new brick must link to the parent and child already exist!
        # return the pointer to the new brick.
        if dep > self.height:
            self.bricks.append({})
            self.height = self.height + 1
        b = brick(self.dt, index)
        self.bricks[dep].update({index: b})
        try:
            # check if the parent exist
            p = self.bricks[dep + 1][int(index / 2)]
        except:
            return b
        else:
            b.parent = p
        try:
            # check if child exist
            lc = self.bricks[dep - 1][index * 2]
        except:
            return b
        else:
            lc.parent = b
        try:
            # check if child exist
            rc = self.bricks[dep - 1][index * 2 + 1]
        except:
            return b
        else:
            rc.parent = b

        return b

    def carry_over_base(self, x, dep):
        # the x is the position index of pre-layer,the dep is also the pre-layer`s depth
        # this function use to encounter the situation that basic layer happens Overflow.
        # Step 0:Find the mapped brick in the next layer,calculate the plus and turn the flag situation by the odd/even
        # of the x position of the pre-bricks.
        # Step 1:If the plus process happens a overflow as well,if the brick has already have a parent,then carry_over
        # to its parent.Or initialize a new brick as its parent and add the link between them,the another Child of the
        # new bricks should be linked as well.
        b = self.bricks[dep][int(x / 2)]
        t = b.val
        lr = x % 2
        if lr:
            b.Rflag = 1
        else:
            b.Lflag = 1
        t = self.dt(t + 1)
        if t < b.val:
            if type(b.parent) == brick:
                self.carry_over_brick(b.parent, dep+1)
            else:
                p = self.create_brick(dep + 1, int(b.id / 2))
                p.val = self.dt(1)
                if b.id % 2:
                    p.Rflag = 1
                else:
                    p.Lflag = 1
                b.parent = p
        b.val = t

    def carry_over_brick(self, b: brick, h):
        # Step 0: the position is exact.Calculate whether there is a carry over
        # Step 1: if no carry over happens,add the val and stop
        # Step 2: if carry over happens,judge if there is a parent,if not,create one and add val,else plus val directly.
        old_val = b.val
        b.val = self.dt(old_val + 1)
        dep = h
        if b.val < old_val:
            if b.parent != -1:
                self.carry_over_brick(b.parent, h+1)
            else:
                p = self.create_brick(dep + 1, int(b.id / 2))
                if b.id % 2:
                    p.Rflag = 1
                else:
                    p.Lflag = 1

    def step_back_base(self, x, dep):
        # the x is the position index of pre-layer,the dep is also the pre-layer`s depth
        # this function use to encounter the situation that base layer happens step_back and need to
        # subtract the first brick layer.
        # Step 0:we location the brick is by calculate index
        # Step 1:calculate the val of the brick,if steps back as well,find parent by link
        # Step 2:step_back_brick(parent)
        b = self.bricks[dep][int(x / 2)]
        old_val = b.val
        b.val = old_val - self.dt(1)
        if b.val > old_val:
            # means need step back
            try:
                self.step_back_brick(b.parent)
            except:
                print("Error:no parent to step back")

    def step_back_brick(self, b: brick):
        old_val = b.val
        b.val = old_val - self.dt(1)
        if b.val > old_val:
            # means need step back
            try:
                self.step_back_brick(b.parent)
            except:
                print("Error:no parent to step back")


class PyramidSketch(Thread):
    def __init__(self, sketch_id, w, stream, dt, s):
        # sketch_id is the index of the sketch.
        # hfunc_pair is the (hfunc,w) tuple
        # stream is the graph stream,a list of Infocell
        # dt means the basic datatype of the matrix,e.g np.uint8
        Thread.__init__(self)
        self.id = sketch_id
        self.gs = stream
        self.dt = dt
        self.w = w
        self.base_layer = np.zeros((w, w), dtype=dt)
        self.s = s
        # At first we initialize the base-layer and the first-layer.
        self.pyramid_proj = []
        print("No.%d Pyramid base start initializing" % self.id)
        for a in tqdm.tqdm(range(len(self.base_layer))):
            arr = self.base_layer[a]
            pyramid_slice = PyramidSlice(self.dt)
            for i in range(int(len(arr) / 2) + 1):
                # i = [0,w-1]
                b = pyramid_slice.create_brick(0, i)
                b.Lflag = -1
                b.Rflag = -1
                # -1 means this brick is on the base, it`s position should be calculated by the id
            self.pyramid_proj.append(pyramid_slice)
        print("No.%d Pyramid base has been initialized" % self.id)
        # print("The first layer of Pyramid Structure has been initialized,No.", self.id)

    def insert_edge(self, cell):
        # insert an edge,which is a entity of Infocell
        x, y = int(cell[0]), int(cell[1])
        val = self.dt(cell[2])
        # Step 0 :find the hashed position in the Base, e.g M[x][y]
        # Step 1 :let them plu,if outflow, let the outflow part go to the n-layer part
        old_val = self.base_layer[x][y]
        res = old_val + val
        if res < old_val:
            # print('Overflow in base')
            self.pyramid_proj[y].carry_over_base(x, 0)  # 此x为base中的x坐标

        self.base_layer[x][y] = res
        # end

    def delete_edge(self, delete_cell):
        # how to delete a edge
        x, y = int(delete_cell[0]), int(delete_cell[1])
        val = self.dt(delete_cell[2])
        # Step 0:find the hashed position in the Base layer,e.g M[x][y]
        # Step 1:let it subtract,if step_back,put the right val to M and use func step_back to let it run in the n-layer
        old_val = self.base_layer[x][y]
        res = old_val - val
        if res > old_val:
            self.pyramid_proj[y].step_back_base(x, 0)
        self.base_layer[x][y] = res

    def query_edge_base(self, edge):
        # use to query the weight of an edge
        # Step 0:get the position in the pyramid,then keep search their parent,if it is a brick,continue and add the val
        # to the list,if not,append 0
        x = edge[0]
        y = edge[1]
        val = [self.base_layer[x][y]]
        b_first = self.pyramid_proj[y].bricks[0][int(x / 2)]
        self.query_edge_brick(b_first, val, 0, int(x/2))
        return Tools.Fusing(val, self.s)

    def query_edge_brick(self, b, val, h, lr):
        if type(b) == int:
            return 0
        if type(b.parent) == brick:
            if lr % 2:
                if b.parent.Rflag == 1:
                    val.append(b.val)
                    self.query_edge_brick(b.parent, val, h + 1, int(lr/2))
                else:
                    val.append(b.val)
            else:
                if b.parent.Lflag == 1:
                    val.append(b.val)
                    self.query_edge_brick(b.parent, val, h + 1, int(lr/2))
                else:
                    val.append(b.val)

        else:
            val.append(b.val)
            return 0

    def run(self):
        # Inheritance from threading.Thread
        print('sketch %d start processing' % self.id)
        for cell in self.gs:
            self.insert_edge(cell)

    def print_M(self):
        # Use to print the matrix form data of the pyramid
        print('base layer\n', self.base_layer)
        print(self.base_layer.max())
        # print('The first brick layer')
        # for s in self.pyramid_proj:
        #     for r in s.bricks[0].values():
        #         print(r.val, end=" ")
        #     print(' ')

    def query_in_degree(self, x):
        sums = self.base_layer.sum(axis=0)
        x = int(x)
        lr = int(x / 2)
        val_base = [sums[x]]
        print(val_base)
        for sl in self.pyramid_proj:
            val_list_base = []
            b = sl.bricks[0][int(x/2)]
            val_list_base.append(b.val)
            while type(b.parent) == brick:
                if lr % 2:
                    if b.parent.Rflag == 1:
                        lr /= 2
                        b = b.parent
                        val_list_base.append(b.val)
                    else:
                        break
                else:
                    if b.parent.Lflag == 1:
                        lr /= 2
                        b = b.parent
                        val_list_base.append(b.val)
                    else:
                        break
            val_base.append(Tools.Fusing(val_list_base, self.s))
        res = 0
        for c in val_base:
            res += c
        return res

    def query_out_degree(self, x):
        sums = self.base_layer.sum(axis=1)
        val_base = [sums[x]]
        p_slice = self.pyramid_proj[x]
        val_base_list = []
        lr = int(x / 2)
        for b in p_slice.bricks[0].values():
            val_base_list.append(b.val)
            while type(b.parent) == brick:
                if lr % 2:
                    if b.parent.Rflag == 1:
                        lr = int(lr/2)
                        b = b.parent
                        val_base_list.append(b.val)
                    else:
                        break
                else:
                    if b.parent.Lflag == 1:
                        lr = int(lr/2)
                        b = b.parent
                        val_base_list.append(b.val)
                    else:
                        break
            val_base.append(Tools.Fusing(val_base_list, self.s))
        res = 0
        for c in val_base:
            res += c
        return res
