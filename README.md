<h1 align="center">
📄<br>QueryGPT
</h1>

## 📚 QueryGPT

> QueryGPT是一个基于`OpenAI GPT3.5` 和 `Langchain` 的自然语言数据查询工具。

## 快速开始 Quickstart
Follow these steps to quickly set up and run.
1. Install Python 3.10, if not already installed.
2. Clone this repository
3. Navigate to the cloned repository directory: cd /path/to/DataBot
4. Install poetry: ```pip install poetry```
5. Create a new virtual environment with Python 3.10: ```poetry env use python3.10```
6. Activate the virtual environment:```poetry shell```
7. Install app dependencies:```poetry install```
8. Set the required environment variables in *.env.example* and rename  the file to *.env*
```
# openai
OPENAI_API_KEY=xxx

# proxy
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890

# Azure OpenAI
OPENAI_API_TYPE=azure
OPENAI_API_VERSION=2023-05-15
OPENAI_API_BASE=xxx
OPENAI_API_KEY=xxx
```
9. Run with the csv file API :```poetry run python main.py --host xx --port xxx --csv_path xxx.csv``` or
Run with the excel file API: ```poetry run python main.py --host xx --port xxx --excel_path xxx.xlsx```


## 路线图 Roadmap
- [x] 实现数据查询功能和结果输出
  - [x] 自然语言查询表格数据，并输出答案
  - [x] 输出Echart图表
  - [x] 输出Markdown形式表格

- [ ] 交互优化
  - [ ] 界面UI美化
  - [ ] 图标UI优化
  - [ ] 流式输出文本结果
  - [ ] 引导用户正确提问，显示关联问题
  - [ ] 显示执行过程
  - [ ] 支持数据上传
  - [ ] 显示执行过程

- [ ] 实现更多功能
  - [ ] 数据分析能力，对输出数据进行简单分析
  - [ ] 数据分析能力，对输出数据进行简单分析
  - [ ] 支持连接数据库，支持运行SQL Agent
  - [ ] 通过向量检索缩小取数范围
  - [ ] 支持自然语言操作表格数据
  - [ ] 用户登录
