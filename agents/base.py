"""Agent for working with pandas objects."""
from typing import Any, Dict, List, Optional

from langchain.agents.agent import AgentExecutor
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains.llm import LLMChain
from langchain.tools.python.tool import PythonAstREPLTool
from agents.query_prompt import (
    PREFIX,
    SUFFIX_NO_DF,
    SUFFIX_WITH_DF,
    FORMAT_INSTRUCTIONS
)
from agents.output_parser import MRKLOutputParser


def create_query_dataframe_agent(
    llm: BaseLanguageModel,
    df: Any,
    callback_manager: Optional[BaseCallbackManager] = None,
    prefix: str = PREFIX,
    suffix: Optional[str] = None,
    input_variables: Optional[List[str]] = None,
    verbose: bool = False,
    return_intermediate_steps: bool = False,
    max_iterations: Optional[int] = 15,
    max_execution_time: Optional[float] = None,
    early_stopping_method: str = "force",
    agent_executor_kwargs: Optional[Dict[str, Any]] = None,
    include_df_in_prompt: Optional[bool] = True,
    **kwargs: Dict[str, Any],
) -> AgentExecutor:
    """Construct a pandas agent from an LLM and dataframe."""
    try:
        import pandas as pd
        import datetime

    except ImportError:
        raise ValueError(
            "pandas package not found, please install with `pip install pandas`"
        )

    try:
        import matplotlib.pyplot as plt
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
    except ImportError:
        raise ValueError(
            "matplotlib package not found, please install with `pip install matplotlib`"
        )

    if not isinstance(df, pd.DataFrame):
        raise ValueError(f"Expected pandas object, got {type(df)}")
    if include_df_in_prompt is not None and suffix is not None:
        raise ValueError("If suffix is specified, include_df_in_prompt should not be.")
    if suffix is not None:
        suffix_to_use = suffix
        if input_variables is None:
            input_variables = ["df", "input", "agent_scratchpad"]
    else:
        if include_df_in_prompt:
            suffix_to_use = SUFFIX_WITH_DF
            input_variables = ["df", "input", "agent_scratchpad"]
        else:
            suffix_to_use = SUFFIX_NO_DF
            input_variables = ["input", "agent_scratchpad"]
    df_copy = df.copy()
    tools = [PythonAstREPLTool(locals={"df": df_copy, "pd": pd, "datatime": datetime},
                               return_direct=True
                               )]
    now = pd.Timestamp.now().strftime("%Y-%m-%d")
    prompt = ZeroShotAgent.create_prompt(
        tools, prefix=prefix.format(now=now), suffix=suffix_to_use, format_instructions=FORMAT_INSTRUCTIONS,
        input_variables=input_variables
    )
    if "df" in input_variables:
        partial_prompt = prompt.partial(df=str(df.head(1).to_markdown()))
    else:
        partial_prompt = prompt

    llm_chain = LLMChain(
        llm=llm,
        prompt=partial_prompt,
        callback_manager=callback_manager,
    )
    tool_names = [tool.name for tool in tools]
    agent = ZeroShotAgent(
        llm_chain=llm_chain,
        allowed_tools=tool_names,
        callback_manager=callback_manager,
        output_parser=MRKLOutputParser(),
        **kwargs,
    )
    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        callback_manager=callback_manager,
        verbose=verbose,
        return_intermediate_steps=return_intermediate_steps,
        max_iterations=max_iterations,
        max_execution_time=max_execution_time,
        early_stopping_method=early_stopping_method,
        handle_parsing_errors=True,
        **(agent_executor_kwargs or {}),
    )