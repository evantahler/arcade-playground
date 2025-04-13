import os

from sentence_transformers import SentenceTransformer

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
model = SentenceTransformer(MODEL_NAME)
MODEL_VEC_SIZE = model.get_sentence_embedding_dimension()


def embed_text(text: str) -> list[float]:
    return model.encode(text).tolist()
