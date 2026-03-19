from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

#  Improved Prompt
prompt = ChatPromptTemplate.from_template("""
You are a clothing and textiles database assistant.

Core Behavior:
You only answer questions using the information provided in the Context section.

Rules:
0. If the user greets (hi, hello, hey), respond with:
   Hello! How can I help you with clothing or textile information?

1. Use ONLY the information in the Context.
2. Do NOT create, assume, or invent any data.
3. Do NOT use outside knowledge.
4. If the answer cannot be found in the Context, reply:
   Sorry, that information is not available in the database.
5. If the Context is empty, reply:
   Sorry, the database does not contain information related to your request.
6. If the user does not have permission, reply:
   Sorry, you do not have permission to access this information.
7. If the question is not related to clothing/textiles AND is not a greeting:
   I can only help with clothing and textile database information.
8. Never reveal ID columns or ID values.
9. Use names or codes instead of IDs.
10. Do NOT guess missing values.
11. Do NOT generate fake/sample data.

Assistant Identity:
If asked who you are:
I am a clothing and textiles database assistant.

- Group data by sections
- Each section MUST be on a new line

- Do NOT combine everything in one sentence
- Do NOT repeat items
- Do NOT include explanations
- Only show sections that exist in the context

Formatting Rules:
- Plain text only
- Clean and readable
- No paragraphs

Context:
{context}

Question:
{question}

Answer:
""")

#  Greeting detection (better than simple match)
def is_greeting(text):
    greetings = ["hi", "hello", "hey", "good morning", "good evening"]
    return any(greet in text.lower() for greet in greetings)


def rag_answer(vectorstore, question, role):

    question_clean = question.strip().lower()

    #  1. Handle greetings BEFORE LLM
    if is_greeting(question_clean):
        return "Hello! How can I help you with clothing or textile information?"

    print("Running similarity search...")

    docs = vectorstore.similarity_search(question, k=20)

    #  2. Role-based access (IMPROVED)
    role_permissions = {
        "OWNER": None,  # full access
        "CASHIER": ["attire", "attire_rent", "billing"],
        "CUSTOMER": ["attire", "category", "availability", "price"],
        "SALES_ASSISTANT": ["attire", "category", "inventory"]
    }

    if role not in role_permissions:
        return "Invalid role."

    allowed_keywords = role_permissions[role]

    filtered_docs = []

    for doc in docs:
        text = doc.page_content.lower()

        # OWNER → no filtering
        if allowed_keywords is None:
            filtered_docs.append(doc)
        else:
            #  match ANY relevant keyword (more flexible than "table:")
            if any(keyword in text for keyword in allowed_keywords):
                filtered_docs.append(doc)

    #  3. Handle empty results cleanly
    if not filtered_docs:
        return "Sorry, the information is not available or you do not have permission to access it."

    print("Documents retrieved:", len(filtered_docs))

    context = "\n".join(doc.page_content for doc in filtered_docs)

    #  4. Role instruction (clean)
    role_instruction_map = {
        "OWNER": "You can access all data.",
        "CASHIER": "Focus on billing, rentals, and attire.",
        "CUSTOMER": "Focus on attire availability, category, and pricing.",
        "SALES_ASSISTANT": "Focus on attire, category, and inventory."
    }

    role_instruction = role_instruction_map.get(role, "")

    print("Sending request to LLM...")

    response = llm.invoke(
        prompt.format(
            context=context,
            question=f"{question}\nUser Role: {role_instruction}"
        )
    )

    print("LLM response received")

    return response.content