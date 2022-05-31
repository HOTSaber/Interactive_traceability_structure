from hashlib import sha256
import json
import time
import random
import pandas as pd
import ipfshttpclient as ipfsapi  #导入python的IPFS接口
from PIL import Image

class Block:
    ##################################  class attribute  ###############################################################
    ################################  instance attribute  ##############################################################
    def __init__(self,index,transactions,timestamp,previous_hash,nonce=0):      #这里的self是指Block Class 下的一个instance
        self.index = index                                              #为Block下的instance添加attribute
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
    #####################################  计算instance hash  ###########################################################
    def compute_hash(self):                                             #为整个Block Class 下的所有instance添加function-compute_hash
        block_string = json.dumps(self.__dict__, sort_keys = True)        #这里的self也是Block Class 下的一个instance,即将一个block instance转为json格式
                                                                                #使用参数indent = 4 格式化字符串
        return sha256(block_string.encode()).hexdigest()                #再将json格式的block求hash,用十六进制表示

class BC:
    '''
    0.creat_genesis_block
    1.add_new_transaction
    2.mine(include the process of add block to the chain)
    '''
    ##################################  class attribute  ###############################################################
    minning_difficulty = 2
    ################################  instance attribute  #############################################################
    def __init__(self):     #这里的self是指 Blockchain
        self.unconfirmed_transactions = [] #未上链交易池
        self.chain = []
        # self.create_genesis_block()
    #########################################  新建创世纪块  #############################################################
    def create_genesis_block(self):
        genesis_block = Block(0,[],time.time(),0)   #Class Block下新增了一个instance genesis_block.
        genesis_block.hash = genesis_block.compute_hash()   #为instance genesis_block 添加 attribute hash
        self.chain.append(genesis_block)    #为self.chain = [] 中append第一个genesis_block
        global current_block_index
        current_block_index = 0                     #返回一个全局变量current_block_index,表示已上链的最后一个区块高度

    #########################################  返回最新区块  #############################################################
    @property                               #直接返回属性值不需要加括号，（调用属性方式）（加括号的是调用函数方式）
    def last_block(self):
        return self.chain[-1]               #返回倒数第一个区块
    #########################################  待上链块的工作量证明  #######################################################
    @staticmethod#静态方法调用无需实例化，但也可以实例化使用，即在proof_of_work函数中没有self
    def proof_of_work(block):
        block.nonce = 0                     #通过更改nonce解puzzle(找出开头有多少个0的特殊hash结果)
        compute_hash = block.compute_hash() #计算区块hash值，但注意这里是将整个Block本身作为输入，实际上Bitcoin中只是将Block_header作为输入，Block_header与Block_body之间由merkel_tree连接
        while not compute_hash.startswith('0' * BC.minning_difficulty): #逻辑为当hash结果开头不是以minning_difficulty个0开头时，就更改nonce重新计算
            block.nonce += 1                #这里的nonce是instance的
            compute_hash = block.compute_hash()
        return compute_hash
    #########################################  待上链块上链  #############################################################
    def add_block(self,block,proof):        #这里的self是指的此class——Blockchain
        previous_hash = self.last_block.hash #这里为什么写的是hash，answer:在5行后由block.hash = proof在Blockchain上add新区块时，为每一个instance添加attribute_hash
        if previous_hash !=block.previous_hash:
            return False
        if not BC.is_valid_proof(block, proof):#func is_valid_proof在后面定义
            return False
        block.hash = proof                  #attribute hash是在此时添加的。前一个区块added后，后一个区块在add时调用前一区块attribute—hash.
                                            #proof是传递进来的，即proof_of_work函数的返回值compute_hash
        self.chain.append(block)
        global current_block_index
        current_block_index += 1
        return True                         #【三个return是怎么处理的】
    #########################################  工作量证明验证  ############################################################
    @classmethod#表示这是一个类方法，区别于平时的实例方法，第一个参数为cls,调用时用BC.is_valid_proof
    def is_valid_proof(cls,block,block_hash):
        return (block_hash.startswith('0' * BC.minning_difficulty) and block_hash == block.compute_hash())#括号中是两个判断，都为True时返回True
    #########################################  为待处理交易池添加新交易  ####################################################
    def add_new_transactions(self,transaction):
        self.unconfirmed_transactions.append(transaction)
    #########################################  待处理交易池打包——出块  #####################################################
    def mine(self):
        if not self.unconfirmed_transactions:   #【当unconfirmed_transactions是空时，会返回False?】
            print('no transaction to mine')
            return False
        last_block = self.last_block
        new_block = Block(index=last_block.index+1,
                          transactions = self.unconfirmed_transactions,
                          timestamp= time.time(),
                          previous_hash=last_block.hash)    #此时没有nonce，在计算此块POW时添加并修改instance的nonce
        proof = self.proof_of_work(new_block)               #计算POW
        self.add_block(new_block,proof)
        self.unconfirmed_transactions = []                  #清空待处理交易池
        return True

