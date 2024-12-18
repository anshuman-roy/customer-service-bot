import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv

file_path = "/Users/anshuman.roy/Downloads/Travel360 Policy Document.pdf"


def load_data():
    # loader = PyPDFLoader(folder_path + "/jesc113.pdf")
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    return docs


def save_docs_to_db(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=20,
    )
    split_docs = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    doc_db = PineconeVectorStore.from_documents(
        documents=split_docs,
        embedding=embeddings,
        index_name=os.getenv('PINECONE_INDEX_NAME'),
        pinecone_api_key=os.getenv('PINECONE_API_KEY'),
    )

    return doc_db


def get_similar_docs(query: str):
    embeddings = OpenAIEmbeddings()
    vector_db = PineconeVectorStore(embedding=embeddings,
                                    index_name=os.getenv('PINECONE_INDEX_NAME'),
                                    pinecone_api_key=os.getenv('PINECONE_API_KEY')
                                    )

    result = vector_db.similarity_search(query)
    # if(len(result) > 0):
    #
    #     for content in result:
    #         print(content.page_content)
    # else:
    #     print("No results")
    return result


def get_retriever_handle():
    embeddings = OpenAIEmbeddings()
    vector_db = PineconeVectorStore(embedding=embeddings,
                                    index_name=os.getenv('PINECONE_INDEX_NAME'),
                                    pinecone_api_key=os.getenv('PINECONE_API_KEY')
                                    )

    retriever = vector_db.as_retriever()
    return retriever


if __name__ == "__main__":
    load_dotenv()
    # docs = load_data()
    # print("# of pages loaded", len(docs))
    # ##print(docs[0])
    # doc_db = save_docs_to_db(docs)
    # print("Docs saved to Pinecone DB")

    ## Get similar docs
    get_similar_docs("What's the cancellation policy for flights?")
