from arcade_rag.embedder import MODEL_VEC_SIZE, embed_text


def test_embedder():
    result = embed_text("hello world")
    assert len(result) == MODEL_VEC_SIZE
