import uvicorn
import argparse
import sys
import os
import pandas as pd
from langchain.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

from agents.excel_agent import ExcelAgent
from agents.function_query_agent import FunctionQueryAgent
from tools.response_parser import query_response_parse, function_query_response_parse
from agents.dataStore import set_vector_store, DataStore
from models.api import ChatResponse, ChatRequest

from fastapi.responses import FileResponse
from fastapi import FastAPI, File, HTTPException, Depends, Body
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv('.env'))
app = FastAPI()


@app.post(
    "/chat",
    response_model=ChatResponse,)
async def chat(question: ChatRequest = Body(...)):
    try:
        agent = ExcelAgent(llm, df.copy(), verbose=args.verbose)
        response = agent.predict(question.question)
        chart_type = agent.get_chart_type(question.question)
        response = query_response_parse(response, chart_type)
        return ChatResponse(response=response)
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Internal Service Error")


@app.post(
    "/function_chat",
    response_model=ChatResponse,)
async def function_chat(question: ChatRequest = Body(...)):
    try:
        similarity_df = DATA_STORE.init_df(question.question)
        agent = FunctionQueryAgent(function_llm, DATA_STORE, similarity_df, verbose=args.verbose)
        response_dict = agent.predict(question.question)
        response = function_query_response_parse(response_dict, args.api_endpoint)
        return ChatResponse(response=response)
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Internal Service Error")


@app.get("/file/{file_path:path}")
async def read_file(file_path: str):
    return FileResponse(file_path)


@app.on_event("startup")
async def startup():
    global llm
    global function_llm
    global df
    global args
    global DATA_STORE

    args = get_args()
    # llm = AzureChatOpenAI(
    #     deployment_name="v1",
    #     model_name="gpt-35-turbo",
    #     temperature=0
    # )
    llm = ChatOpenAI()
    function_llm = ChatOpenAI(model_name="gpt-3.5-turbo-0613")
    vector_store = set_vector_store([args.csv_path], embeddings=OpenAIEmbeddings(), vector_store=FAISS, encoding="UTF-8-sig")
    DATA_STORE = DataStore(vectors=vector_store)
    if args.excel_path is not None:
        df = pd.read_excel(args.excel_path)
    else:
        df = pd.read_csv(args.csv_path, encoding="utf-8")
    df['日期'] = pd.to_datetime(df['日期'])
    df = df.sort_values('日期')


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--csv_path", type=str, default="data/data.csv")
    parser.add_argument("--excel_path", type=str, default=None)
    parser.add_argument("--verbose", type=bool, default=True)
    parser.add_argument("--api_endpoint", type=str, default="https://127.0.0.1:8000/file")
    args = parser.parse_args()
    return args


def start():
    uvicorn.run("main:app", host=args.host, port=args.port, reload=True)


if __name__ == "__main__":
    args = get_args()
    start()