class Tx:
    '''定义Tx类的instance attribute
    {author,content,pre_TxID,TxID}'''
    def __init__(self, content,author):
        self.content = content
        self.author = author
    def compute_pre_TxID(self,pre_TxID):
        self.pre_TxID = pre_TxID
    # def create_genesis_block(self):
    #     self.pre_TxID = 0
    def IPFS_CID(self):     #写入指向IPFS系统中对应文件的CID
        pass
    def compute_TxID(self):     #对于紧后交易来说就是pre_TxID
        TX_string = json.dumps(self.__dict__,sort_keys=True)
        self.TxID = sha256(TX_string.encode()).hexdigest()
        # return self.TxID

def compute_target_value(max,min,num):#max为上限，min为下限,num为生成几个数
    """随机生成递增数组"""
    min,max = (int(min),int(max)) if max>=min else (int(max),int(min))#防止填反函数
    n = 0
    target_list = []
    while n<num:
        n += 1
        target = random.randint(min+1,min+int(max/num)-1)
        target_list.append(target)
        min = min+int(max/num)
    return target_list
def encode(tag_list, file_pointer, file_name):# tag_list is a list ,and file_pointer is a list too,length相同,这里file name是一个str
    im=Image.open(f'Raw image\\{file_name}.jpg')
    """
        在python中,路径可以接受“/”“\”，这里形象的比喻成撇和捺。但是由于“\”在python中是作为转义符使用，所以在路径中使用“\”时，要写成“\\”。

        因此在python中，下面这两种写法都是可以接受的。
        "c:/test/my doc"
        "c:\\test\\my doc"
    """
    global total_Tx_size
    (w,h) = im.size
    #width = math.ceil(str_len ** 0.5)
    #im = Image.new('RGB', (width, width), 0x0) #新建图像
    x, y = 0, 0
    num = 0
    for text in file_pointer:
        for i in str(text):
            index = ord(i)
            rgb = (tag_list[num], (index & 0xFF00) >>8, index & 0xFF) #& 0xff与 & 0xff00的作用：
            '''
            0xff00中：
            0x表示4位16进制数
            有：
            0x —— 16进制
            0o ——8进制
            0b ——2进制
            0 1 2 3 4 5 6 7 8 9  a  b  c  d  e  f
                                 10 11 12 13 14 15
            f=1111=2^3+2^2+2^2+2^0=8+4+2+1=15
            0=0000=0
            则有0xff00=1111 1111 0000 0000  #为16位2进制数，表示为4位16进制数
            &为位操作符，位操作符共有：
            与        &    ——两一得一，否则为0
            或        |    ——有一得一，两0得0
            异或      ^    ——不同为1，相同为0
            取反      ~    ——1变0，0变1
            左位移     <<  ——右跟左移的位数
            右位移     >>  ——同上 
            因为采用ord()与chr()函数，转换标准为unicode,uincode将世界上所有的文字用2进制编码统一编制
            所有unicode用数字0-0x10FFFF来映射这些字符，最多可以容纳1114112个字符
            '''
            im.putpixel((x, y), rgb)
            if x == w - 1:#写满一行后，换一行
                x = 0
                y += 1
            else:#未写满一行，写下一格
                x += 1
        num += 1
    im.putpixel((x, y), (255,0,0))#写一个结束位
    im.save(f'Image evidence\\{total_Tx_size}_{file_name}.bmp')
    # return im
