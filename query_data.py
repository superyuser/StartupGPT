from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import random
import shutil
import os
import nltk
import argparse

load_dotenv()
print(f"API key is: {os.getenv('OPENAI_API_KEY')}")

nltk.download('averaged_perceptron_tagger_eng')

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATA_PATH = "data/books"
CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def main():
    # CLI for inputting query text
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="the query text")
    args = parser.parse_args()
    query_text = args.query_text

    embedding_fn = OpenAIEmbeddings()
    db = Chroma(persist_directory = CHROMA_PATH, embedding_function = embedding_fn)

    results = db.similarity_search_with_relevance_scores(query_text, k = 5)
    if len(results) == 0 or results[0][1] < 0.7:
        print(f"Unable to find query results!")
        return

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)
    model = ChatOpenAI(
        model = "gpt-3.5-turbo",
        api_key = OPENAI_API_KEY
    )
    response_text = model.predict(prompt)
    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)

if __name__ == "__main__":
    main()