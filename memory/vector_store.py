import os
import chromadb
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
import logging

class VectorStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        
        # Use OpenAI if key exists, otherwise fallback to local HuggingFace embeddings
        if os.getenv("OPENAI_API_KEY"):
            self.embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")
        else:
            logging.info("No OPENAI_API_KEY found, falling back to local sentence-transformers.")
            self.embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Long-term semantic memory
        self.semantic_collection_name = "semantic_memory"
        self.semantic_db = Chroma(
            client=self.client,
            collection_name=self.semantic_collection_name,
            embedding_function=self.embedding_function
        )

    def store(self, content: str, metadata: dict) -> str:
        """Stores a chunk of text with metadata into the vector database."""
        try:
            self.semantic_db.add_texts(texts=[content], metadatas=[metadata])
            return f"Successfully stored document with metadata: {metadata}"
        except Exception as e:
            logging.error(f"Error storing in vector DB: {str(e)}")
            return f"Error storing document: {str(e)}"

    def search(self, query: str, top_k: int = 3, filter_dict: dict = None) -> list:
        """Searches the vector database for relevant chunks."""
        try:
            results = self.semantic_db.similarity_search_with_relevance_scores(
                query, 
                k=top_k, 
                filter=filter_dict
            )
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": float(score)
                })
            return formatted_results
        except Exception as e:
            logging.error(f"Error searching vector DB: {str(e)}")
            return [{"error": f"Search failed: {str(e)}"}]
