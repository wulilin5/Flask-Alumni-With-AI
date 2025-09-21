from dotenv import load_dotenv
import os

dotenv_path = r"D:\wll\job\wll_xm\flask-alumni-ai-with-search\python-flask-user-crud-main\.env"
load_dotenv(dotenv_path, override=True)
print("读取到的 LLM_API_KEY:", os.getenv("LLM_API_KEY"))
