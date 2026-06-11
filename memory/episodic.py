import chromadb
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
import logging
import json
import os

class EpisodicMemory:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        
        if os.getenv("OPENAI_API_KEY"):
            self.embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")
        else:
            self.embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        self.episodic_collection_name = "episodic_memory"
        self.episodic_db = Chroma(
            client=self.client,
            collection_name=self.episodic_collection_name,
            embedding_function=self.embedding_function
        )

    def log_trajectory(self, query: str, plan: list, success: bool, final_score: float = None):
        """Logs a completed research trajectory to episodic memory."""
        trajectory_summary = f"Query: {query}\nPlan: {json.dumps(plan)}\nOutcome: {'Success' if success else 'Failed'}"
        
        metadata = {
            "type": "trajectory",
            "success": success,
        }
        if final_score is not None:
            metadata["score"] = final_score
            
        try:
            self.episodic_db.add_texts(texts=[trajectory_summary], metadatas=[metadata])
            return True
        except Exception as e:
            logging.error(f"Error logging trajectory to episodic memory: {str(e)}")
            return False

    def retrieve_past_strategies(self, query: str, top_k: int = 2) -> list:
        """Retrieves successful past plans for similar queries."""
        try:
            results = self.episodic_db.similarity_search(
                query, 
                k=top_k, 
                filter={"success": True}
            )
            return [doc.page_content for doc in results]
        except Exception as e:
            logging.error(f"Error retrieving from episodic memory: {str(e)}")
            return []
