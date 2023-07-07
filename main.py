import uvicorn
import argparse
import pandas as pd
import langchain
from langchain.chat_models import AzureChatOpenAI, ChatOpenAI
from vectorstores.faiss import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.cache import InMemoryCache

from agents.excel_agent import ExcelAgent
from agents.function_query_agent import FunctionQueryAgent
from tools.response_parser import query_response_parse, function_query_response_parse
from tools.file import extract_dataframe_from_form_file, FileStore, delete_file
from agents.dataStore import set_vector_store, DataStore
from models.api import ChatResponse, ChatRequest, DeleteRequest, DeleteResponse, UpsertResponse

from fastapi.responses import FileResponse
from fastapi import FastAPI, File, HTTPException, UploadFile, Body
from dotenv import find_dotenv, load_dotenv
langchain.llm_cache = InMemoryCache()
load_dotenv(find_dotenv('.env'))
app = FastAPI()


# @app.post(
#     "/chat",
#     response_model=ChatResponse,)
# async def chat(question: ChatRequest = Body(...)):
#     try:
#         agent = ExcelAgent(llm, df.copy(), verbose=args.verbose)
#         response = agent.predict(question.question)
#         chart_type = agent.get_chart_type(question.question)
#         response = query_response_parse(response, chart_type)
#         return ChatResponse(response=response)
#     except Exception as e:
#         print("Error:", e)
#         raise HTTPException(status_code=500, detail="Internal Service Error")


@app.post(
    "/function_chat",
    response_model=ChatResponse,)
async def function_chat(question: ChatRequest = Body(...)):
    try:
        DATA_STORE.init_df(question.question)
        agent = FunctionQueryAgent(function_llm, DATA_STORE, args=args)
        response_dict = agent.predict(question.question)
        response = function_query_response_parse(response_dict, args.api_endpoint, args.plot_image)
        return ChatResponse(response=response)
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Internal Service Error")


@app.get("/file/{file_path:path}")
async def read_file(file_path: str):
    return FileResponse(file_path)


@app.post(
    "/upsert-file",
)
async def upsert_file(
    file: UploadFile = File(...),
):
    try:
        path_id = await extract_dataframe_from_form_file(
            file_store=FILE_STORE,
            data_store=DATA_STORE,
            file=file)
        return UpsertResponse(ids=[path_id])
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Internal Service Error")


@app.delete(
    "/delete",
    response_model=DeleteResponse,
)
async def delete(
    request: DeleteRequest = Body(...),
):
    if not (request.ids or request.delete_all):
        raise HTTPException(
            status_code=400,
            detail="One of ids or delete_all is required",
        )
    try:
        success = await delete_file(
            file_store=FILE_STORE,
            data_store=DATA_STORE,
            ids=request.ids,
            delete_all=request.delete_all)
        return DeleteResponse(success=success)
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Internal Service Error")


@app.on_event("startup")
async def startup():
    # global llm
    global function_llm
    # global df
    global args
    global DATA_STORE
    global FILE_STORE

    args = get_args()
    # llm = AzureChatOpenAI(
    #     deployment_name="v1",
    #     model_name="gpt-35-turbo",
    #     temperature=0
    # )
    FILE_STORE = FileStore()
    # llm = ChatOpenAI()
    function_llm = ChatOpenAI(model_name="gpt-3.5-turbo-0613")
    vector_store = set_vector_store([], embeddings=OpenAIEmbeddings(), vector_store=FAISS, encoding="UTF-8-sig")
    DATA_STORE = DataStore(vectors=vector_store)
    DATA_STORE.date_column_name = args.date_column_name
    # if args.excel_path is not None:
    #     df = pd.read_excel(args.excel_path)
    # else:
    #     df = pd.read_csv(args.csv_path, encoding="utf-8")
    # df['日期'] = pd.to_datetime(df['日期'])
    # df = df.sort_values('日期')


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--csv_path", type=str, default="test.csv")
    parser.add_argument("--excel_path", type=str, default=None)
    parser.add_argument("--date_column_name", type=str, default="日期")
    parser.add_argument("--verbose", type=bool, default=True)
    parser.add_argument("--plot_image", type=bool, default=False)
    parser.add_argument("--api_endpoint", type=str, default="https://127.0.0.1:8000/file")
    args = parser.parse_args()
    return args


def start():
    uvicorn.run("main:app", host=args.host, port=args.port, reload=True)


if __name__ == "__main__":
    args = get_args()
    start()
