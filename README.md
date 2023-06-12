## Quickstart
Follow these steps to quickly set up and run.
1. Install Python 3.10, if not already installed.
2. Clone this repository
3. Navigate to the cloned repository directory: cd /path/to/DataBot
4. Install poetry: ```pip install poetry```
5. Create a new virtual environment with Python 3.10: ```poetry env use python3.10```
6. Activate the virtual environment:```poetry shell```
7. Install app dependencies:```poetry install```
8. Set the required environment variables in *.env.example* and rename  the file to *.env*
```
# openai
OPENAI_API_KEY=xxx

# proxy
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890

# Azure OpenAI
OPENAI_API_TYPE=azure
OPENAI_API_VERSION=2023-05-15
OPENAI_API_BASE=xxx
OPENAI_API_KEY=xxx
```
9. Run with the csv file API :```poetry run python main.py --host xx --port xxx --csv_path xxx.csv``` or
Run with the excel file API: ```poetry run python main.py --host xx --port xxx --excel_path xxx.xlsx```