def decode(im,bound1,bound2,bound3,bound4):#image_file,10,20,30,255

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
                return result
def generate_random_transaction():
    """random_str_list 是一串字符串，在其中随机抽取字符，str
    random_str_len是生成多长的随机字符串,int
    random_author_list是名称列表，在此列表中随机选择名称作为交易发起人，
    random transaction是没有pre_TxID的，用0代替"""
    global random_str_list,random_str_len,random_author_list
    random_string = ''.join((random.sample(random_str_list, random_str_len)))#生成随机字符串
    random_author = random.choice(random_author_list) #生成随机名称
    test_Tx = Tx(random_string, random_author)
    test_Tx.compute_pre_TxID(0)
    test_Tx.compute_TxID()
    test_Tx.CID = 0          #没有在IPFS上存储文件
    return test_Tx
def generate_target_transaction():
    '''
    生成有pin的transaction，作为后续查询算法的目标
    target transaction是有链式结构的
    在此function中只是生成target_Tx的content,author,pre_TxID的内容
    区分了交易链头与后续交易，即有无pre_TxID
    '''
    global pin, target_value, pre_TxID_pool, random_str_list, random_str_len, random_author_list
    random_string = ''.join((random.sample(random_str_list, random_str_len)))
    random_author = random.choice(random_author_list)
    test_Tx = Tx(random_string + pin, random_author)
    if current_block_index == target_value[0]:
        test_Tx.compute_pre_TxID(0)
    else:
        test_Tx.compute_pre_TxID(pre_TxID_pool[-1])
    return test_Tx
def generate_image(tag_list, file_pointer, file_name):#file name可以List，即一个Tx有多个文件,也可是一个str
    if isinstance(file_name,str):#当file name 是str时,Tx对应只有一个文件
        encode(tag_list,file_pointer,file_name)
    else:                       #当file name 是list时,Tx对应有多具文件，需要将他们都进行加密
        for content in file_name:
            encode(tag_list,file_pointer,content)#
def request_CID(file_name):#向IPFS发出文件，并将返回的CID写入test_Tx的CID attribute
    #保存路径f'D:/go-ipfs/{total_Tx_size}_{image_file_name[0]}.bmp'
    global test_Tx,total_Tx_size
    if isinstance(file_name,str):#当file name 是str时,Tx对应只有一个文件
        res = api.add(f'Image evidence\\{total_Tx_size}_{file_name}.bmp').as_json()  # 反回的是response格式，需要转换,经过as_json转换后res为dict
        test_Tx.CID = res['Hash']
    else:                       #当file name 是list时,Tx对应有多具文件，需要将他们都进行加密
        test_Tx.CID = []
        for content in file_name:
            res = api.add(f'Image evidence\\{total_Tx_size}_{content}.bmp').as_json()  # 反回的是response格式，需要转换,经过as_json转换后res为dict
            test_Tx.CID.append(res['Hash'])
def write_pre_CID(tag_start_num):#指CID字符的tag标记阈值
    global file_pointer,tag,pre_CID_pool
    #加入判断是否是list
    if isinstance(pre_CID_pool[0],list):#如果是多项的话，会是list嵌套
        num = 0
        for content in pre_CID_pool[0]:#去list嵌套[[,,]]
            file_pointer.append(content)
            tag.append(tag_start_num+num)
            num+=1
        pre_CID_pool= []
    else:
        file_pointer.append(pre_CID_pool.pop(-1))
        tag.append(tag_start_num)
def write_pre_TxID(tag_start_num):
    global file_pointer,tag,pre_TxID_pool
    if isinstance(pre_TxID_pool[0],list):#如果是多项的话，会是list嵌套
        num = 0
        for content in pre_TxID_pool[0]:#去list嵌套
            file_pointer.append(content)
            tag.append(tag_start_num+num)
            num+=1
        pre_TxID_pool = []
    else:
        file_pointer.append(pre_TxID_pool.pop(-1))
        tag.append(tag_start_num)
