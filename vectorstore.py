from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
import pandas as pd


def create_vectorstore(df):
    texts = []
    EXCLUDED_TABLES = ['tenants', 'refresh_tokens', 'login']

    for _, row in df.iterrows():
        if 'source_table' in row and row['source_table'] in EXCLUDED_TABLES:
            continue
        row_text = []
        for col in df.columns:
            if pd.notna(row[col]) and col != 'source_table':
                row_text.append(f"{col}: {row[col]}")
        if 'source_table' in row:
            row_text.insert(0, f"Table: {row['source_table']}")
        text = "\n".join(row_text)
        texts.append(text)

    splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=30)
    documents = splitter.create_documents(texts)

    # 3. CHANGE THE EMBEDDINGS HERE:
    print("Generating local embeddings... (this takes a few seconds the first time)")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = FAISS.from_documents(documents, embeddings)
    return vectorstore