import pandas as pd
import ipfshttpclient as ipfsapi
import json
from io import BytesIO
from PIL import Image
import time
'''
1.search_last_Tx #record last Tx info
2.decode_preimage_CID #record all image file pointer info
3.search target_Tx in ralated block #record all Tx info 
'''
def search_content(df,target_TxID):#只输入block中transactions的Dataframe格式，
    '''本function目标target_TxID格式为str,即只搜索一个target_TxID'''
    global result_list,block_index_list,CID_list,block_index,last_Tx_index
    target_Tx = df.query('TxID == @target_TxID')  # 对dataframe进行查询操作
    if target_Tx.empty:  # 本区块没有找到目标Tx
        return False# 判断是否找到，返回bool值
    else:  # 找到了目标Tx
        target_Tx = target_Tx.copy()#【】
        target_Tx.loc[:,'block_index']=[block_index]#在result中写上区块高度
        result_list.append(target_Tx.to_dict(orient='records')[0])  # 保存查询结果
        block_index_list.append(block_index)  # 记录区块高度
        CID_list.append(target_Tx.at[0,'CID'])#记录CID值
        last_Tx_index = block_index
        '''类似于 loc, 但仅取一个具体的值，结构为 at[<索引>,<列名>]：'''
        return True#找到了
        '''
        orient参数列表
        - 'dict' (default) : dict like {column -> {index -> value}}
        - 'list' : dict like {column -> [values]}
        - 'series' : dict like {column -> Series(values)}
        - 'split' : dict like {'index' -> [index], 'columns' -> [columns], 'data' -> [values]}
        - 'records' : list like [{column -> value}, ... , {column -> value}]
        - 'index' : dict like {index -> {column -> value}}
        '''
        # target_TxID = target_Tx.at[0, 'pre_TxID']
        '''只需判断在本块儿是否找到交易，不再更新target_TxID,因为在IPFS搜索中target_TxID由解码file而来，不需要递推'''
def search_last_Tx(target_TxID):
    global block_chain_list,block_index,result_list#block_chain_list是一个list,记录着blockchain的信息，每一个元素都是block的dict形式
    r = False
    while not r:
        block = block_chain_list.pop(-1)#取最后一个区块，有删除
        Tx_data = block['transactions']#提取出区块中的transactions信息，是一个List，每个元素是一个Tx的dict
        block_index = block['index']#当前区块高度
        df = pd.DataFrame(Tx_data)#将list转化为DataFrame格式，变成header是content,author,pre_TxID,CID,第行是一个Tx的df
        r = search_content(df,target_TxID)#result_list保存查询结果,block_index_list记录区块高度,CID_list记录CID值
def imaget_decode(im,bound1,bound2,bound3,bound4):#image_file,10,20,30,255
    width,height = im.size
    lst = []
    CID  = []
    TxID = []
    Index =[]
    start,green,blue = im.getpixel((0,0))
    for y in range(height):
        for x in range(width):
            red,green,blue = im.getpixel((x,y))
            if bound1<=red<=bound4:#tag在，CID值域内容
                if start == red:
                    index = (green<<8) + blue
                    lst.append(chr(index))
                else:#当tag出现变化时，start暂时还没有更新，使用start判断当前类别
                    if bound1<=start<bound2:
                        CID.append(''.join(lst))
                    elif bound2<=start<bound3:
                        TxID.append(''.join(lst))
                    else:
                        Index.append(''.join(lst))
                    lst =[]#清空lst
                    index = (green<<8) + blue
                    lst.append(chr(index))
                    start = red  # 在添加完内容后，更新start，进行下一个字段
            if red == bound4 :#结束
                result = {}
                result['pre_file_CID'] = CID
                result['pre_TxID'] = TxID
                result['pre_index'] = Index
                # result['pre_file_CID'] = CID[0] if len(CID) == 1 else CID
                # result['pre_TxID'] = TxID[0] if len(TxID) == 1 else TxID
                # result['pre_index'] = Index[0] if len(Index) == 1 else Index
                '''注意解码结果都是list,即使只有一个元素，result['pre_file_CID']都是{class:list}'''
                return result
