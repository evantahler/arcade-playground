import json

import duckdb

from arcade_rag.database import Database, Document
from arcade_rag.embedder import MODEL_VEC_SIZE, embed_text


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
          body_embedding FLOAT[{MODEL_VEC_SIZE}],
          summary_embedding FLOAT[{MODEL_VEC_SIZE}],
          metadata_embedding FLOAT[{MODEL_VEC_SIZE}],
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

        body_embedding = embed_text(body)
        summary_embedding = embed_text(summary)
        metadata_embedding = embed_text(json.dumps(metadata))

        self.connection.execute(
            f"""
            INSERT INTO {collection_name} (
                uri,
                title,
                body,
                summary,
                metadata,
                body_embedding,
                summary_embedding,
                metadata_embedding,
                chunk_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                uri,
                title,
                body,
                summary,
                metadata,
                body_embedding,
                summary_embedding,
                metadata_embedding,
                chunk_id,
            ],
        )
        return True

    def remove_document(self, collection_name: str, uri: str):
        collection_name = self.sanitize_collection_name(collection_name)
        self.connection.execute(
            f"DELETE FROM {collection_name} WHERE uri = ?",  # noqa: S608
            [uri],
        )
        return True

    def get_document(self, collection_name: str, uri: str) -> Document | None:
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
                score=None,
            )
        return None

    def find_relevant_documents(
        self, collection_name: str, query: str, limit=10, min_score=0.01
    ) -> list[Document]:
        collection_name = self.sanitize_collection_name(collection_name)

        query_embedding = embed_text(query)

        result = self.connection.execute(
            f"""
            SELECT
            *
            , array_cosine_similarity(body_embedding, ?::float[{MODEL_VEC_SIZE}])
                as body_score
            , array_cosine_similarity(summary_embedding, ?::float[{MODEL_VEC_SIZE}])
                 as summary_score
            , array_cosine_similarity(metadata_embedding, ?::float[{MODEL_VEC_SIZE}])
                as metadata_score
            FROM {collection_name}
            WHERE (body_score + summary_score + metadata_score) >= ?
            ORDER BY (body_score + summary_score + metadata_score) DESC
            LIMIT ?
            """,
            [
                query_embedding,
                query_embedding,
                query_embedding,
                min_score,
                limit,
            ],
        ).fetchdf()

        if result.empty:
            return []

        return [
            Document(
                uri=row["uri"],
                title=row["title"],
                body=row["body"],
                summary=row["summary"],
                metadata=json.loads(row["metadata"]),
                chunk_id=row["chunk_id"],
                score=row["body_score"] + row["summary_score"] + row["metadata_score"],
            )
            for _, row in result.iterrows()
        ]

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
