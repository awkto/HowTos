## How to use RAG against Markdown files

1. Deploy LLM on vLLM such as Llama 3.1 8B (the one I used here)
2. Create a folder *howtos/* and place your markdown files inside it.
3. Create Python Script **ragdemo.py** and configure it with your LLM endpoint details.
4. Create Python Venv: `python -m venv demovenv`
5. Activate Venv: `source demovenv/bin/activate`
6. Install Dependencies: `pip install langchain langchain-community langchain-chroma langchain-openai unstructured sentence-transformers markdown`
7. Run Script: `python ragdemo.py`


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



### Lessons Learned

Some key takeaways about how Retrieval-Augmented Generation works and considerations for performance:

* **RAG Augments LLMs with External Knowledge:** RAG systems improve LLM responses by first retrieving relevant information from a separate knowledge base (like your markdown files stored in a vector database) and then providing this retrieved context to the LLM alongside the user's query. The LLM then uses this specific context to generate a more informed and accurate answer.
* **LLM Context Window is Crucial for Input:** The LLM has a maximum input size limit called a "context window." The combined total of the user query, the retrieved document chunks, and the system prompt must fit within this window. If the input exceeds the context window, the LLM will only process the beginning of the input, leading to incomplete or "cut off" answers.
* **Managing Context Size:** To prevent exceeding the LLM's context window and getting truncated answers, you can:
    * Reduce the size of the document chunks (`chunk_size` and `chunk_overlap` in the text splitter). This makes each piece of retrieved information smaller.
    * Reduce the number of retrieved chunks (`k` in the retriever's `search_kwargs`). This limits the total volume of context sent to the LLM.
    * Use an LLM with a larger context window, if available and feasible, as it can handle more input tokens.
* **Query Specificity Impacts Retrieval:** The specificity of your user query significantly affects which documents (and therefore which chunks) the vector database retrieves. A more specific query is likely to retrieve highly targeted chunks, while a more general query might retrieve chunks related to a broader topic.
