import json
import pandas as pd
from pandas import DataFrame
from typing import Any
from pydantic import BaseModel, BaseConfig
from typing import List
from langchain.embeddings.base import Embeddings
from tools.loader import CSVLoader
from langchain.vectorstores.base import VectorStore

from tools.plot_tool import plot_chart


def set_vector_store(file_paths: List[str], embeddings: Embeddings, vector_store: VectorStore, encoding: str = "UTF-8") -> VectorStore:
    csv_data = []
    for file_path in file_paths:
        csv_data.extend(CSVLoader(file_path, encoding=encoding).load())
    vectors = vector_store.from_documents(csv_data, embeddings)
    return vectors


class DataStore(BaseModel):
    df: Any = None
    date_column_name: str = "日期"
    query_df: dict = {"query": [], "channel": []}
    vectors: VectorStore = None

    class Config(BaseConfig):
        arbitrary_types_allowed = True

    def init_df(self, query: str) -> DataFrame:
        source_dict = {}
        source_set = set()
        df = DataFrame()
        results = self.vectors.similarity_search(query=query, k=20)
        for clo in results:
            column_name = clo.page_content
            file_path = clo.metadata["source"]
            if file_path in source_set:
                source_dict[file_path].append(column_name)
            else:
                source_dict[file_path] = [column_name]
            source_set.add(file_path)
        for k, v in source_dict.items():
            if self.date_column_name not in v:
                v.append(self.date_column_name)
            df[v] = pd.read_csv(k)[v]
        df[self.date_column_name] = pd.to_datetime(df[self.date_column_name])
        self.df = df
        return df

    def query(self, time_series: List[str], column_names: List[str], dates: List[str] = None) -> json:
        if not set(column_names).issubset(set(self.df.columns)): return json.dumps({"error": "Column name does not exist. Please enter a column name in the dataframe."})
        if self.date_column_name in column_names: column_names.remove(self.date_column_name)
        if dates:
            filtered_df = self.df[self.df[self.date_column_name].isin(dates)]
            res_df = filtered_df.loc[:, [self.date_column_name] + column_names].reset_index(drop=True)
            res_df[self.date_column_name] = pd.to_datetime(res_df[self.date_column_name])
            self.query_df["query"].append(res_df)
            res_df[self.date_column_name] = res_df[self.date_column_name].dt.strftime("%Y-%m-%d")
            return json.dumps(res_df.to_dict(orient='records'))
        elif time_series:
            if len(time_series) != 2: return json.dumps({"error": "Please enter the correct time series: [start_date, end_date]."})
            start_date, end_date = pd.to_datetime(time_series[0]), pd.to_datetime(time_series[1])
            filtered_df = self.df[(self.df[self.date_column_name] >= start_date) & (self.df[self.date_column_name] <= end_date)]
            res_df = filtered_df.loc[:, [self.date_column_name] + column_names].reset_index(drop=True)
            self.query_df["query"].append(res_df)
            result_dict = {}
            for col_name in column_names:
                result_dict[col_name] = "{}至{}的总值：{:.2f}".format(
                    time_series[0], time_series[1], float(res_df[col_name].sum()))
            result_dict["description"] = res_df.describe().to_markdown()
            return json.dumps(result_dict)
        else:
            return json.dumps({"error": "Please enter the correct time."})

    def calculate_growth_rate(self, time_series: List[str], column_names: List[str]) -> json:
        if len(time_series) != 2: return json.dumps({"error": "Please enter the correct time series: [start_date, end_date]."})
        if not set(column_names).issubset(set(self.df.columns)): return json.dumps(
            {"error": "Column name does not exist. Please enter a column name in the dataframe."})
        if not self.query_df["query"]: return json.dumps({"error": "Please perform a query operation first."})
        if self.date_column_name in column_names: column_names.remove(self.date_column_name)
        offset_start_date, offset_end_date = pd.to_datetime(time_series[0]), pd.to_datetime(time_series[1])
        filtered_df = self.df.loc[:, [self.date_column_name] + column_names]
        current_df = self.query_df["query"][0]
        start_date, end_date = pd.to_datetime(current_df[self.date_column_name].iloc[0]), pd.to_datetime(current_df[self.date_column_name].iloc[-1])
        overed_df = filtered_df[(filtered_df[self.date_column_name] >= offset_start_date) & (filtered_df[self.date_column_name] <= offset_end_date)]
        result_dict = {}
        value_type = "同比" if (end_date - offset_end_date).days > 92 else "环比"
        for col_name in column_names:
            current_col_sum = current_df[col_name].sum()
            overed_col_sum = overed_df[col_name].sum()
            month_over_month_value = (current_col_sum - overed_col_sum) / overed_col_sum * 100
            result_dict[col_name] = "{}至{}的总和为：{:.2f}, {}至{}的总和为：{:.2f}, {}增长：{:.2f}%".format(
                start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), current_col_sum,
                time_series[0], time_series[1], overed_col_sum, value_type, month_over_month_value)
        self.query_df["query"].append(overed_df)
        return json.dumps(result_dict)

    def average_order_value(self, dividend_name: str, divisor_name: str) -> json:
        if not {dividend_name, divisor_name}.issubset(set(self.df.columns)): return json.dumps(
            {"error": "Column name does not exist. Please enter a column name in the dataframe."})
        try:
            dividend_sum = float(self.query_df["query"][0][dividend_name].sum())
            divisor_sum = float(self.query_df["query"][0][divisor_name].sum())
        except:
            return json.dumps({"error": "Please query {} first.".format(divisor_name)})
        value = dividend_sum / divisor_sum
        result_dict = {"result": "{}的总值为{:.2f}，{}的总值为{:.2f}，客单价为{:.2f}".format(dividend_name, dividend_sum,
                                                                               divisor_name, divisor_sum, value)}
        return json.dumps(result_dict)

    def channel_ratio(self, time_series: List[str], base_name: str, channel_names: list) -> json:
        if len(time_series) != 2: return json.dumps({"error": "Please enter the correct time series: [start_date, end_date]."})
        if not set(channel_names + [base_name]).issubset(set(self.df.columns)): return json.dumps(
            {"error": "Column name does not exist. Please enter a column name in the dataframe."})
        if self.date_column_name in channel_names: channel_names.remove(self.date_column_name)
        if base_name in channel_names: channel_names.remove(base_name)
        start_date, end_date = pd.to_datetime(time_series[0]), pd.to_datetime(time_series[1])
        filtered_df = self.df.loc[:, [self.date_column_name, base_name] + channel_names]
        overed_df = filtered_df[(filtered_df[self.date_column_name] >= start_date) & (filtered_df[self.date_column_name] <= end_date)]
        self.query_df["channel"].append(overed_df)
        result_dict = {}
        base_col_sum = overed_df[base_name].sum()
        for col_name in channel_names:
            channel_col_sum = overed_df[col_name].sum()
            channel_ratio = channel_col_sum / base_col_sum * 100
            result_dict[col_name] = "{}至{}的总和为：{:.2f}, 渠道占比为：{:.2f}%".format(
                start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), channel_col_sum, channel_ratio)
        return json.dumps(result_dict)

    def plot_data(self, chart_title: str, chart_type: str, plot_image: bool) -> json:
        if chart_type == "pie":
            data = self.query_df["channel"][0]
        else:
            data = pd.concat(self.query_df["query"], axis=0)
        image_path = plot_chart(data, chart_title, chart_type, plot_image)
        return json.dumps({"image_path": image_path})

    def gather(self, columns_limit: int = 5, return_type: str = "dict"):
        if self.query_df["query"]:
            query_data = pd.concat(self.query_df["query"] + self.query_df["channel"], axis=0).drop_duplicates().dropna().reset_index(drop=True)
        else:
            query_data = pd.concat([self.df[self.date_column_name], self.df.iloc[:, :columns_limit]], axis=1).drop_duplicates().dropna().reset_index(drop=True)
        query_data[self.date_column_name] = pd.to_datetime(query_data[self.date_column_name])
        if len(query_data.columns) < columns_limit:
            # 获得相似列
            similarity_column_names = self.df.iloc[:, :columns_limit].columns.to_list()
            # 去除相同列
            [similarity_column_names.remove(col) for col in query_data.columns if col in similarity_column_names]
            merged_df = pd.merge(self.df, query_data, on=self.date_column_name)
            similarity_data = merged_df.loc[:, similarity_column_names]
            query_data = pd.concat([query_data, similarity_data], axis=1)
        query_data[self.date_column_name] = query_data[self.date_column_name].dt.strftime("%Y-%m-%d")
        query_data = query_data.round(2)
        if return_type == "dict":
            return query_data.to_dict(orient='list')
        elif return_type == "markdown":
            return query_data.to_markdown()

    def reset(self) -> None:
        self.query_df["query"].clear()
        self.query_df["channel"].clear()