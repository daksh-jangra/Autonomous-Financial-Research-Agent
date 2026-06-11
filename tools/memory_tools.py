from memory.vector_store import VectorStore

_global_vector_store = None

def get_vector_store():
    global _global_vector_store
    if not _global_vector_store:
        _global_vector_store = VectorStore()
    return _global_vector_store

def vector_db_search(query: str, top_k: int, filter: dict = None) -> list:
    vs = get_vector_store()
    return vs.search(query, top_k, filter)

def vector_db_store(content: str, metadata: dict) -> str:
    vs = get_vector_store()
    return vs.store(content, metadata)
