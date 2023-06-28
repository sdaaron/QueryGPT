import ast
from typing import Any, Optional
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackManager
from langchain.agents import Tool
from agents.base import create_query_dataframe_agent


def double_query_check_tool(llm: BaseLanguageModel, df: Any, verbose: bool = True,
                            callback_manager: Optional[BaseCallbackManager] = None) -> Tool:
    agent = create_query_dataframe_agent(llm, df, verbose=verbose, callback_manager=callback_manager)

    def run(question: str) -> dict:
        result = agent.run(question + ",并且打印查询的数据结果。")
        try:
            result = ast.literal_eval(str(result))
            _, _ = result['日期'], result['summary']
            return result
        except:
            return {'日期': [], 'summary': []}

    query_tool = Tool(
        name='data_query',
        func=run,
        description="Useful for when you need to retrieve the query results."
                    "Input MUST be the original question.",
        return_direct=True
    )
    return query_tool