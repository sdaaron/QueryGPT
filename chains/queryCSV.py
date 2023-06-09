import datetime

from langchain import OpenAI, PromptTemplate, LLMChain
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain.agents import create_pandas_dataframe_agent


def getCurrentDateFun():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def getDateFromGPT(question: str):
    llm = OpenAI(temperature=0 , model_name="gpt-3.5-turbo")
    # prompt = PromptTemplate(
    #     input_variables=["current_date", "question"],
    #     template="""today is {current_date} ,you are a Data analyst ,
    #     can you get a start date and last date from question: {question},
    #              it must be format like: YYYY-MM-DD to YYYY-MM-DD
    #              """
    # )
    # chain = LLMChain(llm=llm, prompt=prompt)

    # resp = chain.run(current_date= '2022/05/01，Sunday', question=question)
    # print(resp)
    import pandas as pd
    df = pd.read_csv('data/data1.csv')
    # print(df[(df['日期'] >= '2022/3/1' ) & (df['日期'] <= '2022/3/31')])
    # print(df[df['日期'].between('2022/03/01', '2022/03/31')])
    # 将字符串YYYY/M/D转换为YYYY/MM/DD, 例如2022/5/1转换为2022/05/01，修改源文件
    # df['日期'] = pd.to_datetime(df['日期'], format='%Y/%m/%d' )
    # print(df[df['日期'].between('2022/03/01', '2022/03/31')])
    # 保存存修改
    # df.to_csv('data/data1.csv', index=False)
    df['日期'] = pd.to_datetime(df['日期'], format='%Y-%m-%d')
    agent = create_pandas_dataframe_agent(llm, df, verbose=True)
    response = agent.run("""
    As a professional data  analysis assistant, your job is retrieve data from a CSV file.
    If you can't get the required data column, please find a similar one.
    Please note that you will not read any external files or create a new dataframe;
    You will only use the existing variable 'df' to operate the dataframe.
    Get the required time series that is use for query based on current date and question.
    if query result is multiple rows, please return use JSON format ,else if just return the query result.
    Please only use 'df' to retrieve data by below question : """ + question
   )
    return response
