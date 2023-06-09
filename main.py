import os
from typing import Union
from langchain.chat_models import ChatOpenAI
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain.llms import OpenAI
from pydantic import BaseModel

from agents.csv_agent import CsvAgent

from routers import chat

os.environ["OPENAI_API_KEY"] = "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"
app = FastAPI()
# cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(chat.router)


class ChatQuestionDto(BaseModel):
    question: str
    api_key: Union[str, None] = None


@app.post("/question3")
async def simple_question3(chat_question_dto: ChatQuestionDto):
    print('question: ', chat_question_dto.question)
    return agent.predict(chat_question_dto.question)


@app.on_event("startup")
async def startup():
    global agent
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0
    )
    # df = pd.read_csv('data/data1.csv', encoding="utf-8", sep="\t")
    df = pd.read_csv('data/data1.csv')
    # date format is YYYY-MM-DD
    df['日期'] = pd.to_datetime(df['日期'], format='%Y-%m-%d')
    # # 时间整体加上一年
    # df['日期'] = df['日期'].apply(lambda x: x + pd.DateOffset(years=1))
    # # 保存
    # df.to_csv('data/data1.csv', index=False)
    agent = CsvAgent(llm, df ,verbose=True)


if __name__ == '__main__':
    import uvicorn


    uvicorn.run('main:app', host='0.0.0.0', port=7001, reload=True)
