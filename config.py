import os
from dotenv import load_dotenv
from langchain_community.llms.ollama import Ollama
# from langchain_ollama.llms import OllamaLLM

load_dotenv()

HTTP_PORT = int(os.environ.get('HTTP_PORT', "8000"))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = f"{BASE_DIR}/data/"
LLM = Ollama(model = "llama3.1:8b-instruct-q4_0")
