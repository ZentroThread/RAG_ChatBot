from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

db = None

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

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def format_chat_history():
    history = ""
    for msg in st.session_state.chat_history:
        history += f"{msg['role']}: {msg['content']}\n"
    return history

def getQueryFromLLM(question):
    template = """
    Below is the schema of MYSQL database, read the schema carefully and answer user's question in the form of SQL query.

    {schema}
    
    Chat History:
    {chat_history}

    Write a syntactically correct MySQL query for the user's latest question.
    Rules:
    - Use only schema tables and columns
    - Return ONLY the SQL query
    - No explanations

    question: {question}
    SQL query:
    Please only provide the SQL query and nothing else
    """

    prompt = ChatPromptTemplate.from_template(template)

    chain = prompt | llm

    response = chain.invoke({
        "question": question,
        "chat_history": format_chat_history(),
        "schema": getDatabaseSchema()
    })
    return response.content.strip()

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
    
    Chat History:
    {chat_history}

    question: {question}
    SQL query: {query}
    Result: {result}
    Response: 

    """

    prompt2 = ChatPromptTemplate.from_template(template2)
    chain2 = prompt2 | llm

    response = chain2.invoke({
        "question": question,
        "chat_history": format_chat_history(),
        "schema": getDatabaseSchema(),
        "query": query,
        "result": result
    })
    return response.content.strip()

connectDatabase()

# question= "How many brands we have in the database ?"
# query = getQueryFromLLM(question)
# result = runQuery(query)
#
# response = getResponseForQueryResult(question, query, result)
# print(response)

# print(getDatabaseSchema())

st.set_page_config(
    page_title="Chat with MySQL DB",
    page_icon="🤖",
    layout="centered"
)

# Show previous messages
for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).markdown(msg["content"])

question = st.chat_input("Chat with the MySQL Database")

if question:
    # Store user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": question
    })
    st.chat_message("user").markdown(question)

    try:
        query = getQueryFromLLM(question)
        result = runQuery(query)
        response = getResponseForQueryResult(question, query, result)

        # Store assistant response
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })

        st.chat_message("assistant").markdown(response)

    except Exception as e:
        st.error(f"Error: {e}")


