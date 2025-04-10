from abc import ABC, abstractmethod

from pydantic import BaseModel


class Document(BaseModel):
    uri: str
    title: str
    body: str
    summary: str
    metadata: dict
    chunk_id: int


class Database(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def add_collection(self, collection_name: str):
        pass

    @abstractmethod
    def remove_collection(self, collection_name: str):
        pass

    @abstractmethod
    def check_collection_exists(self, collection_name: str) -> bool:
        pass

    @abstractmethod
    def add_document(
        self,
        collection_name: str,
        uri: str,
        title: str,
        document_body: str,
        document_summary: str | None,
        document_metadata: dict | None,
    ) -> bool:
        """The URI is the unique identifier for the document."""
        pass

    @abstractmethod
    def remove_document(
        self,
        collection_name: str,
        uri: str,
    ) -> bool:
        pass

    @abstractmethod
    def get_document(self, collection_name: str, uri: str) -> Document:
        pass

    @abstractmethod
    def find_relevant_documents(
        self, collection_name: str, query: str, limit=10, min_score=0.01
    ) -> list[Document]:
        """
        This method looks through the documents in the collection and returns the most semantically relevant documents to the query.
        We will run 3 comparisons against the document's summary, metadata, and full body.
        """  # noqa: E501
        pass
