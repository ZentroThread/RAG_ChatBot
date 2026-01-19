from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os

def create_vectorstore(df):
    texts = []
    
    # # Brands
    # for _, r in brands.iterrows():
    #     texts.append(
    #         f"Brand {r['brand_name']} (ID {r['brand_id']})"
    #     )
    # 
    # # Categories
    # for _, r in categories.iterrows():
    #     texts.append(
    #         f"Category {r['category_name']} (ID {r['category_id']})"
    #     )
    #     
    # # Clothes
    # for _, r in clothes.iterrows():
    #     texts.append(
    #         f"Cloth {r['cloth_name']} (ID {r['cloth_id']}) category ID {r['category_id']} brand ID {r['brand_id']} size {r['size']} color {r['color']} price {r['price']} stock quantity {r['stock_quantity']}"
    #     )

    for _, row in df.iterrows():
        text = f"""
            Product: {row['cloth_name']}
            Brand: {row['brand_name']}
            Category: {row['category_name']}
            Price: {row['price']}
            Size: {row['size']}
            Color: {row['color']}
            Stock Quantity: {row['stock_quantity']}
            """
        texts.append(text)
        
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 150,
        chunk_overlap = 30
    )
    
    documents = splitter.create_documents(texts)
    
    embeddings = OpenAIEmbeddings(
        api_key = os.getenv("OPENAI_API_KEY")
    )
    
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    return vectorstore