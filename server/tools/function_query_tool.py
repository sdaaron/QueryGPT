import json
from typing import Any, Type, Optional, List, Dict
from pydantic import BaseModel, Extra, Field, root_validator
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools.base import BaseTool
from langchain.llms.base import BaseLanguageModel
from langchain.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from langchain.agents import AgentExecutor

from agents.base import create_query_dataframe_agent
from agents.dataStore import DataStore
from agents.query_prompt import FUNCTION_QUERY_PREFIX


class QueryToolInput(BaseModel):
    time_series: list = Field(..., description="""Will be the current consecutive time series: [start_date, end_date], e.g. ["2021-03-01", "2021-03-15"]""")
    date_list: list = Field(..., description='''Will be the single date or multiple non-consecutive dates, e.g. ["2021-03-01", "2021-03-15", "2021-05-15", ...]''')
    column_names: list = Field(..., description='''Must be the column names of dataframe , e.g. ["交易人数", "交易金额"]''')


class QueryTool(BaseTool):
    name: str = "data_query"
    description: str = """
    Get data of a specific time from a dataframe.
    """
    args_schema: Type[BaseModel] = QueryToolInput
    data_store: DataStore = None

    def _run(
            self,
            time_series: list,
            column_names: list,
            date_list: list = None,
            run_manager: Optional[CallbackManagerForToolRun] = None,
            ) -> str:
        result = self.data_store.query(time_series, column_names, date_list)
        return result

    async def _arun(
            self,
            time_series: list,
            date_list: list,
            column_names: list,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        result = self.data_store.query(time_series, column_names, date_list)
        return result


class AverageOrderValueInput(BaseModel):
    dividend_name: str = Field(..., description="""The name of the column to which the dividend""")
    divisor_name: str = Field(..., description='''The name of the column to which the divisor''')


class AverageOrderValue(BaseTool):
    name: str = "calculate_average_value"
    description: str = """
    You should use this function to calculate the average value(客单价).
    """
    args_schema: Type[BaseModel] = AverageOrderValueInput
    data_store: DataStore = None

    def _run(
        self,
        dividend_name: str,
        divisor_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        result = self.data_store.average_order_value(dividend_name, divisor_name)
        return result

    async def _arun(
            self,
            dividend_name: str,
            divisor_name: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        result = self.data_store.average_order_value(dividend_name, divisor_name)
        return result


class YearOverYearInput(BaseModel):
    time_series: list = Field(..., description="""MUST be the time series from the previous year, e.g. ["2020-03-01", "2020-03-15"]""")
    column_names: list = Field(..., description='''Will be the dataframe column names, e.g. ["交易人数", "交易金额"]''')


class YearOverYear(BaseTool):
    name: str = "calculate_year_comparison"
    description: str = """
    Useful to you should calculate the year-over-year comparison (同比).
    """
    args_schema: Type[BaseModel] = YearOverYearInput
    data_store: DataStore = None

    def _run(self,
             time_series: list,
             column_names: list,
             run_manager: Optional[CallbackManagerForToolRun] = None,
             ) -> str:
        result = self.data_store.calculate_growth_rate(time_series, column_names)
        return result

    async def _arun(self,
                    time_series: list,
                    column_names: list,
                    run_manager: Optional[CallbackManagerForToolRun] = None,
                    ) -> str:
        result = self.data_store.calculate_growth_rate(time_series, column_names)
        return result


class MonthOverMonthInput(BaseModel):
    time_series: list = Field(..., description="""MUST be the time series from the previous period: [start_date, end_date], e.g. ["2021-02-13", "2021-02-28"]""")
    column_names: list = Field(..., description='''Will be the dataframe column names, exclude date column, e.g. ["交易人数", "交易金额"]''')


class MonthOverMonth(BaseTool):
    name: str = "calculate_period_comparison"
    description: str = """
    Useful to you should calculate the data from the previous month or another period of time comparison(环比).
    """
    args_schema: Type[BaseModel] = YearOverYearInput
    data_store: DataStore = None

    def _run(self,
             time_series: list,
             column_names: list,
             run_manager: Optional[CallbackManagerForToolRun] = None,
             ) -> str:
        result = self.data_store.calculate_growth_rate(time_series, column_names)
        return result

    async def _arun(self,
                    time_series: list,
                    column_names: list,
                    run_manager: Optional[CallbackManagerForToolRun] = None,
                    ) -> str:
        result = self.data_store.calculate_growth_rate(time_series, column_names)
        return result


class PlotChartsInput(BaseModel):
    chart_title: str = Field(..., description="""Will be the chart title name.""")
    chart_type: str = Field(..., description="""Will be the chart type you should plot, "enum": ["line", "pie", "bar", "scatter"]""")


class PlotCharts(BaseTool):
    name: str = "plot_charts"
    description: str = """
    Useful to you should plot a chart.
    """
    args_schema: Type[BaseModel] = PlotChartsInput
    data_store: DataStore = None
    plot_image: bool = True

    def _run(self,
             chart_title: str,
             chart_type: str,
             run_manager: Optional[CallbackManagerForToolRun] = None,
             ) -> str:
        result = self.data_store.plot_data(chart_title, chart_type, self.plot_image)
        return result

    async def _arun(self,
                    chart_title: str,
                    chart_type: str,
                    run_manager: Optional[CallbackManagerForToolRun] = None,
                    ) -> str:
        result = self.data_store.plot_data(chart_title, chart_type, self.plot_image)
        return result


class FilterDataInput(BaseModel):
    description: str = Field(..., description="""Will be the detailed and accurate description, like column names and specific conditions.""")
    time_series: list = Field(..., description="""Will be the current time series: [start_date, end_date], e.g. ["2021-02-13", "2021-02-28"]""")


class FilterData(BaseTool):
    llm: BaseLanguageModel
    agent: AgentExecutor = Field(init=False)
    df: Any = None
    prefix: str = '''You are working with a pandas dataframe in Python. The name of the dataframe is `df`.
                    You will answer the question in detailed.'''

    name: str = "get_specified_data"
    description: str = """
    Useful to the data_query is unable to provide the desired results, you can use this function to get specified data, filter data or compare data.
    """
    args_schema: Type[BaseModel] = FilterDataInput

    @root_validator(pre=True)
    def initialize_llm_chain(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if "agent" not in values:
            # values["agent"] = create_pandas_dataframe_agent(
            #     llm=values.get("llm"),
            #     df=values.get("df"),
            #     verbose=True,
            #     prefix=values.get("prefix"),
            #     agent_type=AgentType.OPENAI_FUNCTIONS,
            # )
            values["agent"] = create_query_dataframe_agent(
                llm=values.get("llm"),
                df=values.get("df"),
                prefix=FUNCTION_QUERY_PREFIX,
                verbose=True,
            )
        return values

    def _run(self,
             description: str,
             time_series: list,
             run_manager: Optional[CallbackManagerForToolRun] = None,
             ) -> str:
        try:
            result = self.agent.run("请计算{}至{}，{}".format(time_series[0], time_series[1], description))
        except:
            result = ""
        return json.dumps({"result": result})

    async def _arun(self,
                    description: str,
                    run_manager: Optional[CallbackManagerForToolRun] = None,
                    ) -> str:
        result = self.agent.arun(description)
        return json.dumps({"result": result})


class CalculateRatioInput(BaseModel):
    time_series: list = Field(..., description="""Will be the current consecutive time series: [start_date, end_date], e.g. ["2021-03-01", "2021-03-15"]""")
    base_name: str = Field(..., description='''Will be the baseline column name. e.g. "交易人数"''')
    channel_names: list = Field(..., description='''Will be other channel column names in dataframe of the baseline column, e.g. ["交易人数", "交易金额"]''')


class CalculateRatio(BaseTool):
    name: str = "calculate_ratio"
    description: str = """
    Useful to you should perform calculating percentages and channel ratio.
    """
    args_schema: Type[BaseModel] = CalculateRatioInput
    data_store: DataStore = None

    def _run(self,
             time_series: list,
             base_name: str,
             channel_names: list,
             run_manager: Optional[CallbackManagerForToolRun] = None,
             ) -> str:
        result = self.data_store.channel_ratio(time_series, base_name, channel_names)
        return result

    async def _arun(self,
                    time_series: list,
                    base_name: str,
                    channel_names: list,
                    run_manager: Optional[CallbackManagerForToolRun] = None,
                    ) -> str:
        result = self.data_store.channel_ratio(time_series, base_name, channel_names)
        return result
