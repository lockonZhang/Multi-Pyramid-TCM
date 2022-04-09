import numpy as np
import Tools
import seaborn as sns
import matplotlib.pyplot as plt
def tcm_core(stream_path, w):
    n = 1
    dt = np.uint32
    z = np.zeros((w,w), dtype=dt)
    graph_stream, l_stream = Tools.DBLPDataProcessor(stream_path)
    hpara = Tools.GenerateHashPara(w, n)
    for cell in graph_stream:
        # x = (int(hpara[0][0]) * int(cell[0]) + int(hpara[0][1])) % int(hpara[0][2])
        # y = (int(hpara[0][0]) * int(cell[1]) + int(hpara[0][1])) % int(hpara[0][2])
        x = (int(cell[0])*31  + 7 ) % 500
        y = (int(cell[1])*13  + 7 ) % 500
        # print(cell,x,y)
        z[x,y] += 1
    hphoto = sns.heatmap(z).invert_yaxis()
    plt.show()

tcm_core('/Users/cherudim/Desktop/DBLP/DBLPdata/1424953.txt'
         #'/Users/cherudim/Desktop/DBLP/DBLPdata/collaboration.txt'
          , 500)