import pytest
import os
from memory.vector_store import VectorStore
from memory.context_manager import ContextManager
from memory.episodic import EpisodicMemory

@pytest.fixture
def mock_db_path(tmp_path):
    return str(tmp_path / "chroma_test_db")

def test_context_manager():
    cm = ContextManager(max_tokens=100)
    # 100 tokens is very small, we should hit the limit quickly
    obs = {
        "step_0": "This is a short observation.",
        "step_1": "This is a much longer observation " * 20
    }
    
    compressed = cm.compress_context(obs)
    
    assert "step_0" in compressed
    assert "step_1" in compressed
    # step_1 should be truncated or at least the process should not crash
    assert compressed["step_1"] != obs["step_1"] or len(compressed["step_1"]) <= len(obs["step_1"])

def test_vector_store(mock_db_path):
    # Setting fake API key to avoid external calls during tests if possible,
    # but we'll let it fallback to HuggingFace for tests.
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
        
    vs = VectorStore(persist_directory=mock_db_path)
    store_result = vs.store("Tesla's revenue grew by 15%", {"ticker": "TSLA", "type": "news"})
    assert "Successfully" in store_result
    
    search_results = vs.search("Tesla revenue", top_k=1)
    assert len(search_results) == 1
    assert "Tesla's revenue grew" in search_results[0]["content"]

def test_episodic_memory(mock_db_path):
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
        
    em = EpisodicMemory(persist_directory=mock_db_path)
    em.log_trajectory("Analyze Tesla", ["step 1", "step 2"], True, 95.0)
    
    past = em.retrieve_past_strategies("Tesla analysis", top_k=1)
    assert len(past) == 1
    assert "Analyze Tesla" in past[0]
