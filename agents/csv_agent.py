from datetime import datetime
from typing import Optional, Dict, Any

from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.agents import Tool, AgentExecutor, ConversationalChatAgent
from langchain.agents.agent_toolkits.pandas.base import create_pandas_dataframe_agent
from langchain.memory import ConversationBufferMemory

from agents.matplotlib import create_matplotlib_dataframe_agent
from agents.conv_prompt import CONV_PREFIX, CONV_SUFFIX


def getCurrentDateFun():
    return datetime.now().strftime("%Y-%m-%d")


class CsvAgent:
    agent_executor: Optional[AgentExecutor] = None
    llm: OpenAI = None
    prefix: str = CONV_PREFIX
    suffix: str = CONV_SUFFIX
    agent_executor_kwargs: Optional[Dict[str, Any]] = None
    return_intermediate_steps: bool = False
    max_iterations: Optional[int] = 15
    max_execution_time: Optional[float] = None
    early_stopping_method: str = "force"

    def _get_pandas_tool(self) -> Tool:
        pandas_agent_df = create_pandas_dataframe_agent(self.llm,
                                                        self.df, verbose=self.verbose,
                                                        callback_manager=self.callback_manager)
        pandas_tool = Tool(
            name='Dataframe analysis tool',
            func=pandas_agent_df.run,
            description="Useful for when you need to answer question about a Dataframe and retrieve analysis results."
                        "The input will be an accurate description of the data you need,"
                        "such as the total sum of the second column or the average of the first five columns."
                        "Before you retrieve data,you should make sure the column you obtain must exist in the current input dataframe."
                        "Get the required time series that is use for query based on current time and question."
                        "time format is YYYY-MM-DD"
                        "only retrieve necessary data and time column."
                        "retrieve the data you need, and return the results."
                        "the result must keep column name in dataframe."
                        "if return data rather than draw a figure, you should return a dataframe."

        )
        return pandas_tool

    def _get_plot_tool(self) -> Tool:
        plot_agent_df = create_matplotlib_dataframe_agent(self.llm, self.df, verbose=self.verbose,
                                                          max_iterations=self.max_iterations,
                                                          callback_manager=self.callback_manager)
        plot_tools = Tool(
            name='Plot Data frame tool',
            func=plot_agent_df.run,
            description="Useful for when you need to plot Pandas Dataframe."
                        "Input will be the description of what kind figures you want, "
                        "output will be the saved figure path."
        )

        return plot_tools

    def __init__(self, llm: ChatOpenAI,
                 df: Any,
                 verbose: bool = False,
                 **kwargs: Dict[str, Any]
                 ):
        self.max_iterations = None
        self.callback_manager = None
        self.df = df
        self.llm = llm
        self.verbose = verbose

        try:
            import pandas as pd
        except ImportError:
            raise ValueError(
                "pandas package not found, please install with `pip install pandas`"
            )
        pandas_tool = self._get_pandas_tool()
        plot_tools = self._get_plot_tool()
        tools = [pandas_tool, plot_tools]
        conv_prompt = ConversationalChatAgent.create_prompt(
            tools, system_message=self.prefix, human_message=self.suffix)
        llm_chain = LLMChain(
            llm=self.llm,
            prompt=conv_prompt,
            callback_manager=self.callback_manager,
        )
        tool_names = [tool.name for tool in tools]
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        agent = ConversationalChatAgent(
            llm_chain=llm_chain,
            allowed_tools=tool_names,
            callback_manager=self.callback_manager,
            **kwargs,
        )
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            memory=memory,
            callback_manager=self.callback_manager,
            verbose=self.verbose,
            return_intermediate_steps=self.return_intermediate_steps,
            max_iterations=self.max_iterations,
            max_execution_time=self.max_execution_time,
            early_stopping_method=self.early_stopping_method,
            handle_parsing_errors=True,
            **(kwargs or {}),
        )

    def predict(self, query: str) -> str:
        try:
            response = self.agent_executor.run(input="today is " + getCurrentDateFun() + query)
        except ValueError as e:
            response = str(e)
            if response.startswith("Could not parse LLM output: `"):
                response = response.removeprefix("Could not parse LLM output: `").removesuffix("`")
        return response
