import os
from pypdf import PdfReader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# Path to store the FAISS index
FAISS_DB_PATH = "index"

def save_to_faiss(file_path):
    """
    Extracts text from a PDF, splits it into chunks, generates embeddings, 
    and stores them in a FAISS vector index.
    """
    # Read and extract text from PDF
    reader = PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    full_text = full_text.strip()
    if not full_text:
        print("No text found in the PDF.")
        return

    # Split the text into smaller chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(full_text)
    print(f"Created {len(chunks)} text chunks from the PDF.")

    # Convert chunks to LangChain Document objects
    documents = [Document(page_content=chunk) for chunk in chunks]
    print(f"Converted chunks to {len(documents)} Document objects.")

    # Generate embeddings
    embeddings = OpenAIEmbeddings()
    print("OpenAI embeddings initialized.")

    # Create and save FAISS index
    try:
        faiss_index = FAISS.from_documents(documents, embeddings)
        faiss_index.save_local(FAISS_DB_PATH)
        print(f"FAISS index saved to '{FAISS_DB_PATH}'.")
    except Exception as e:
        print(f"Error saving FAISS index: {e}")

def search_faiss(query):
    """
    Loads the FAISS index and returns the top 3 matching document chunks based on the query.
    """
    embeddings = OpenAIEmbeddings()
    # Allow deserialization since index is self-generated and trusted
    faiss_index = FAISS.load_local(FAISS_DB_PATH, embeddings, allow_dangerous_deserialization=True)
    results = faiss_index.similarity_search(query, k=3)
    return " ".join([doc.page_content for doc in results])
