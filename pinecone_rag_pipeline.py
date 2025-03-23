import os
import time
import pinecone
from dotenv import load_dotenv
from tqdm import tqdm
from argparse import ArgumentParser
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain.schema import HumanMessage, AIMessage, SystemMessage

DATA_PATH = "data/books"
BATCH_SIZE = 100
load_dotenv()

# client
pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"), environment="us-east-1")
index_name = "yc-test-rag"

# Connect to existing index (or show warning)
try:
    index = pc.Index(index_name)
    time.sleep(1)
except Exception as e:
    print(f"{index_name} Pinecone index not found. Run initialize_index() first!")
    raise e

embedding_model = OpenAIEmbeddings()
messages = [
    SystemMessage(content="You are a helpful, encouraging and strategic assistant."),
    HumanMessage(content="Hi AI, how are you today?"),
    AIMessage(content="I'm in a wonderful mood today. How can I help you?"),
    HumanMessage(content="I'd like to understand how to build my own startup.")
]
chat = ChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-3.5-turbo"
)

# Use correct method for SDK v3-compatible LangChain wrapper
vectorstore = LangchainPinecone.from_existing_index(
    index_name=index_name,
    embedding=embedding_model,
    text_key="page_content"
)

def initialize_index():
    existing_indexes = pc.list_indexes()
    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="dotproduct"
        )
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)
    time.sleep(1)
    index = pc.Index(index_name)
    print(f"✨initialized index!")
    print(index.describe_index_stats())
    return index

def clear_all(index):
    index.delete(delete_all=True)

def get_chunks():
    print(f"✨loading docs...")
    loader = DirectoryLoader(DATA_PATH)
    docs = loader.load()
    print(f"✨chunking...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False
    )
    chunks = text_splitter.split_documents(docs)
    print(f"✨got chunks: {len(chunks)}")
    return chunks

def embed_chunks(chunks):
    chunk_texts = [chunk.page_content for chunk in chunks]
    chunk_metadata = [chunk.metadata for chunk in chunks]
    chunk_text_embeddings = embedding_model.embed_documents(chunk_texts)
    pinecone_vectors = [
        {
            "id": f"doc-{i}",
            "values": embedding,
            "metadata": chunk_metadata[i]
        }
        for i, embedding in tqdm(list(enumerate(chunk_text_embeddings)), desc="😎embedding chunks")
    ]
    print(f"✨created pinecone vectors: {len(pinecone_vectors)}")
    return pinecone_vectors

def upsert_to_index(index, pinecone_vectors, mode="all", batch_size=BATCH_SIZE):
    if mode == "batch":
        for i in tqdm(range(0, len(pinecone_vectors), batch_size)):
            batch = pinecone_vectors[i:i+batch_size]
            index.upsert(batch)
            print(f"✨added batch: {i}")
    else:
        index.upsert(pinecone_vectors)
    print(f"✨added all {len(pinecone_vectors)} vectors to pinecone!\n")
    print(index.describe_index_stats())

def add_to_database(clear):
    index = initialize_index()
    chunks = get_chunks()
    pinecone_vectors = embed_chunks(chunks)
    upsert_to_index(index, pinecone_vectors, mode="batch")
    if clear:
        clear_all(index)
        print(f"🌬️✨cleared database!")
    return index, chunks, pinecone_vectors

def setup_retrieval(index):
    text_field = "page_content"
    vectorstore = LangchainPinecone.from_existing_index(
        index_name=index_name,
        embedding=embedding_model,
        text_key=text_field
    )
    return vectorstore

def chat_loop(vectorstore, chat):
    while True:
        query = input("🤔Enter a question: ")
        if not query:
            print(f"🤗Exiting chat session!")
            break
        similar_chunks = vectorstore.similarity_search(query, 5)
        source_knowledge = "\n".join([chunk.page_content for chunk in similar_chunks])
        augmented_prompt = f"""Using the contexts below, answer the query.
        Context:
        {source_knowledge}

        Query: 
        {query}"""
        prompt = HumanMessage(augmented_prompt)
        messages.append(prompt)
        res = chat(messages)
        res_without_rag = chat(messages + [query])
        print(f"\n💌Response w/ RAG: {res.content}")
        messages.append(res)

if __name__ == "__main__":
    # parser = ArgumentParser()
    # parser.add_argument("--clear", action="store_true", help="deletes the index")
    # args = parser.parse_args()
    # index, chunks, pinecone_vectors = add_to_database(clear=args.clear)
    # res, chat, messages = initialize_chat()
    # vectorstore = setup_retrieval(index)
    chat_loop(vectorstore, chat)
