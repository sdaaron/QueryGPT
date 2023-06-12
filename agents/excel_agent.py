import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains import LLMChain
from langchain.agents import Tool, AgentExecutor
from langchain.agents import ConversationalChatAgent
from langchain.memory import ConversationBufferMemory
from langchain.agents.agent_toolkits.pandas.base import create_pandas_dataframe_agent

from agents.conv_prompt import CONV_PREFIX, CONV_SUFFIX
from agents.base import create_query_dataframe_agent
from tools.double_query_check import double_query_check_tool
from tools.chart_type_prompt import CHART_TYPE_PROMPT


@dataclass
class ExcelAgent:
    agent_executor: Optional[AgentExecutor] = None
    prefix: str = CONV_PREFIX
    suffix: str = CONV_SUFFIX
    input_variables: Optional[List[str]] = None
    return_intermediate_steps: bool = False
    max_iterations: Optional[int] = 15
    max_execution_time: Optional[float] = None
    early_stopping_method: str = "force"
    agent_executor_kwargs: Optional[Dict[str, Any]] = None
    include_df_in_prompt: Optional[bool] = True

    def _get_pandas_tool(self) -> Tool:
        pandas_agent_df = create_pandas_dataframe_agent(self.llm,
                                                        self.df, verbose=self.verbose, callback_manager=self.callback_manager)
        pandas_tool = Tool(
            name='Dataframe analysis tool',
            func=pandas_agent_df.run,
            description="Useful for when you need to answer question about a Dataframe and retrieve analysis results."
                        "The input will be an accurate description of the data you need,"
                        "such as the total sum of the second column or the average of the first five columns."
        )
        return pandas_tool

    def _get_plot_tool(self) -> Tool:
        plot_agent_df = create_query_dataframe_agent(self.llm, self.df, verbose=self.verbose,
                                                          max_iterations=self.max_iterations, callback_manager=self.callback_manager)
        plot_tools = Tool(
            name='Plot Data frame tool',
            func=plot_agent_df.run,
            description="Useful for when you need to plot Pandas Dataframe."
                        "Input will be the description of what kind figures you want, "
                        "output will be the saved figure path."
        )

        return plot_tools

    def __init__(self, llm: BaseLanguageModel,
                       df: Any,
                       verbose: bool = False,
                       callback_manager: Optional[BaseCallbackManager] = None,
                       **kwargs: Dict[str, Any]):
        self.llm = llm
        self.df = df
        self.verbose = verbose
        self.callback_manager = callback_manager
        try:
            import pandas as pd
        except ImportError:
            raise ValueError(
                "pandas package not found, please install with `pip install pandas`"
            )

        if not isinstance(self.df, pd.DataFrame):
            raise ValueError(f"Expected pandas object, got {type(self.df)}")
        query_tool = double_query_check_tool(self.llm, self.df, self.verbose, self.callback_manager)
        tools = [query_tool]
        conv_prompt = ConversationalChatAgent.create_prompt(
            tools, system_message=self.prefix, human_message=self.suffix)

        llm_chain = LLMChain(
            llm=self.llm,
            prompt=conv_prompt,
            callback_manager=self.callback_manager,
        )
        self.chart_parser_llm = LLMChain(llm=llm, prompt=CHART_TYPE_PROMPT)
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
            # memory=memory,
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
            response = self.agent_executor.run(input=query, chat_history=[])
        except ValueError as e:
            response = str(e)
            if response.startswith("Could not parse LLM output: `"):
                response = response.removeprefix("Could not parse LLM output: `").removesuffix("`")
        return response

    def get_chart_type(self, query: str) -> str:
        response = self.chart_parser_llm.predict(input=query)
        _, chart_type = response.split("chart_type: ")
        if chart_type in ["None", "Line", "Pie", "Bar"]:
            return chart_type
        else:
            return "None"
