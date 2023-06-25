<h1 align="center">
📄<br>QueryGPT
</h1>

## 📚 QueryGPT

> QueryGPT是一个基于`OpenAI GPT3.5` 和 `Langchain` 的自然语言数据查询工具。
> 基于`OpenAI GPT3.5-turobo-0613`最新发布的`Function Calling`实现，比Langchain官方的`Pandas Agent`和`CSV Agent` **更快**、**更稳定**、**更准确**
> 实现了`Markdown`格式、``JSON格式`的数据输出，支持`Echart`形式和`Matplotlib`图表绘制。

## 快速开始
Follow these steps to quickly set up and run.
1. 安装Python 3.10和pip.
2. `git clone git@github.com:sdaaron/QueryGPT.git`
3. `cd QueryGPT`
4. 安装依赖`pip install -r requirements.txt`
5. 将`.env.example`重命名为`.env`并修改环境变量
```
OPENAI_API_KEY='你的OpenAI Key'
OPENAI_API_BASE="代理地址（非必须）"
OPENAI_API_VERSION="2020-11-07（非必须）"
```
6. 启动命令
启动程序并指定本地CSV文件 :```python main.py --host xx --port xxx --csv_path xxx.csv```
启动程序并指定本地Excel文件: ```python main.py --host xx --port xxx --excel_path xxx.xlsx```


## 路线图 Roadmap
- [x] 实现数据查询功能和结果输出
  - [x] 自然语言查询表格数据，并输出答案
  - [x] 输出Echart图表
  - [x] 输出Markdown形式表格

- [ ] 交互优化
  - [ ] 界面UI美化
  - [ ] 图表样式优化
  - [ ] 流式输出
  - [ ] 引导用户正确提问，显示关联问题
  - [ ] 显示取数过程

- [ ] 实现更多功能
  - [ ] 数据分析能力，对输出数据进行简单分析
  - [ ] 支持用户上传表格数据
  - [ ] 支持连接数据库
  - [ ] 通过向量检索缩小取数范围
  - [ ] 支持自然语言操作表格数据
  - [ ] 用户登录

- [ ] 支持更多Agent
  - [ ] 支持SQL Agent