from langchain_ollama import ChatOllama

llm = ChatOllama(
    model = "llama3.1:8b-instruct-q4_0",
    temperature = 0.5,
)

messages = [
    ("human", "Return the words Hello World!"),
]
for chunk in llm.stream(messages):
    print(chunk)