def request_decode(target_CID,pin1,pin2):#只是解读当前CID对应文件的pointer，没有循环,pin1,pin2用于保存文件时的命名公式
    global total_Tx_size,CID_list,file_pointer_result
    res = api.cat(target_CID)#向IPFS转出读取请求，非下载，此时返回的res为bytes格式
    bytes_stream = BytesIO(res)#将bytes结果转化为字节流
    raw_image = Image.open(bytes_stream)#<class 'PIL.BmpImagePlugin.BmpImageFile'>转化为PIL.image对应格式
    raw_image.save(f'{total_Tx_size}/{total_Tx_size}_{chain_level-pin1}{pin2}.bmp')#保存文件，目前有5张图片
    all_dict = imaget_decode(raw_image,10,20,30,255)#{class: dict},pre_file_CID,pre_TxID,pre_index
    file_pointer_result.append(all_dict)#保存指针全部信息
    return all_dict
def request_Tx_position(first_CID):
    ''''
    first_CID是自己定义的第一个CID内容，这里我们是用的int 0,
    但是因为decode后全部CID都变为str，且都由list装载，故这里first_CID-->{class:list}:['0']
    '''
    global CID_list,file_pointer_result,block_index_list,Tx_position
    target_CID = CID_list[-1]
    while first_CID not in CID_list:
        pin1 = CID_list.index(target_CID)
        inside_lst = []
        if isinstance(target_CID,str):#target_TxID只有一个
            inside_lst2 = []
            pin2 = 1
            pointer_dict = request_decode(target_CID,pin1,pin2)#返回的pointer_dict是pointer decode后的所有信息。
            CID_list.append(pointer_dict['pre_file_CID'])#更新CID_list,只能用append保留list框
            inside_lst2.append(pointer_dict['pre_index'])  #
            inside_lst2.append(pointer_dict['pre_TxID'])
            inside_lst.append(inside_lst2)# 需要inside_lst2的框,保证一个个index与TxID对
        else:
            target_CID = list(set(target_CID))  # 去除list中的重复元素
            for content in target_CID:
                CID_lst2,inside_lst2 = [],[]
                pin2 = target_CID.index(content)+1
                pointer_dict = request_decode(content,pin1,pin2)  # 返回的pointer_dict是pointer decode后的所有信息。
                CID_lst2.extend(pointer_dict['pre_file_CID'])#,记录pre_file_CID,不保留list框，有CID_list2的框
                inside_lst2.append(pointer_dict['pre_index'])
                inside_lst2.append(pointer_dict['pre_TxID'])
                inside_lst.append(inside_lst2)  # 需要inside_lst2的框
            CID_lst2 = list(set(CID_lst2))#去除重复项
            CID_list.append(CID_lst2)#更新CID_list
        Tx_position.extend(inside_lst)#记录Tx_position

        target_CID = CID_list[-1]  # 更新target_CID
    return Tx_position
    '''
    这里返回的target_CID可能是str,即一个，也可以是一个list,即多个
    当循环结束时file_pointer_result填满，block_index_list填满，CID_list填满
    '''
        # print(CID_list)
