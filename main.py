import uvicorn
import argparse
import sys
import os
import pandas as pd
from io import StringIO

from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain.llms import AzureOpenAI
from langchain.llms import OpenAI
from agents.execl_agent import ExeclAgent

from fastapi.responses import FileResponse
from fastapi import FastAPI, File, HTTPException, Depends, Body, UploadFile, WebSocket, WebSocketDisconnect
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv('.env'))
app = FastAPI()




@app.websocket("/ws/logger")
async def output_ws(websocket: WebSocket):
    await websocket.accept()

    tmp = sys.stdout
    hidden_text_io = StringIO()
    sys.stdout = hidden_text_io
    try:
        while True:
            input_json = await websocket.receive_text()
            output = hidden_text_io.getvalue()
            if output:
                await websocket.send_text(output)
    except WebSocketDisconnect:
        sys.stdout = tmp
        await websocket.close()


@app.get("/file/{file_path:path}")
async def read_file(file_path: str):
    return FileResponse(file_path)


@app.on_event("startup")
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


def start():
    uvicorn.run("main:app", host=args.host, port=args.port, reload=True)


if __name__ == "__main__":
    args = get_args()
    start()
