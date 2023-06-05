import argparse
from fastapi import APIRouter, Depends, HTTPException
from chains import openAI

from pydantic import BaseModel
from typing import Union
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from fastapi import FastAPI, File, HTTPException, Depends, Body, UploadFile, WebSocket, WebSocketDisconnect
from tools.response_parser import res_parser
import pandas as pd
from agents.execl_agent import ExeclAgent
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)
class ChatResponse(BaseModel):
    response: str = Field(..., description="Response text",
                          example="这是财富保有用户数量近一个月的柱状图：![image](http://127.0.0.1:8000/file/images/2023-05-30_19-33-38.png)")


class ChatRequest(BaseModel):
    question: str = Field(..., description="Question text", example="财富保有用户数量近一个月的数据绘制成柱状图")



@router.post(
    "/chat",
    response_model=ChatResponse, )
async def chat(question: ChatRequest = Body(...)):
    try:
        response = agent.predict(question.question)
        response = res_parser(response, args.api_endpoint)
        return ChatResponse(response=response)
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Internal Service Error")


class ChatQuestionDto(BaseModel):
    question: str
    api_key: Union[str, None] = None


# sse response streaming
@router.post("/question")
async def simple_question(chat_question_dto: ChatQuestionDto):
    if chat_question_dto.api_key is None:
        raise HTTPException(status_code=400, detail="api_key is required")
    return StreamingResponse(openAI.chat(chat_question_dto.question), media_type='text/event-stream')
@router.on_event("startup")
async def startup():
    global agent
    global df
    global args
    args = get_args()
    llm = AzureChatOpenAI(
        deployment_name="v1",
        model_name="gpt-35-turbo",
        temperature=0
    )
    if args.excel_path is not None:
        df = pd.read_excel(args.excel_path)
    else:
        df = pd.read_csv(args.csv_path, encoding="utf-8", sep="\t")
    agent = ExeclAgent(llm, df, verbose=args.verbose)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--csv_path", type=str, default="data/data.csv")
    parser.add_argument("--excel_path", type=str, default=None)
    parser.add_argument("--verbose", type=bool, default=True)
    parser.add_argument("--api_endpoint", type=str,
                        default="https://u104788-9a62-38eec028.east.seetacloud.com:8443/file")
    args = parser.parse_args()
    return args