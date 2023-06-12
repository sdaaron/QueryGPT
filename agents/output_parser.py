import re
from typing import Union

from langchain.agents.agent import AgentOutputParser
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from agents.query_prompt import FORMAT_INSTRUCTIONS

FINAL_ANSWER_ACTION = "Final Answer:"


class MRKLOutputParser(AgentOutputParser):
    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        if FINAL_ANSWER_ACTION in text:
            return AgentFinish(
                {"output": text.split(FINAL_ANSWER_ACTION)[-1].strip()}, text
            )
        # \s matches against tab/newline/whitespace
        regex = (
            r"Action\s*\d*\s*:[\s]*(.*?)[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        )
        if not re.search(
                r"[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)", text, re.DOTALL):
            text = re.sub(r"```(.*?)\n", "Action Input:\n```\n", text, count=1)
        match = re.search(regex, text, re.DOTALL)
        if not match:
            if not re.search(r"Action\s*\d*\s*:[\s]*(.*?)", text, re.DOTALL):
                raise OutputParserException(
                    f"Could not parse LLM output: `{text}`",
                    observation="Invalid Format: Missing 'Action:' after 'Thought:'",
                    llm_output=text,
                    send_to_llm=True,
                )
            elif not re.search(
                r"[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)", text, re.DOTALL
            ):
                action_input_match = re.search(r"Action\s*\d*\s*:[\s]*(.*?)[\s]*```python([\s\S]*?)```", text, re.DOTALL)
                if not action_input_match:
                    raise OutputParserException(
                        f"Could not parse LLM output: `{text}`",
                        observation="Invalid Format:"
                        " Missing 'Action Input:' after 'Action:'",
                        llm_output=text,
                        send_to_llm=True,
                    )
            else:
                raise OutputParserException(f"Could not parse LLM output: `{text}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        return AgentAction(action, action_input.strip(" ").strip('"'), text)

    @property
    def _type(self) -> str:
        return "mrkl"
