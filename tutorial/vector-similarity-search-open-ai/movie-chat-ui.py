import os
from typing import List
from dotenv import load_dotenv

from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import Redis as RedisVectorStore
from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

import streamlit as st

load_dotenv()

API_KEY = os.getenv('API_KEY')
RESOURCE_ENDPOINT = os.getenv('RESOURCE_ENDPOINT')
DEPLOYMENT_NAME = os.getenv('DEPLOYMENT_NAME')
MODEL_NAME = os.getenv('MODEL_NAME')
REDIS_ENDPOINT = os.getenv('REDIS_ENDPOINT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

# Function to load the vector store
# This function creates a connection to the Redis Vector Store and loads the index
# It uses the Azure OpenAI embeddings for vectorization
# and the Redis-py format for the connection string
def load_vector_store(aoai_resource_endpoint, aoai_deployment_name, aoai_api_key, redis_endpoint, redis_password):
    # we will use Azure OpenAI as our embeddings provider
    embedding = AzureOpenAIEmbeddings(
        azure_endpoint=aoai_resource_endpoint,
        azure_deployment=aoai_deployment_name,
        openai_api_key=aoai_api_key,
        openai_api_version='2024-03-01-preview',
        show_progress_bar=True,
        chunk_size=16)

    # Name of the Redis search index to create
    index_name = "movieindex"

    # Create a connection string for the Redis Vector Store. Uses Redis-py format: https://redis-py.readthedocs.io/en/stable/connections.html#redis.Redis.from_url
    # This example assumes TLS is enabled. If not, use "redis://" instead of "rediss://
    redis_url = "rediss://:" + redis_password + "@"+ redis_endpoint

    # Initialize the Redis Vector Store
    vectorstore = RedisVectorStore.from_existing_index(
        embedding=embedding,
        redis_url=redis_url,
        index_name=index_name,
        schema="redis_schema.yaml"
    )

    return vectorstore

# Function to format the documents
# This function takes a list of documents and formats them into a single string
# It extracts the page content from each document and joins them with double newlines
# This is useful for displaying the context to the LLM
# in a readable format
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def get_system_prompt():
    return """You are a movie buff who can answer questions about movies, make suggestions, summarise key facts, and provide other useful movie information. Use the following information as context to build your answer. If you are unsure, just say 'I'm unsure. Only discuss movies from the context provided. Don't discuss other topics not related to the movies."""

st.title("Movie Chatbot")
st.write("Ask me anything about movies!")
st.write("""Type your movie question or press "Enter"" to start a new conversation.""")

# Initialize the LLM for chat
llm = AzureChatOpenAI(
    azure_endpoint=RESOURCE_ENDPOINT,
    azure_deployment='gpt-4o-mini',
    api_key=API_KEY,
    openai_api_version="2024-09-01-preview"
)

vectorstore = load_vector_store(RESOURCE_ENDPOINT, DEPLOYMENT_NAME, API_KEY, REDIS_ENDPOINT, REDIS_PASSWORD)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})

# Initialize chat history
if "messages" not in st.session_state:
    # system prompt includes table information, rules, and prompts the LLM to produce
    # a welcome message to the user.
    st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]

print("here 4")

promptTemplate = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a movie buff who can answer questions about movies, make suggestions, summarise key facts, and provide other useful movie information. Use the following information as context to build your answer. If you are unsure, just say 'I'm unsure". Only discuss movies from the context provided. Don't discuss other topics not related to the movies."""
        ),
        (
            "human",
            """
            Context: {context}
            {question}
            """
        ),
        (
            "assistant",
            """Answer:"""
        )
    ]
)

question = st.chat_input("What's your question about movie(s)?")

if question:
    if question == 'q':
        # Clear chat history
        st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]
        with st.chat_message("assistant"):
            st.write("Starting a new conversation...")
    else:
        # Add question to chat history
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("user"):
            st.write(question)
        
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | promptTemplate
            | llm
            | StrOutputParser()
        )

        # Get the answer
        answer = rag_chain.invoke(question)

        print(f"{answer}")
        
        # Add answer to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        with st.chat_message("assistant"):
            st.write(answer)
