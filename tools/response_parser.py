import re
from typing import Any
from models.api import QueryResult


def query_response_parse(response: Any, chart_type: str) -> QueryResult:
    if isinstance(response, dict):
        text = str(response['summary'])
        response.pop('summary')
    else:
        text = response
        response = {'日期': []}
        chart_type = 'None'
    return QueryResult(text=text, data=response, chart_type=chart_type)