def write_pre_index(tag_start_num):
        global file_pointer,tag,pre_block_index
        if isinstance(pre_block_index[0],list):#如果是多项的话，会是list嵌套
            num = 0
            for content in pre_block_index[0]:
                file_pointer.append(content)
                tag.append(tag_start_num+num)
                num+=1
            pre_block_index = []
        else:
            file_pointer.append(pre_block_index.pop(-1))
            tag.append(tag_start_num)

#########################################  运行单节点区块链  ##############################################################
if __name__ == '__main__':
    '''请自行新建一个以total_Tx_size值为名称的文件夹，用以存储结果数据
        请提供基础图像文件，除图像文件外的信息为随机生成
        图像路径在function:encode与requese_CID中修改；图像名称请用list:image_file_name更改，是有结构的'''
###########################################  初始化区块链  ###############################################################
    num_list = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200]
    for num in num_list:
        blockchain = BC()
        blockchain.create_genesis_block()
        api = ipfsapi.connect()#需要在CMD先启动IPFS daemon,链接到IPFS
    #########################################  运行单节点区块链  ##############################################################
        random_str_list = 'abcdefghigklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        random_str_len =16
        random_author_list = ['Austin','Bob','Ju']
        pin = 'target'
        image_file_name = ['11','21',['31','32'],'41']
        max_pool_size = 200
        total_Tx_size = num*10000
        max_chain_length = total_Tx_size/max_pool_size #开头有一个genesis_block
        print('预计总链长度：',max_chain_length)
        chain_level = 4 #4#希望交易链有多少级
        pre_TxID_pool = []#应当编写查询功能
        pre_CID_pool = []#IPFS
        pre_block_index = []#IPFS
        result_pool = []#保存所有target_Tx 信息
        target_value = compute_target_value(1,max_chain_length,chain_level) #生成目标交易要插入的区块位置
        target_value[0]=22
        print('生成目标交易要插入的区块位置',target_value)
        '''定义随机交易内容、长度、查询目标交易标记戳，以及目标交易要插入的位置等参数'''
        pool_size = len(blockchain.unconfirmed_transactions)
        '''初始化unconfirmed_Tx= blockchain.unconfirmed_transactions,pool_size'''
        ########################################  生成块循环  ################################################################
        while current_block_index <= max_chain_length: #写到指定块长度停止
            '''
            1.generate random content and author——done
            2.target_Tx's pre_TxID——done
            3.write_file pointer——done
            4.interact with IPFS adn get CID——done
            5.compute tareget_Tx Hash as its TxID——done
            '''
            if current_block_index not in target_value: #待挖块内无target_Tx
                while pool_size < max_pool_size: #填满unconfirmed_transaction_pool,unconfirmed_Tx
                    test_Tx = generate_random_transaction() #生成random_transaction
                    blockchain.unconfirmed_transactions.append(test_Tx.__dict__) #将random_transaction 压入unconfirmed_Tx
                    pool_size = len(blockchain.unconfirmed_transactions) #更新pool_size
                print('当前写入进度',current_block_index)
            else:                       #待挖块内有target_Tx,有文件，需要修改图像pointer,需要与IPFS交互，得到CID
                test_Tx = generate_target_transaction()#生成target_Tx,有content,author,pre_TxID
            ###########################################  图像写入  ##########################################################
                if current_block_index == target_value[0]:#第一笔target_Tx
                    '''
                    current_block_index，不是指当前正在打包，而是目前链上最后区块的高度，但是区块高度是从0开始的
                    在genesis块中,有current_block_index = 0
                    在BC class 的 add_block function中有 current_block_index += 1
                    当target_value = 22 时，即当链上新块高度为22时开始打包目标交易，目标交易则被写入23块中
                    故在记录函数中有pre_block_index.append(current_block_index+1)
                    '''
                    file_pointer = [0, 0, 0]  # pre_file_CID,pre_block_index，pre_TxID，第一笔交易没有前置内容
                    tag = [10, 20, 30]  # 定义好各个内容的tag，这里可以有多个前文件、前交易、前区块，都采用一定值域，在<20为pre_file_CID,<30为pre_block_index
                                        # >30为pre_TxID,若为0则结束
                    generate_image(tag, file_pointer, image_file_name[0])#保存路径f'D:/go-ipfs/{total_Tx_size}_{image_file_name[0]}.bmp'
                else:#后续几笔target_Tx,有pre_file_CID,pre_TxID,pre_index
                    file_pointer = []
                    tag = []
                    write_pre_CID(10)# 定义好各个内容的tag，这里可以有多个前文件、前交易、前区块，都采用一定值域，在<20为pre_file_CID,<30为pre_block_index
                                    # >30为pre_TxID,若为0则结束
                    write_pre_TxID(20)
                    write_pre_index(30)#依次进行三次写入操作，并清空了三个pool
                    generate_image(tag, file_pointer, image_file_name[target_value.index(current_block_index)])#.index定位元素在列表中的位置
                    ''' 
                        保存路径f'D:/go-ipfs/{total_Tx_size}_{image_file_name[0]}.bmp'
                        .index返回current_block_index在target_value中的位置,用于定位file_name
                    '''
            ###########################################  IPFS交互  #########################################################
                request_CID(image_file_name[target_value.index(current_block_index)])  #向IPFS发出文件，并将返回的CID写入test_Tx的CID attribute
                '''CID已经写入完毕，可以计算TxID,并push into the unconfirmed_Tx_pool中了'''
            ###########################################  TxID 进pre_TxID_poll  #############################################
                test_Tx.compute_TxID()
                pre_TxID_pool.append(test_Tx.TxID)
                pre_CID_pool.append(test_Tx.CID)
                pre_block_index.append(current_block_index+1)
                blockchain.unconfirmed_transactions.append(test_Tx.__dict__) #压入unconfirmed_Tx
                result_pool.append(test_Tx.__dict__)#保存一下结果
                pool_size = len(blockchain.unconfirmed_transactions)
            ##########################################  剩余pool space 用ramdom_Tx填充  ######################################
                while pool_size < max_pool_size:
                    test_Tx = generate_random_transaction()
                    blockchain.unconfirmed_transactions.append(test_Tx.__dict__)
                    pool_size = len(blockchain.unconfirmed_transactions)
                print('当前写入进度：',current_block_index, pin)
            blockchain.mine() #unconfirmed_Tx满，进行挖块
            pool_size = len(blockchain.unconfirmed_transactions)#更新pool_size
        print('最后交易ID：',pre_TxID_pool)
        ######################################  保存latest_TxID,与所有target_Tx的信息 #########################################
        with open(f'{total_Tx_size}/{total_Tx_size}_last_target_TxID.txt', 'w', encoding='utf-8') as lf:  # 打开一个文件，'w'为只写模式，为lf,有中文写入时要指定'utf-8'
            lf.writelines(pre_TxID_pool)#因为在write函数中每一次都清空list,故最后只有最后一笔TxID
            lf.close()
        with open(f'{total_Tx_size}/{total_Tx_size}_targetTx_pool.json','w',encoding='utf-8') as lf:
            json.dump(result_pool,lf)
            lf.close()
        ###########################################  链保存为json  ##############################################################
        content = []
        chain = blockchain.chain #此时chain 是一个list
        for block in chain:
            block = block.__dict__
            ################################  尝试字典化  ##############################
            # for transactions in block["transactions"]: #json只接受 str,bytes bytearray,但str下必需是dict格式，这里只能先bytearray
            #     print(type(transactions), transactions)
                # transactions = eval(transactions)#字典化
                # print(type(transactions), transactions)
            ##########################################################################
            content.append(block)
        #######################################################################################################################
        with open(f'{total_Tx_size}/{total_Tx_size}_sim_BC_structure.json', 'w', encoding='utf-8') as lf:  # 打开一个文件，'w'为只写模式，为lf,有中文写入时要指定'utf-8'
            json.dump(content,lf)#,sort_keys=True)#,indent=4)
            lf.close()
