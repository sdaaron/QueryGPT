from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import threading
import queue
from langchain.chains import LLMChain
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


class ThreadedGenerator:
    def __init__(self):
        self.queue = queue.Queue()

    def __iter__(self):
        return self

    def __next__(self):
        item = self.queue.get()
        if item is StopIteration: raise item
        return item

    def send(self, data):
        self.queue.put(data)

    def close(self):
        self.queue.put(StopIteration)


def generate_serially(message: str):
    llm = OpenAI(temperature=0.9)
    prompt = PromptTemplate(
        input_variables=[],
        template="我想让你扮演一个基于文本的冒险游戏。我在这个基于文本的冒险游戏中扮演一个角色。请尽可能具体地描述角色所看到的内容和环境，并在游戏输出的唯一代码块中回复，而不是其他任何区域。我将输入命令来告诉角色该做什么，而你需要回复角色的行动结果以推动游戏的进行。我的第一个命令是'醒来'，请从这里开始故事",
    )
    print('message1: ', message)
    chain = LLMChain(llm=llm, prompt=prompt)
    resp = chain.run(product="toothpaste")
    print(resp)


simple_question_template = """
我想让你扮演一个基于文本的冒险游戏。我在这个基于文本的冒险游戏中扮演一个角色。请尽可能具体地描述角色所看到的内容和环境，并在游戏输出的唯一代码块中回复，而不是其他任何区域。我将输入命令来告诉角色该做什么，而你需要回复角色的行动结果以推动游戏的进行。
我想要你根据以下问题编写故事：
{question}
并且在回答末尾附带你对答案的心情描述词。
"""


# sse response streaming
def generate_simple_question(question: str):
    llm = OpenAI(streaming=True, callbacks=[StreamingStdOutCallbackHandler()], temperature=0)
    prompt = PromptTemplate(
        input_variables=['question'],
        template=simple_question_template,
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    resp = chain.run(question=question)
    return resp


class ChainStreamHandler(StreamingStdOutCallbackHandler):
    def __init__(self, gen):
        super().__init__()
        self.gen = gen

    def on_llm_new_token(self, token: str, **kwargs):
        self.gen.send(token)


def llm_thread(g, prompt):
    try:
        chat = ChatOpenAI(
            verbose=True,
            streaming=True,
            callback_manager=BaseCallbackManager([ChainStreamHandler(g)]),
            temperature=0.7,
        )
        chat([
            # SystemMessage(content="你是一个狂欢小丑，邪恶而残忍，你需要扮演好这个角色"),
            HumanMessage(content=prompt)
        ])

    finally:
        g.close()


def chat(question: str):
    g = ThreadedGenerator()
    prompt = PromptTemplate(
        input_variables=['question'],
        template=simple_question_template,
    )
    threading.Thread(target=llm_thread, args=(g, prompt.format(question=question))).start()
    return g
