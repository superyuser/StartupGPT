from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import random
import shutil
import os
import nltk

load_dotenv()

nltk.download('averaged_perceptron_tagger_eng')

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATA_PATH = "data/books"
CHROMA_PATH = "chroma"

def load_docs():
    loader = DirectoryLoader(DATA_PATH, glob="*.md")
    docs = loader.load()
    print(f"loaded {len(docs)} documents!")
    return docs

def split_text(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 500,
        length_function = len,
        add_start_index = True
    )
    chunks = text_splitter.split_documents(docs)
    print(f"split {len(docs)} docs into {len(chunks)} chunks!")
    demo_chunk = chunks[random.randint(0, len(chunks) - 1)]
    print(demo_chunk.page_content)
    print(demo_chunk.metadata)
    return chunks

# chroma: create db from docs

def save_to_chroma(chunks):
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    
    db = Chroma.from_documents(
        chunks,
        OpenAIEmbeddings(),
        persist_directory = CHROMA_PATH
    )

    db.persist() # force save db
    print(f"saved {len(chunks)} chunks to {CHROMA_PATH}")

def main():
    docs = load_docs()
    chunks = split_text(docs)
    save_to_chroma(chunks)

if __name__ == "__main__":
    main()
