import json

import duckdb

from arcade_rag.tools.classes.database import Database, Document


class DuckDBDatabase(Database):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def connect(self):
        self.connection = duckdb.connect(self.db_path)

    def disconnect(self):
        self.connection.close()

    def add_collection(self, collection_name: str):
        collection_name = self.sanitize_collection_name(collection_name)
        self.connection.execute(f"""
          CREATE TABLE {collection_name} (
          uri TEXT UNIQUE,
          title TEXT,
          body TEXT,
          summary TEXT,
          metadata JSON,
          chunk_id INTEGER,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

    def remove_collection(self, collection_name: str):
        collection_name = self.sanitize_collection_name(collection_name)
        self.connection.execute(f"DROP TABLE {collection_name}")

    def check_collection_exists(self, collection_name: str) -> bool:
        collection_name = self.sanitize_collection_name(collection_name)
        return (
            self.connection.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_name = ?",
                [collection_name],
            ).fetchone()
            is not None
        )

    def add_document(
        self,
        collection_name: str,
        uri: str,
        title: str,
        body: str,
        summary: str,
        metadata: dict,
        chunk_id: int = 0,
    ) -> bool:
        collection_name = self.sanitize_collection_name(collection_name)
        self.connection.execute(
            f"""
            INSERT INTO {collection_name} (uri, title, body, summary, metadata, chunk_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,  # noqa: S608
            [uri, title, body, summary, metadata, chunk_id],
        )
        return True

    def remove_document(self, collection_name: str, uri: str):
        collection_name = self.sanitize_collection_name(collection_name)
        self.connection.execute(
            f"DELETE FROM {collection_name} WHERE uri = ?",  # noqa: S608
            [uri],
        )
        return True

    def get_document(self, collection_name: str, uri: str):
        collection_name = self.sanitize_collection_name(collection_name)
        result = self.connection.execute(
            f"SELECT * FROM {collection_name} WHERE uri = ?",  # noqa: S608
            [uri],
        ).fetchdf()
        if not result.empty:
            doc_dict = result.iloc[0].to_dict()
            return Document(
                uri=doc_dict["uri"],
                title=doc_dict["title"],
                body=doc_dict["body"],
                summary=doc_dict["summary"],
                metadata=json.loads(doc_dict["metadata"]),
                chunk_id=doc_dict["chunk_id"],
            )
        return None

    def find_relevant_documents(self, collection_name: str, query: str, limit=10, min_score=0.01):
        collection_name = self.sanitize_collection_name(collection_name)
        return self.connection.execute(
            "SELECT * FROM ? WHERE uri = ?",
            [collection_name, uri],
        ).fetchone()

    def sanitize_collection_name(self, collection_name: str) -> str:
        return (
            collection_name.replace("'", "''")
            .replace(" ", "_")
            .replace("-", "_")
            .replace(".", "_")
            .replace(":", "_")
            .replace("/", "_")
            .replace("\\", "_")
            .replace(";", "_")
        )
