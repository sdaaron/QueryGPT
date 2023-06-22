from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackManager
from langchain.chat_models import ChatOpenAI
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.agents.openai_functions_multi_agent.base import OpenAIMultiFunctionsAgent
from langchain.agents import Tool, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from langchain.prompts.base import BasePromptTemplate

from agents.conv_prompt import CONV_PREFIX, CONV_SUFFIX
from tools.function_query_tool import (
                 QueryTool,
                 AverageOrderValue,
                 YearOverYear,
                 MonthOverMonth,
                 PlotCharts,
                 FilterData,
                 CalculateRatio)
from agents.dataStore import DataStore


@dataclass
class FunctionQueryAgent:
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

    def __init__(self, llm: BaseLanguageModel,
                 data_store: DataStore,
                 args: Any,
                 callback_manager: Optional[BaseCallbackManager] = None,
                 **kwargs: Dict[str, Any]):
        self.llm = llm
        self.data_store = data_store
        self.verbose = args.verbose
        self.callback_manager = callback_manager
        try:
            import pandas as pd
        except ImportError:
            raise ValueError(
                "pandas package not found, please install with `pip install pandas`"
            )
        tools = [QueryTool(data_store=data_store),
                 AverageOrderValue(data_store=data_store),
                 YearOverYear(data_store=data_store),
                 MonthOverMonth(data_store=data_store),
                 PlotCharts(data_store=data_store, plot_image=args.plot_image),
                 FilterData(llm=ChatOpenAI(), df=data_store.df),
                 CalculateRatio(data_store=data_store)]
        prompt = self.create_prompt(data_store.df)
        agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
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

    def predict(self, query: str) -> dict:

        response = self.agent_executor.run(input=query, chat_history=[])
        if self.data_store.query_df["query"]:
            query_data = self.data_store.gather()
            query_data_markdown = self.data_store.gather(return_type="markdown")
        else:
            query_data = {"日期": []}
            query_data_markdown = ""
        self.data_store.reset()
        return {"text": response,
                "markdown": query_data_markdown,
                "data": query_data}

    @classmethod
    def create_prompt(cls, query_df: Any) -> BasePromptTemplate:
        now = datetime.now().strftime("%Y-%m-%d")
        messages = [
            SystemMessage(content=f'''You are a helpful AI assistant.You will proficient in utilizing various tools to answer questions effectively. 
                                        Your all calculation results will from the tools and compile these results to the answer the question.
                                        You should NEVER call other functions before "data_query" has been called in the conversation.
                                        You will infer all the correct time and column names based on the question, and extract the time and column names from the question according to the dataframe.
                                        If the provided column name is not correct, you will input the column name from the dataframe that is most similar to it.
                                        All column names MUST in the following dataframe::
                                        {query_df.head(1).to_markdown()}
                                        The current date is {now}.'''),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
        input_variables = ["input", "agent_scratchpad"]
        return ChatPromptTemplate(input_variables=input_variables, messages=messages)
