from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

def build_vector_store():
    sample_doc = "To troubleshoot PPPoE dropping, check MTU sizes. Default RouterOS MTU is 1480. If users report random disconnects, verify the physical link and log for 'peer is not responding' messages."
    with open("manual.txt", "w") as f:
        f.write(sample_doc)
        
    loader = TextLoader("manual.txt")
    splits = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(loader.load())
    return Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings()).as_retriever()
