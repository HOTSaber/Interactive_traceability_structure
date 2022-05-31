import json,time
import pandas as pd
import ipfshttpclient as ipfsapi
from io import BytesIO
from PIL import Image
def search_content(df):#只输入block中transactions的Dataframe格式，
    '''本function目标target_TxID格式为str,即只搜索一个target_TxID'''
    global result_list,block_index_list,target_TxID
    target_Tx = df.query('TxID == @target_TxID')  # 对dataframe进行查询操作
    if target_Tx.empty:  # 本区块没有找到目标Tx
        pass # 直接跳过，到更新block为前一个区块
    else:  # 找到了目标Tx
        result_list.append(target_Tx.to_dict(orient='records')[0])  # 保存查询结果
        block_index_list.append(block_index)  # 记录区块高度
        # print(type(target_Tx.to_dict(orient='records')[0]))
        '''
        orient参数列表
        - 'dict' (default) : dict like {column -> {index -> value}}
        - 'list' : dict like {column -> [values]}
        - 'series' : dict like {column -> Series(values)}
        - 'split' : dict like {'index' -> [index], 'columns' -> [columns], 'data' -> [values]}
        - 'records' : list like [{column -> value}, ... , {column -> value}]
        - 'index' : dict like {index -> {column -> value}}
        '''
        target_TxID = target_Tx.at[0, 'pre_TxID']  # 更新target_TxID为pre_TxID
        '''类似于 loc, 但仅取一个具体的值，结构为 at[<索引>,<列名>]：'''
def search_Tx(block_chain_list,first_pre_TxID):
    '''
    这里的输入就是jsondata,是生成算法生成的blockchain list
    first_preTxID是我们定义的交易链第一笔交易的pre_TxID值，我们定义的第一笔交易的pre_TxID是int 0
    '''
    global target_TxID,block_index,block_index_list,result_list
    while target_TxID != first_pre_TxID:
        block = block_chain_list.pop(-1)#取最后一个区块，有删除
        block_index = block['index']#当前区块高度
        Tx_data = block['transactions']#提取出区块中的transactions信息，是一个List，每个元素是一个Tx的dict
        df = pd.DataFrame(Tx_data)#将list转化为DataFrame格式，变成header是content,author,pre_TxID,CID,第行是一个Tx的df
        if isinstance(target_TxID,str):#当目标TxID只有一个时
            search_content(df)#跟据global variable:result_list,block_index_list,查询target_TxID {class:str}
        else:#当目标TxID是一个list时，将list进行拆分,即有多个target_TxID需要查询
            for content in target_TxID:
                search_content(df)#这里的content是一个str


##############################################  检索  ##################################################################
if __name__ == '__main__':
    api = ipfsapi.connect()
    size_lst = [200000,400000,600000,800000,1000000,1200000,1400000,1600000,1800000,2000000]
    # size_lst = [500000,1000000,1500000,2000000]
    new_col = ['local','total']
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
            target_TxID = f.read()
            f.close()
        time1 = time.time()
        '''第一次记录时间'''
        # target_TxID = '9c9865549a20d65fa8262e09a0df262236c196f65b87c5f94d93aa6d5688ef8f'
        block_index_list = []
        result_list = []
        search_Tx(jsondata,0)
        time2 = time.time()
        '''第二次记录时间'''
        df_result  = pd.DataFrame(result_list)
        df_result = df_result['CID'].tolist()
        pin1 =0
        for content in df_result:
            if isinstance(content,list):
                content = list(set(content))
                pin2 =0
                for content2 in content:
                    res = api.cat(content2)  # 向IPFS转出读取请求，非下载，此时返回的res为bytes格式
                    bytes_stream = BytesIO(res)  # 将bytes结果转化为字节流
                    raw_image = Image.open(bytes_stream)  # <class 'PIL.BmpImagePlugin.BmpImageFile'>转化为PIL.image对应格式
                    raw_image.save(f'{total_Tx_size}/J{total_Tx_size}_{chain_level - pin1}{pin2}.bmp')  # 保存文件，目前有5张图片
                    pin2 =+ 1
            else:
                res = api.cat(content)  # 向IPFS转出读取请求，非下载，此时返回的res为bytes格式
                bytes_stream = BytesIO(res)  # 将bytes结果转化为字节流
                raw_image = Image.open(bytes_stream)  # <class 'PIL.BmpImagePlugin.BmpImageFile'>转化为PIL.image对应格式
                raw_image.save(f'{total_Tx_size}/J{total_Tx_size}_{chain_level - pin1}.bmp')  # 保存文件，目前有5张图片
            pin1 +=1
        time3 = time.time()
        '''第三次记录时间'''
        # print(result_list)
        # print(block_index_list)
        print(f'{total_Tx_size}本地检索用时',time2-time1,'秒')
        print(f'{total_Tx_size}总检索用时',time3-time1,'秒')
        '''此时result_list与block_index_list都是倒序排序'''
    ############################################  保存结果 ##############################################################
        with open(f'{total_Tx_size}/{total_Tx_size}_chain_search_result.json','w',encoding='utf-8') as f:
            json.dump(result_list,f)
            f.close()
        with open(f'{total_Tx_size}/{total_Tx_size}_block_index_chainsearchresult.txt','w',encoding='utf-8') as f:
            f.writelines(str(block_index_list))
            f.close()
        local_search_timecost.append(time2-time1)
        total_search_timecost.append(time3-time1)
    ####################################################################################################################
    df1 = pd.DataFrame(local_search_timecost)
    df2 = pd.DataFrame(total_search_timecost)
    df = pd.concat([df1,df2],axis=1)
    df.columns=new_col
    print(df)
    df.to_csv('20W_200W_json_search_results.csv',index=None)
##############################################  test  ##################################################################
# df = pd.DataFrame(jsondata)
# print(type(df),df)
# # df.to_csv(r'D:\Users\aucnm\Desktop\Git\df.csv')
# print(type(df['transactions'][1]),df['transactions'][1])
# print(type(df['transactions'][1][0]),df['transactions'][1][0])
# print(type(df['transactions'][1][0]['TxID']),df['transactions'][1][0]['TxID'])
##############################################  test  ##################################################################
