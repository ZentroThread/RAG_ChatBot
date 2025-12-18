from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

db = None
https://github.com/ZentroThread/RAG_ChatBot.git
def connectDatabase():
    global db
    mysql_uri = f"mysql+mysqlconnector://root:@localhost:3306/ragmysqldb"
    db = SQLDatabase.from_uri(mysql_uri)

def runQuery(query):
    return db.run(query) if db else "Please connect to Database"

def getDatabaseSchema():
    return db.get_table_info() if db else "Please Connect to Database"

llm = ChatOpenAI(
    model='gpt-3.5-turbo',
    api_key=api_key
)

def getQueryFromLLM(question):
    template = """
    Below is the schema of MYSQL database, read the schema carefully and answer user's question in the form of SQL query.

    {schema}

    question: {question}
    SQL query:
    Please only provide the SQL query and nothing else
    """

    prompt = ChatPromptTemplate.from_template(template)

    chain = prompt | llm

    response = chain.invoke({
        "question": question,
        "schema": getDatabaseSchema()
    })
    return response.content

def getResponseForQueryResult(question, query, result):
    template2 = """
    Below is the schema of MYSQL database, read the schema carefully about the table and column names and convert the result into natural language

    {schema}

    for example:
    question: How many brands we have in the database?
    SQL query: SELECT COUNT(DISTINCT brand_id) AS total_brands FROM brands;
    Result: [(5,)]
    Response: There are brands in the database
    
    Now your turn to write response in natural language from the given result : 

    question: {question}
    SQL query: {query}
    Result: {result}
    Response: 

    """

    prompt2 = ChatPromptTemplate.from_template(template2)
    chain2 = prompt2 | llm

    response = chain2.invoke({
        "question": question,
        "schema": getDatabaseSchema(),
        "query": query,
        "result": result
    })
    return response.content

connectDatabase()

# question= "How many brands we have in the database ?"
# query = getQueryFromLLM(question)
# result = runQuery(query)
#
# response = getResponseForQueryResult(question, query, result)
# print(response)

# print(getDatabaseSchema())

st.set_page_config(
    page_icon="🤖",
    page_title="Chat with MYSQL DB",
    layout= "centered"
)

question = st.chat_input('Chat with the Mysql Database')

if question:
    st.chat_message('user').markdown(question)
    query = getQueryFromLLM(question)
    result = runQuery(query)
    response = getResponseForQueryResult(question, query, result)
    st.chat_message('assistant').markdown(response)


