import re


def res_parser(response: str, api_endpoint: str) -> str:
    response = response.replace("[", "").replace("]", "").replace("!", "").replace("(", ":").replace(")", "")
    for image_filename in re.findall("images/.*?.png", response):
            response = re.sub("images/.*?.png", f"![image]({api_endpoint}/{image_filename})", response)
    return response