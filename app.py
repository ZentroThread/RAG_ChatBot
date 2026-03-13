import streamlit as st
from database import load_mysql_data
from vectorstore import create_vectorstore
from ragapp import rag_answer

st.set_page_config(page_title="Textile RAG Chatbot", layout="wide")
st.title("Textile RAG Chatbot (Multi-table MySQL)")

@st.cache_resource
def init_vectorstore():
    try:
        df = load_mysql_data()
        st.success(f" Database connected successfully! Loaded {len(df)} records.")
        return create_vectorstore(df)
    except Exception as e:
        st.error(f"Error initializing: {str(e)}")
        return None

try:
    vector_store = init_vectorstore()
except Exception as e:
    st.warning(f"Vector store initialization failed: {str(e)}")
    st.info("You can still test the database connection above.")
    vector_store = None

question = st.text_input("Ask anything......")

if st.button("Ask"):
    if question.strip():
        if vector_store is None:
            st.error("Vector store not initialized. Please fix the OpenAI API key first.")
        else:
            answer = rag_answer(vector_store, question, role="CUSTOMER")  # You can change role as needed
            st.success(answer)
