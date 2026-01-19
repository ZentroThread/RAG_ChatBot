from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)

# prompt = PromptTemplate(
#     input_variables = ["context", "question"],
#     template = """
#         You are a clothing and textiles information assistant. You have to retrieve the data from the given database and answer the question in human readable natural language.
#         
#         Answer ONLY using the context below.
# 
#         Context:
#         {context}
# 
#         Question:
#         {question}
# 
#         Answer clearly in simple English.
#     """
# )

prompt = ChatPromptTemplate.from_template(
    """
        You are a clothing and textiles information assistant. You have to retrieve the data from the given database and answer the question in human readable natural language.
        
        Answer ONLY using the context below.

        Context:
        {context}

        Question:
        {question}

        Answer clearly in simple English.
    """
)

def rag_answer(vectorstore, question):
    docs = vectorstore.similarity_search(question, k=30)
    context = "\n".join(doc.page_content for doc in docs)
    
    response = llm.invoke(
        prompt.format(context=context, question=question)
    )
    
    return response.content