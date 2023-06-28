import re
import pandas as pd
from typing import Any
from models.api import QueryResult


def query_response_parse(response: Any, chart_type: str) -> QueryResult:
    if isinstance(response, dict):
        text = str(response['summary'])
        response.pop('summary')
        text = text + pd.DataFrame(response).to_markdown() + "\n"
    else:
        text = response
        response = {'日期': []}
        chart_type = 'None'
    return QueryResult(text=text, data=response, chart_type=chart_type)


def function_query_response_parse(response_dict: dict, api_endpoint: str, plot_image: bool) -> QueryResult:
    response = response_dict["text"]
    if plot_image:
        for image_filename in re.findall("images/.*?.png", response):
            response = re.sub("\(.*?.png\)", f"({api_endpoint}/{image_filename})", response)
    else:
        response = re.sub("!\[.*?.png\)", "", response)
        response = response.replace("\n", "")
    text = response + "\n" + response_dict["markdown"] + "\n"
    return QueryResult(text=text, data=response_dict["data"], chart_type="None")