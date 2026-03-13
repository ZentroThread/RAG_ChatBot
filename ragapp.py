from pydoc import doc

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant", # Llama-3.1 
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

prompt = ChatPromptTemplate.from_template(
"""
You are an assistant that helps users retrieve information from a clothing and textiles database.

Core Behavior:
You only answer questions using the information provided in the Context section.

Rules:

1. Use ONLY the information in the Context.
2. Do NOT create, assume, or invent any data.
3. Do NOT use outside knowledge.
4. If the answer cannot be found in the Context, reply:
   Sorry, that information is not available in the database.
5. If the Context is empty, reply:
   Sorry, the database does not contain information related to your request.
6. If the user does not have permission to access the requested information, reply:
   Sorry, you do not have permission to access this information.
7. If the question is not related to clothing, textiles, attire, rentals, customers, orders, or inventory stored in the database, reply:
   I can only help with clothing and textile database information.
8. Never reveal ID columns or ID values.
9. Use names or codes instead of IDs.
10. Do NOT guess missing values.
11. Do NOT generate sample or fake data.

Assistant Identity:
If the user asks who you are or what you do, reply:
I am a clothing and textiles database assistant. I help you find information about clothing items, textile products, rentals, customers, and inventory stored in the database.

Formatting Rules:

* Use clear and simple professional English.
* Return plain text only.
* Do not use bold, italics, stars, or special characters.
* Keep responses short and clearly structured.

Context:
{context}

Question:
{question}

Answer:
"""
)


def rag_answer(vectorstore, question, role):

    print("Running similarity search...")

    docs = vectorstore.similarity_search(question, k=30)

    
    if role == "CUSTOMER":
        restricted_tables = ["attire", "category"]

    elif role == "CASHIER":
        restricted_tables = ["attire", "attire_rent"]
    
    elif role == "SALES_ASSISTANT":
        restricted_tables = ["attire", "category"]

    elif role == "OWNER":
        restricted_tables = None 

    else:
        return "Invalid role."

    filtered_docs = []

    for doc in docs:
        text = doc.page_content.lower()

        if restricted_tables is None:
 
            filtered_docs.append(doc)
        else:
            for table in restricted_tables:
                if f"table: {table}" in text:
                    filtered_docs.append(doc)
                    break

    if not filtered_docs:
        return "The requested information is not available in the database or you do not have permission to access it."

    print(" Documents retrieved:", len(filtered_docs))

    context = "\n".join(doc.page_content for doc in filtered_docs)

    role_instruction = ""

    if role == "OWNER":
        role_instruction = "You can access all information."
    elif role == "CASHIER":
        role_instruction = "Only answer questions about attire, attire_rent, and billing."
    elif role == "CUSTOMER":
        role_instruction = "Only answer about attire, availability, price, and attire category."
    elif role == "SALES_ASSISTANT":
        role_instruction = "Only answer about attire, category, and inventory."
    print("Sending request to LLM...")

    response = llm.invoke(
        prompt.format(
            context=context,
            question=question + "\nUser Role: " + role_instruction
        )
    )

    print("LLM response received")

    return response.content