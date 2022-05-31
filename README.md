# Interactive_traceability_structure
用于测试交互溯源结构的溯源效率
程序须知：
1. ipfshttpclient version 0.8.0a2
2. ipfs version 0.8.0
3. 文件20至2000000为手工创建，用于存储不同量级下的仿真数据与溯源结果
4. Raw_image文件件存储仿真原图像文件
5. 目标交易链结构：

![image](https://github.com/aucnm/Interactive_traceability_structure/blob/master/target_chain_structure/target_chain_structure.jpg)

运行顺序：
1. BCandIPFS_DataFrame_generator.py -->生成各量级下的仿真数据
2. loop_IPFS_search.py -->在不同量级下进行交互溯源，并在20W_200W_IPFS_search_results.csv中记录溯源耗时
3. loop_json_search.py -->在不同量级下进行链上溯源，并在20W_200W_json_search_results.csv中记录溯源耗时
4. Figure_results_20W_200W_.py --> 不同方法耗时对比

论文相关数据已上传release
