import os
import uuid
import pandas as pd
from io import BytesIO
from pydantic import BaseModel
from typing import Dict
from fastapi import UploadFile, File
from tools.loader import CSVLoader
from agents.dataStore import DataStore
temp_file_path = "./tmp/temp_file/"
os.makedirs(temp_file_path, exist_ok=True)


class FileStore(BaseModel):
    id_to_path: Dict[str, list] = dict()
    id_to_doc_ids: Dict[str, list] = dict()


async def extract_dataframe_from_form_file(file_store: FileStore, data_store: DataStore, file: UploadFile = File(...)):
    """Return the dataframe of a file."""
    # get the file body from the upload file object

    file_stream = await file.read()
    df_dict = {}
    if '.csv' in file.filename:
        df_dict[file.filename] = pd.read_csv(BytesIO(file_stream))
    elif '.xlsx' in file.filename:
        sheets = pd.read_excel(file_stream, sheet_name=None)
        for name, df in sheets.items(): df_dict[file.filename.removesuffix('.xlsx') + "_" + name + ".csv"] = df

    # write the file to a temporary location
    path_list = []
    col_list = []
    path_id = str(uuid.uuid4())[:8]
    for name, df in df_dict.items():
        csv_path = temp_file_path + path_id + "_" + name
        path_list.append(csv_path)
        df.to_csv(csv_path, encoding="utf-8", sep=",", index=False)
        col_list.extend(CSVLoader(csv_path, encoding='utf-8-sig').load())

    file_store.id_to_path[path_id] = path_list

    old_ids = set(data_store.vectors.index_to_docstore_id.values())
    data_store.vectors.add_documents(col_list)
    new_ids = old_ids ^ set(data_store.vectors.index_to_docstore_id.values())
    file_store.id_to_doc_ids[path_id] = list(new_ids)
    return path_id


async def delete_file(file_store: FileStore, data_store: DataStore, ids: list, delete_all: bool) -> bool:
    if delete_all:
        for file in os.listdir(temp_file_path):
            os.remove(temp_file_path + file)
        for doc_ids in file_store.id_to_doc_ids.values():
            data_store.vectors.delete(doc_ids)
        file_store.id_to_path.clear()
        file_store.id_to_doc_ids.clear()
        return True
    else:
        for id in ids:
            for file in file_store.id_to_path[id]:
                os.remove(file)
            data_store.vectors.delete(file_store.id_to_doc_ids[id])
            del file_store.id_to_path[id]
            del file_store.id_to_doc_ids[id]
        return True



if __name__ == "__main__":
    a = pd.read_excel("../data/template.xlsx", sheet_name=None)
    print(a)
    pd.merge()
    for i, df in enumerate(dfs):
        if i == 0:
            merge_df = pd.merge(df, dfs[i + 1], on="日期", suffixes=('', f'_{i}'))
        elif 1 < i:
            merge_df = pd.merge(merge_df, df, on="日期", suffixes=('', f'_{i}'))
