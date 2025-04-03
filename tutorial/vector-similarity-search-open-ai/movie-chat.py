import os
from typing import List
from dotenv import load_dotenv

from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import Redis as RedisVectorStore
from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

API_KEY = os.getenv('API_KEY')
RESOURCE_ENDPOINT = os.getenv('RESOURCE_ENDPOINT')
DEPLOYMENT_NAME = os.getenv('DEPLOYMENT_NAME')
MODEL_NAME = os.getenv('MODEL_NAME')
REDIS_ENDPOINT = os.getenv('REDIS_ENDPOINT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

# we will use Azure OpenAI as our embeddings provider
embedding = AzureOpenAIEmbeddings(
    azure_endpoint=RESOURCE_ENDPOINT,
    azure_deployment=DEPLOYMENT_NAME,
    openai_api_key=API_KEY,
    openai_api_version='2024-03-01-preview',
    show_progress_bar=True,
    chunk_size=16)

# name of the Redis search index to create
index_name = "movieindex"

# create a connection string for the Redis Vector Store. Uses Redis-py format: https://redis-py.readthedocs.io/en/stable/connections.html#redis.Redis.from_url
# This example assumes TLS is enabled. If not, use "redis://" instead of "rediss://
redis_url = "rediss://:" + REDIS_PASSWORD + "@"+ REDIS_ENDPOINT

vectorstore = RedisVectorStore.from_existing_index(
    embedding=embedding,
    redis_url=redis_url,
    index_name=index_name,
    schema="redis_schema.yaml"
)

# Initialize the LLM
llm = AzureChatOpenAI(
    azure_endpoint=RESOURCE_ENDPOINT,
    azure_deployment='gpt-4o-mini',
    api_key=API_KEY,
    openai_api_version="2024-09-01-preview"
)

# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "human",
            """You are a movie buff who can answer questions about movies, make suggestions, summarise key facts, and provide other useful movie information. Use the following information as context to build your answer. If you are unsure, just say 'I'm unsure". Only discuss movies from the context provided. Don't discuss other topics not related to the movies.
{question} 
Context: {context}
Answer:""",
        ),
    ]
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Initialize chat history
chat_history = []

while True:
    question = input("What's your question about movie(s)? ")
    if question == 'q':
        print('Bye!')
        break
    elif question == '':
        # Clear chat history
        chat_history = []
        print('Starting a new conversation...')
    else:
        # Add question to chat history
        chat_history.append(f"Question: {question}")
        
        # Combine chat history into context
        formated_chat_history = "\n".join(chat_history)
        
        # Get the answer
        answer = rag_chain.invoke(formated_chat_history)
        
        # Add answer to chat history
        chat_history.append(f"Answer: {answer}")
        
        print(f'\nAnswer:\n{answer}')