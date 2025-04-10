import os

import pytest
from duckdb import Error as DuckDBError

from arcade_rag.tools.databases.duckdb import DuckDBDatabase

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
