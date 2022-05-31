import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
from  matplotlib.ticker import FuncFormatter
import matplotlib.ticker as mtick
import pandas as pd
import numpy as np
import random
df1 = pd.read_csv('20W_200W_IPFS_search_results.csv')#header 'local','total','lastTx'
df2 = pd.read_csv('20W_200W_json_search_results.csv')#header 'local','total'
size = np.shape(df1)[0]
####################################  数据  ############################################################################
y1 = np.array(df1.iloc[:,0].tolist())
y2 = np.array(df1.iloc[:,1].tolist())
y3 = np.array(df1.iloc[:,2].tolist())
y21 = np.array(df2.iloc[:,0].tolist())
y22 = np.array(df2.iloc[:,1].tolist())
x = np.arange(1,size+1)
str1 = ('20','40','60','80','100','120','140','160','180','200')
# str2 = ('50','100','150','200')
# label_list = ('1','2','3','4','5','6','7','8','9','10')
# x[:] = [a-0.5 for a in x]
width = 0.5
#####################################  生成画布  ########################################################################
figsize = 11,9
figure = plt.figure(figsize=figsize)
ax1 = figure.add_subplot(1,1,1)#一行一列第一个位置
# ################################ 中文乱码的处理  #########################################################################
# plt.rcParams['font.sans-serif'] = ['SimHei']
####################################  字体设置  #########################################################################
font1 = {'family' : 'SimHei',#'Arial',#'Times New Roman',
'weight' : 'normal',
'size'   : 26,
}
font2 = {'family' : 'SimHei',#'Arial',#'Times New Roman',
'weight' : 'normal',
'size'   : 20,
}
########################################################################################################################
'''total time cost'''
plt.bar(x,y22,width=width, alpha = 1, align = 'center',color = '#ff7f0e', label = 'on-chain tracing',tick_label=str1,zorder = 100)#traversal algorithm,edgecolor = '#1e0037',tick_label = label_list)#黄色#alpha透明度
plt.bar(x, y2,width=width, alpha = 1, align = 'center',color = '#1f77b4',label = 'interactive tracing',zorder = 100)#,edgecolor = '#1e0037',tick_label = label_list)#黄色#alpha透明度
plt.plot(x,y2,'-r+',zorder = 101)#,label = 'Time cost of IPFS query algorithm'
plt.plot(x,y22,'-b+',zorder = 101)#,label = 'Time cost of sequential algorithm'
############################################  坐标轴名称  ################################################################
plt.xlabel('trading volume(10^4)',font1)
plt.ylabel('tracing time(s)',font1)
###################################  设置数轴数据  ##################################################################
plt.ylim([0,35])#y轴上下限
y_major_locator = MultipleLocator(5)# 创建y轴定位器，间隔5
ax1.yaxis.set_major_locator(y_major_locator)#手动设置x轴数据间隔
plt.grid(axis="y",linestyle='-.',zorder = 0)#生成网络线
plt.legend(loc = 'upper left',prop = font2)#绘制图例
'''zorder是绘图顺序，越小越先画，则图层在下'''
plt.tick_params(labelsize=22)#坐标轴刻度值属性设置
####################################### 为每个条形图添加数值标签############################################################
figure.tight_layout()
plt.show()
'''total/Local query time'''
#####################################  生成画布  ########################################################################
figsize = 11,9
figure = plt.figure(figsize=figsize)
ax1 = figure.add_subplot(1,1,1)#一行一列第一个位置
x = np.arange(1,20,2)
print(x)
plt.bar(x+width/2,y22,width=width, alpha = 1, color = '#f9622e',align = 'center', label = 'interact with IPFS under on-chain tracing',zorder = 100,edgecolor = '#1e0037')#traversal algorithm,edgecolor = '#1e0037',tick_label = label_list)#黄色#alpha透明度
plt.bar(x+width/2,y21,width=width, alpha = 1, color = '#1f77b4',align = 'center', label = 'full-node local retrieval under on-chain tracing',zorder = 100,edgecolor = '#1e0037')#traversal algorithm,edgecolor = '#1e0037',tick_label = label_list)#黄色#alpha透明度
plt.bar(x-width/2, y2,width=width, alpha = 1, color = '#ff7f0e', align = 'center',label = 'interact with IPFS under interactive tracing',zorder = 100,edgecolor = '#1e0037')#,edgecolor = '#1e0037',tick_label = label_list)#黄色#alpha透明度
plt.bar(x-width/2, y1,width=width, alpha = 1, color = '#5baefc', align = 'center',label = 'full-node local retrieval under interactive tracing',zorder = 100,edgecolor = '#1e0037')#,edgecolor = '#1e0037',tick_label = label_list)#黄色#alpha透明度
plt.plot(x,y2,'-+',color = '#ff7f0e',zorder = 101)#,label = '交互溯源时间消耗'
plt.plot(x,y22,'-r+',zorder = 101)#,label = '链上检索时间消耗'
plt.plot(x,y21,'-b+',zorder = 101)#,label = '链上检索本地检索用时'
plt.plot(x,y1,'-+', color = '#5baefc',zorder = 101)#,label = '交互溯源本地检索用时'
############################################  坐标轴名称  ################################################################
plt.xlabel('trading volume(10^4)',font1)
plt.ylabel('time cost(s)',font1)
###################################  设置数轴数据  ##################################################################

plt.ylim([0,35])#y轴上下限
y_major_locator = MultipleLocator(5)
ax1.yaxis.set_major_locator(y_major_locator)#手动设置x轴数据间隔
plt.xticks(x,['20', '40', '60', '80','100','120','140','160','180','200'])#手动设置x_label#, rotation=30, fontsize='small')
#############################################################################################################
plt.grid(axis="y",linestyle='-.',zorder = 0)#生成网络线
plt.legend(loc = 'upper left',prop = font2)#绘制图例
'''zorder是绘图顺序，越小越先画，则图层在下'''
plt.tick_params(labelsize=22)#坐标轴刻度值属性设置
figure.tight_layout()
plt.show()
'''local_time'''