def search_Tx(Tx_position):
    '''
    这里的输入就是Tx_position,是生成算法生成的index与Tx一一对应的list
    [[['7'], ['2e42f47b355a464eeda2b6872ebfab81f9534c74ab00071aba9680cd28734f0c']], [['5'], ['7230c1979873f2842f976f54cf25c90926b0727c200c928323430f97a99ee7a7']], [['5'], ['7230c1979873f2842f976f54cf25c90926b0727c200c928323430f97a99ee7a7']], [['3'], ['688b17937a6980e54f7dd6f16c1b74edbda1f035b8a163c40ba69df298faab60']], [['0'], ['0']]]
    '''
    global block_chain_list,block_index
    for content in Tx_position:#content:[['7'], ['2e42f47b355a464eeda2b6872ebfab81f9534c74ab00071aba9680cd28734f0c']]
        for index in content[0]:#读index,index:'7' {class:str}
            if index != '0':
                for target_TxID in content[-1]:#读TxID，TxID:'2e42f47b355a464eeda2b6872ebfab81f9534c74ab00071aba9680cd28734f0c' {class:str}
                    block = block_chain_list[int(index)]  # 取最相应的区块#转str为int
                    Tx_data = block['transactions']  # 提取出区块中的transactions信息，是一个List，每个元素是一个Tx的dict
                    block_index = block['index']  # 当前区块高度
                    df = pd.DataFrame(Tx_data)  # 将list转化为DataFrame格式，变成header是content,author,pre_TxID,CID,第行是一个Tx的df
                    r = search_content(df,target_TxID) #保存了查询结果result_list,记录了区块高度block_index_list,额外多写了CIDlist

if __name__ == '__main__':
    api = ipfsapi.connect()
    size_lst = [200000,400000,600000,800000,1000000,1200000,1400000,1600000,1800000,2000000]
    # size_lst = [500000,1000000,1500000,2000000]
    new_col = ['local','total','lastTx']
    local_search_timecost = []
    total_search_timecost =[]
    lastTx_search_timecost = []
    for num in size_lst:
        total_Tx_size = num
        chain_level = 4
        with open(f'{total_Tx_size}/{total_Tx_size}_sim_BC_structure.json','r')as f :
            jsondata = json.load(f)
            f.close()
        with open(f'{total_Tx_size}/{total_Tx_size}_last_target_TxID.txt', 'r')as f:
            target_TxID = [f.read()]
            f.close()
        block_chain_list = jsondata
        # target_TxID = ['9c9865549a20d65fa8262e09a0df262236c196f65b87c5f94d93aa6d5688ef8f']
        '''注意target_Tx是一个list形式'''
        block_index_list = []#存储着result_list中对应的区块高度
        result_list = []#存储着target_Tx的full content
        Tx_position = []#存储着index与Tx_ID,的list对，｛class:list｝
        file_pointer_result = []#存储着所有decode出来的file_pointer full content
        CID_list=[]#用于IPFS_file的链式查询
        time1 = time.time()
        '''第一次记录时间'''
        search_last_Tx(target_TxID)##result_list保存查询结果,block_index_list记录区块高度,CID_list记录CID值
        time2 =time.time()
        '''第二次记录时间'''
        Tx_position = request_Tx_position(['0'])
        time3= time.time()
        '''第三次记录时间'''
        search_Tx(Tx_position)#保存了查询结果result_list,记录了区块高度block_index_list,额外多写了CIDlist
        time4 = time.time()
        '''第三次记录时间'''
        # print(result_list)
        # print(block_index_list)
        print(f'{total_Tx_size}总用时',time4-time1,'秒')
        print(f'{total_Tx_size}本地查询用时',time4-time3+time2-time1)
        print(f'{total_Tx_size}最后交易查询用时',time2-time1)
        local_search_timecost.append(time4-time3+time2-time1)
        total_search_timecost.append(time4-time1)
        lastTx_search_timecost.append(time2-time1)
        #############################################保存blockindexlist######################################################
        with open(f'{total_Tx_size}/{total_Tx_size}_block_index_searchresult.txt','w') as f:
            f.writelines(str(block_index_list))
            f.close()
        ##############################################保存查询结果############################################################
        with open(f'{total_Tx_size}/{total_Tx_size}_targetTx_searchresult.json','w') as f:
            json.dump(result_list,f)
            f.close()
        ##############################################保存总查询时间###########################################################
    df1 = pd.DataFrame(local_search_timecost)
    df2 = pd.DataFrame(total_search_timecost)
    df3 = pd.DataFrame(lastTx_search_timecost)
    df = pd.concat([df1,df2,df3],axis=1)
    df.columns=new_col
    print(df)
    df.to_csv('20W_200W_IPFS_search_results.csv',index=None)

