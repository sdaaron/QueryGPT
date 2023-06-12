from langchain import PromptTemplate

prompt_template = '''You will extract and output the type of chart from the word in the {input}, and the output must be one of the following types:
                    None, Line, Pie, Bar. 
                    You answer will use following format:
                    chart_type: put the chart type here
                    '''

CHART_TYPE_PROMPT = PromptTemplate.from_template(prompt_template)