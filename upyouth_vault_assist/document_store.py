from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.storage import LocalFileStore
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage._lc_store import create_kv_docstore

# This text splitter is used to create the child documents
child_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=400, chunk_overlap=0
)

parent_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=16000, chunk_overlap=0
)

# The vectorstore to use to index the child chunks
vectorstore = Chroma(
    embedding_function=OpenAIEmbeddings(), persist_directory="./chroma_db"
)

# The storage layer for the parent documents
fs = LocalFileStore("./document_store")
store = create_kv_docstore(fs)


retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter
)