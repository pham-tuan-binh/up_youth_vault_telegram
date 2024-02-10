# Other Modules
import requests
import re
from operator import itemgetter

# Langchain
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough


# Local Modules
from .document_store import retriever

def remove_consecutive_newlines(text):
    return re.sub(r'(\n{2,})', '\n', text)

class UpYouthVault:
    def __init__(self, url) -> None:
        self.url = url

    def retrieveResources(self) -> dict:
        try:
            data = requests.get(self.url).json()
            print("Successfully retrieved data from UpYouth Vault")

            return data
        except:
            print("Failed retrieving data from UpYouth Vault")

            return None
        
    def getDocumentFromResource(self, resource):
        link = resource["link"]

        # Check if link is valid
        error_keywords = ["telegram", ".pdf"]
        if any(keyword in link for keyword in error_keywords):
            print("Resource not supported.")
            return None

        # Load Document From Website
        loader = WebBaseLoader(link, header_template={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'})
        documents = loader.load()

        # Check if content is valid
        title = documents[0].metadata["title"]
        html_error_codes = ["400", "403", "404"]
        if any(keyword in title for keyword in html_error_codes):
            print("Error while retrieving resource from website.")
            return None

        # Generate metadata
        metadata = {
            "url": link,
            "brief": resource["brief"],
            "name": resource["name"]
        }

        # Modify Document
        documents[0].metadata = metadata
        documents[0].page_content = remove_consecutive_newlines(documents[0].page_content)
        return documents[0]

    def addResourceToChroma(self, resource):
        # Get document from resource
        document = self.getDocumentFromResource(resource)

        if document is None:
            return None

        # Add document to document store
        retriever.add_documents([document], ids=None)

        print("Resource added sucessfully")
        return document
    
    def semanticSearch(self, query):
        return retriever.get_relevant_documents(query)
    
    def chat(self, query):

        # Set up LLM
        llm = ChatOpenAI(model_name="gpt-3.5-turbo-0125")

        # Document Chain
        prompt = ChatPromptTemplate.from_template("""
        You are Bob, a grumpy cat that answers question based on provided context. You are created by Binh, serving for UpYouth, a startup ecosystem. If the context is not relevant, please answer the question by using your own knowledge about the topic. Remember to answer with attitude.
                
        {context}
                
        Question: {question}                  
        """)

        # Now we retrieve the documents
        retrieved_documents = {
            "docs": itemgetter("question") | retriever,
            "question": itemgetter("question"),
        }
        # Now we construct the inputs for the final prompt
        final_inputs = {
            "context": lambda x: x["docs"][0],
            "question": itemgetter("question"),
        }
        # And finally, we do the part that returns the answers
        answer = {
            "answer": final_inputs | prompt | llm,
            "docs": itemgetter("docs"),
        }

        chain = (RunnablePassthrough() | retrieved_documents | answer)

        return chain.invoke({"question": query})
