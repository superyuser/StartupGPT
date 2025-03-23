from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
# from langchain_community.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain.schema.document import Document
from dotenv import load_dotenv
import random
import shutil
import os
import nltk
import argparse

load_dotenv()

nltk.download('averaged_perceptron_tagger_eng')

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATA_PATH = "data/books"
CHROMA_PATH = "chroma"

# embedding_fn = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2")
embedding_fn = OpenAIEmbeddings(
    model = "text-embedding-ada-002",
    api_key = OPENAI_API_KEY
)

def markdown_to_docloader():
    loader = DirectoryLoader(DATA_PATH)
    return loader.load()

def split_docs_chunks(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1200,
        chunk_overlap = 100,
        length_function = len,
        is_separator_regex = False
    )
    chunks = text_splitter.split_documents(docs)
    return chunks

def add_to_chroma(chunks):
    # load chroma
    db = Chroma(persist_directory = CHROMA_PATH, embedding_function = embedding_fn)
    # calculate page ids
    chunk_ids = get_chunk_ids(chunks)
    # get existing ids
    existing_items = db.get(include=[]) # automatically returns ids, nothing else
    existing_ids = set(existing_items["ids"])
    # add docs if existing id not in db
    new_chunks = [chunk for chunk in chunks if chunk.metadata["id"] not in existing_ids]
    new_chunks_id = [chunk.metadata["id"] for chunk in new_chunks]
    # add to database
    if len(new_chunks):
        db.add_documents(new_chunks, id = new_chunks_id)
        db.persist()
        print(f"added new chunks: {len(new_chunks)}")
    else:
        print(f"no new chunks to add")

def get_chunk_ids(chunks):
    prev_id = None
    curr_chunk_index = 0
    for chunk in chunks:
        source = chunk.metadata.get("id")
        page = chunk.metadata.get("page")
        curr_id = f"{source}:{page}"
        if prev_id == curr_id:
            curr_chunk_index += 1
        else:
            curr_chunk_index = 0
        updated_chunk_id = f"{curr_id}:{curr_chunk_index}"
        prev_id = curr_id
        chunk.metadata["id"] = updated_chunk_id
    return chunks

def clear_db():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clear", action = "store_true", help = "reset / clear the database")
    args = parser.parse_args()
    if args.clear:
        clear_db()
        print("db cleared!")
    
    # load
    documents = markdown_to_docloader()
    chunks = split_docs_chunks(documents)
    add_to_chroma(chunks)

if __name__ == "__main__":
    main()