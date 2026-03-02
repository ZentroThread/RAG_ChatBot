# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings
# from langchain_community.vectorstores import FAISS
# import os
# import pandas as pd
#
# def create_vectorstore(df):
#     texts = []
#
#     # Define sensitive tables that should not be embedded
#     EXCLUDED_TABLES = ['tenants', 'refresh_tokens', 'login']
#
#     # # Brands
#     # for _, r in brands.iterrows():
#     #     texts.append(
#     #         f"Brand {r['brand_name']} (ID {r['brand_id']})"
#     #     )
#     #
#     # # Categories
#     # for _, r in categories.iterrows():
#     #     texts.append(
#     #         f"Category {r['category_name']} (ID {r['category_id']})"
#     #     )
#     #
#     # # Clothes
#     # for _, r in clothes.iterrows():
#     #     texts.append(
#     #         f"Cloth {r['cloth_name']} (ID {r['cloth_id']}) category ID {r['category_id']} brand ID {r['brand_id']} size {r['size']} color {r['color']} price {r['price']} stock quantity {r['stock_quantity']}"
#     #     )
#
#     # Dynamic text generation - works with any table structure
#     for _, row in df.iterrows():
#         # Skip rows from sensitive tables (extra security layer)
#         if 'source_table' in row and row['source_table'] in EXCLUDED_TABLES:
#             continue
#
#         # Create text from all columns in the row
#         row_text = []
#         for col in df.columns:
#             if pd.notna(row[col]) and col != 'source_table':  # Skip null values and source_table
#                 row_text.append(f"{col}: {row[col]}")
#
#         # Add source table information
#         if 'source_table' in row:
#             row_text.insert(0, f"Table: {row['source_table']}")
#
#         text = "\n".join(row_text)
#         texts.append(text)
#
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size = 150,
#         chunk_overlap = 30
#     )
#
#     documents = splitter.create_documents(texts)
#
#     embeddings = OpenAIEmbeddings(
#         api_key = os.getenv("OPENAI_API_KEY")
#     )
#
#     vectorstore = FAISS.from_documents(documents, embeddings)
#
#     return vectorstore

#new
from langchain_text_splitters import RecursiveCharacterTextSplitter
# 1. REMOVE THIS: from langchain_openai import OpenAIEmbeddings
# 2. ADD THIS:
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