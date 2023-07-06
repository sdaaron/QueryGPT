<h1 align="center">
  <img src="img/icon.png" alt="icon" style="vertical-align:middle;"> QueryGPT
</h1>

## QueryGPT 自然语言数据查询

> 1. QueryGPT是一个基于`OpenAI GPT3.5` 和 `Langchain` 的自然语言数据查询工具。  
> 2. 基于`OpenAI GPT3.5-turobo-0613`和`Langchain Function Agent`实现，相比`Pandas Agent`和`CSV Agent` **更快、稳定和准确**。  
> 3. 实现了`Markdown`格式、`JSON格式`的数据输出，支持`Echarts`形式和`Matplotlib`图表绘制。  

## 效果示例
<div align="center">
  <img src="img/example.png" alt="example" style="vertical-align:middle;">
</div>

## 快速开始

### 启动API
1. 安装`Python 3.10`和`pip`，创建虚拟环境
2. `git clone git@github.com:sdaaron/QueryGPT.git`
3. `cd QueryGPT/server`
4. `pip install -r requirements.txt`
5. 将`.env.example`重命名为`.env`并修改环境变量
```
OPENAI_API_KEY='你的OpenAI Key'
```
6. 启动命令  
使用本地默认数据文件启动API :```python main.py --host xx --port xxx```  
指定本地CSV文件启动API :```python main.py --host xx --port xxx --csv_path xxx.csv```  
指定本地Excel文件启动API: ```python main.py --host xx --port xxx --excel_path xxx.xlsx```  

### 启动UI
1. `cd QueryGPT/client`
2. `pnpm install`
3. `npm run dev`
4. 确保你的`vite.config.js`中的`proxy`配置，与你的API服务地址一致

## 项目介绍
1. 项目简介  
    * 基于OpenAI的查询数据工具。该工具采用FastAPI作为后端框架，并通过使用Langchain来实现具体功能。工具的优点包括数据不经过接口，所有取数操作在本地完成，确保数据的私密性；同时，该工具是可扩展的，开发者可以在Langchain tool中增加所需的类，实现自定义功能。此外，该工具还采用Embedding相似度搜索，实现多文件搜索，快速定位目标列，减少token使用数量。
1. 功能和特点   
   * 通过调用OpenAI提供的接口，获取所需的信息，再调用接口，完成数据查询，并将信息进行预处理，只保留有效信息，确保了数据的私密性以及有效性。
   * Langchain实现agent功能，通过编写自定义的类，可以扩展工具的功能。开发者可以根据自己的需求，在tool中增加所需的类，以实现特定的查询功能。
   * 采用Embedding相似度搜索技术来实现快速定位目标列和减少token数量。通过将数据转换为向量表示，并计算向量之间的相似度，可以快速找到与查询条件相似的目标列。同时，减少token数量可以提高搜索效率和性能。

2. 缺点
   * 工具的功能相对简单，无法灵活地实现复杂的查询任务。对于一些高级的查询需求和复杂的数据分析任务，该工具可能无法满足用户的要求。
   * 使用场景单一 该工具目前只适用于对结构化数据（如CSV文件）进行查询。对于其他类型的数据或不同的查询场景，该工具的适用性较低，无法实现良好的迁移和扩展性。

3. 展望  
   为了进一步提升工具的功能和适用性，可以考虑以下改进和发展方向：
   * 支持更多查询场景，工具可以扩展支持更多结构化数据的查询场景，例如支持数据库查询。这样可以增加工具的适用范围，并满足更广泛的用户需求。
   * 实现通用的数据仓库，为了支持更多的查询方法和数据类型，可以考虑实现一个通用的数据仓库。通过构建数据仓库，用户可以更灵活地进行数据查询和分析，并享受到更多的功能和特性。


## 路线图
- [ ] 实现数据查询功能和结果输出
  - [x] 自定义Langchain Function Agent
    - [x] 实现Query Tool，实现基础取数需求
    - [x] 实现Plot Tool，实现图表绘制需求
    - [ ] 实现多种自定义的常用计算工具
      - [x] 计算客单价、占比、增长率
      - [x] 计算月同环比、年同环比
      - [ ] 支持更多自定义计算
    - [x] 集成ydata-profiling，实现简单数据描述
  - [x] Embedding相似度搜索
  - [x] 支持多种格式输出
    - [x] 输出Markdown格式数据
    - [x] 输出JSON格式数据
    - [x] 调用Matplotlib绘制簇状柱形图、折线图、饼状图
    - [x] 输出Echart图表
    - [x] 输出表格

- [ ] 交互优化
  - [x] 界面UI美化
  - [x] 图表样式优化
  - [ ] 流式输出
  - [ ] 引导用户正确提问，显示关联问题
  - [ ] 显示取数过程

- [ ] 实现更多功能
  - [ ] 更丰富的数据分析能力，对输出数据进行简单分析
  - [ ] 支持用户上传表格数据
  - [ ] 支持连接数据库
  - [ ] 支持自然语言操作表格数据
  - [ ] 用户登录