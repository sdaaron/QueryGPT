from pydantic import BaseModel, Field
from typing import List, Optional


class QueryResult(BaseModel):
    text: str
    data: dict
    chart_type: str


class DeleteRequest(BaseModel):
    ids: List[str]
    delete_all: Optional[bool] = False


class UpsertResponse(BaseModel):
    ids: List[str]


class DeleteResponse(BaseModel):
    success: bool


class ChatResponse(BaseModel):
    response: QueryResult = Field(..., description='''Response text, chart_type in ["None", "Line", "Pie", "Bar"]''')

    class Config:
        schema_extra = {
            "example": {
                        "response": {
                            "text": "2023年4月1日-6日基金整体交易金额总和为 39085.83",
                            "data": {
                              "日期": [
                                "2023-04-01",
                                "2023-04-02",
                                "2023-04-03",
                                "2023-04-04",
                                "2023-04-05",
                                "2023-04-06"
                              ],
                              "基金整体交易金额": [
                                "2057.93",
                                "7638.26",
                                "6230.90",
                                "6015.42",
                                "9260.09",
                                "7883.23"
                              ]
                            },
                            "chart_type": "Line"
                          }
                    }
                }


class ChatRequest(BaseModel):
    question: str = Field(..., description="Question text", example="2023年4月1日-6日基金整体交易金额是多少？帮我做一个折线图呈现走势")