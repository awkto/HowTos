## Proof of Concept - Use RAG with Markdown files
Retrieval-Augmented Generation (RAG) enhances Large Language Models (LLMs) by retrieving relevant information from external data sources to improve the accuracy and specificity of their generated responses.

1. Deploy LLM on vLLM such as Llama 3.1 8B (the one I used here)
2. Install python3, and venv `sudo apt install python3 python-is-python3 python3.10-venv`
3. Create a folder *howtos/* and place your markdown files inside it.
4. Create Python Script **ragdemo.py** and configure it with your LLM endpoint details.
5. Create Python Venv: `python -m venv demovenv`
6. Activate Venv: `source demovenv/bin/activate`
7. Install Dependencies:
   ```
   pip install langchain langchain-community langchain-chroma langchain-openai \
          unstructured sentence-transformers markdown
   ```
8. Run Script: `python ragdemo.py`


### Script
Full **ragdemo.py** script :
```
import os
import glob
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_openai import ChatOpenAI

from langchain.chains import RetrievalQA

# --- Configuration ---
DOCUMENT_PATH = "./howtos"
CHROMA_DB_PATH = "./chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# --- Local LLM Configuration (vLLM) ---
VLLM_API_BASE = "http://localhost:8000/v1"
VLLM_API_KEY = "YOUR_API_KEY" # Replace or leave as dummy if not needed
LOCAL_LLM_MODEL_NAME = "llama-3.1-8b-instruct" # Set this to the exact model name vLLM is serving

# --- Load and Split Documents ---
print(f"Loading documents from folder: {DOCUMENT_PATH}")

markdown_files = glob.glob(os.path.join(DOCUMENT_PATH, "*.md"))

if not markdown_files:
    print(f"No markdown files found in {DOCUMENT_PATH}.")
    exit()

docs = []
for file_path in markdown_files:
    print(f"Loading {file_path}...")
    loader = UnstructuredMarkdownLoader(file_path)
    try:
        docs.extend(loader.load())
    except Exception as e:
        print(f"Error loading {file_path}: {e}")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
splits = text_splitter.split_documents(docs)
print(f"Split {len(docs)} documents into {len(splits)} chunks.")

# --- Create Embeddings and Index (Vector Database) ---
print(f"Creating embeddings using model: {EMBEDDING_MODEL}")
embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)

print(f"Creating vector database in {CHROMA_DB_PATH}")
if os.path.exists(CHROMA_DB_PATH):
    import shutil
    shutil.rmtree(CHROMA_DB_PATH)
    print("Removed existing Chroma DB.")

vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory=CHROMA_DB_PATH
)

# --- Set up the Retriever ---
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# --- Set up the LLM ---
print(f"Initializing local LLM (vLLM): {LOCAL_LLM_MODEL_NAME} at {VLLM_API_BASE}...")

llm = ChatOpenAI(
    base_url=VLLM_API_BASE,
    api_key=VLLM_API_KEY,
    model=LOCAL_LLM_MODEL_NAME,
    temperature=0
)

# --- Create the RAG Chain ---
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

# --- Query the System ---
print("\n--- RAG Demo Ready ---")
print("Enter your questions based on the markdown files in the folder.")
print("Type 'quit' to exit.")

while True:
    query = input("\nYour question: ")
    if query.lower() == 'quit':
        break

    try:
        result = qa_chain.invoke({"query": query})

        print("\n--- Answer ---")
        print(result['result'])

        if 'source_documents' in result:
            print("\n--- Sources ---")
            for i, doc in enumerate(result['source_documents']):
                print(f"Source {i+1}: {doc.metadata.get('source', 'N/A')}")
        print("--------------")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure your vLLM server is running and the endpoint/model name are correct.")

print("Exiting demo.")

``` 



---
### Stack

* **Orchestration Framework:** `LangChain` (specifically the `RetrievalQA` chain) to manage the flow between components.
* **Document Loading:** `UnstructuredMarkdownLoader` from `langchain-community`, which relies on the `unstructured` and `markdown` Python libraries to read and parse the markdown files.
* **Document Splitting:** `RecursiveCharacterTextSplitter` from `langchain` to break down the documents into smaller, manageable chunks.
* **Embedding Model:** A local Sentence Transformer model (`all-MiniLM-L6-v2`), accessed via `SentenceTransformerEmbeddings` from `langchain-community`, requiring the `sentence-transformers` Python library to convert text chunks into numerical vectors.
* **Vector Database:** `ChromaDB`, integrated through `langchain-community.vectorstores.Chroma`, used to store the document chunks and their embeddings for efficient similarity search.
* **Large Language Model (LLM):** Llama 3.1 8B, running locally and served by `vLLM`.
* **LLM Interface:** `ChatOpenAI` from `langchain-openai`, configured to communicate with your vLLM instance using its OpenAI-compatible API.
* **File Discovery:** Python's built-in `glob` module to find all markdown files in a specified directory.
* **Environment Management (Recommended):** Python's built-in `venv` module for creating isolated project environments.


---

### Lessons Learned

Quick points about how RAG works and how to get the best results:

#### RAG Augments LLMs with External Knowledge
RAG helps LLMs by finding relevant info from your documents (like in a vector DB). It gives this specific info to the LLM along with your question. This makes the answer more accurate and based on your data.

#### LLM Context Window is Crucial for Input
LLMs have a limit on how much text they can read at once – the "context window." Your question, the retrieved document chunks, and system instructions all must fit. If there's too much text, the LLM cuts off the input, leading to incomplete answers.

#### Managing Context Size
To avoid cut-off answers and fit within the context window:
  * Make document chunks smaller (`chunk_size`, `chunk_overlap`).
  * Retrieve fewer chunks (`k` in `search_kwargs`).
  * Use an LLM with a larger context window if possible.

#### Query Specificity Impacts Retrieval
How specific your question is affects what info the system finds. Specific questions get focused, relevant chunks. General questions might get broader info, which can make the LLM's answer less precise.
