import os

import pytest
from duckdb import Error as DuckDBError

from arcade_rag.databases.duckdb import DuckDBDatabase

TEST_DIR = "/tmp/rag"  # noqa: S108
TEST_DB_PATH = f"{TEST_DIR}/test.duckdb"


@pytest.fixture(scope="function")
def db():
    if not os.path.exists(TEST_DIR):
        os.makedirs(TEST_DIR)
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    db = DuckDBDatabase(TEST_DB_PATH)
    db.connect()
    yield db
    db.disconnect()


def test_add_remove_collection(db: DuckDBDatabase):
    assert db.check_collection_exists("test_collection") is False
    db.add_collection("test_collection")
    assert db.check_collection_exists("test_collection") is True
    db.remove_collection("test_collection")
    assert db.check_collection_exists("test_collection") is False


def test_unique_collection_name(db: DuckDBDatabase):
    db.add_collection("test_collection")
    with pytest.raises(DuckDBError):
        db.add_collection("test_collection")


def test_add_get_remove_document(db: DuckDBDatabase):
    db.add_collection("test_collection")
    doc = db.get_document("test_collection", "uri_1")
    assert doc is None

    db.add_document("test_collection", "uri_1", "title_1", "body_1", "summary_1", {"key": "value"})
    doc = db.get_document("test_collection", "uri_1")
    assert doc is not None
    assert doc.uri == "uri_1"
    assert doc.title == "title_1"
    assert doc.body == "body_1"
    assert doc.summary == "summary_1"
    assert doc.metadata == {"key": "value"}

    db.remove_document("test_collection", "uri_1")
    doc = db.get_document("test_collection", "uri_1")
    assert doc is None


def test_uris_are_unique(db: DuckDBDatabase):
    db.add_collection("test_collection")
    db.add_document("test_collection", "uri_1", "title_1", "body_1", "summary_1", {"key": "value"})
    doc = db.get_document("test_collection", "uri_1")
    assert doc is not None
    with pytest.raises(DuckDBError):
        db.add_document(
            "test_collection", "uri_1", "title_1", "body_1", "summary_1", {"key": "value"}
        )


def test_find_relevant_documents(db: DuckDBDatabase):
    db.add_collection("test_collection")
    db.add_document(
        "test_collection",
        "http://books.com/alice_in_wonderland",
        "Alice in Wonderland",
        "Alice as a little girl goes on an adventure in Wonderland. She meets a rabbit and a cat. She drinks a potion and falls asleep.  Eventually a tea party happens and then the queen gets mad.",  # noqa: E501
        "Don't drink tea.",
        {"author": "Lewis Carroll", "year": 1865, "genre": "fantasy", "country": "England"},
    )

    db.add_document(
        "test_collection",
        "http://books.com/20000_leagues_under_the_sea",
        "20000 Leagues Under the Sea",
        "Captain Nemo is a mysterious man who lives on a submarine. He is a great explorer and a great scientist. He really hates giant squid.",  # noqa: E501
        "Don't drink tea.",
        {"author": "Jules Verne", "year": 1865, "genre": "adventure", "country": "France"},
    )

    db.add_document(
        "test_collection",
        "http://books.com/the_count_of_monte_christo",
        "The Count of Monte Cristo",
        "The Count of Monte Cristo is a great adventure. It is a story about a man who is wrongfully imprisoned. He escapes and then seeks revenge on his enemies.",  # noqa: E501
        "Don't make rich people mad.",
        {"author": "Alexandre Dumas", "year": 1844, "genre": "adventure", "country": "France"},
    )

    results = db.find_relevant_documents(
        "test_collection",
        "What is the story about a man who is wrongfully imprisoned?",
        limit=1,
    )
    assert len(results) == 1
    assert results[0].uri == "http://books.com/the_count_of_monte_christo"

    results = db.find_relevant_documents(
        "test_collection",
        "Who drank the tea?",
        limit=1,
    )
    assert len(results) == 1
    assert results[0].uri == "http://books.com/alice_in_wonderland"

    results = db.find_relevant_documents(
        "test_collection",
        "What books were from the country of France?",
        limit=10,
        min_score=0.6,
    )

    print(results)

    assert len(results) == 2
    assert results[0].uri == "http://books.com/the_count_of_monte_christo"
    assert results[1].uri == "http://books.com/20000_leagues_under_the_sea"
