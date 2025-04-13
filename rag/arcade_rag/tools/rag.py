from typing import Annotated

from arcade.sdk import ToolContext, tool

from arcade_rag.database import Document
from arcade_rag.databases.duckdb import DuckDBDatabase
from arcade_rag.object_storages.s3 import S3ObjectStorage

REQUIRED_SECRETS = [
    "AWS_ACCESS_KEY",
    "AWS_SECRET_KEY",
    "AWS_BUCKET_NAME",
    "AWS_REGION",
    "RAG_DATABASE_FILE",
]


@tool(requires_secrets=REQUIRED_SECRETS)
def add_rag_collection(
    context: ToolContext,
    collection_name: Annotated[str, "The name of the RAG collection to add"],
) -> bool:
    """Add a collection to the RAG database to store documents."""
    object_storage = build_object_storage_client(context)
    database = build_database_client(context)
    with object_storage.with_locked_and_downloaded_file(database.db_path) as f:
        database.add_collection(collection_name)

    return True


@tool(requires_secrets=REQUIRED_SECRETS)
def remove_rag_collection(
    context: ToolContext,
    collection_name: Annotated[str, "The name of the RAG collection to add"],
) -> bool:
    """Remove a previously added collection from the RAG database."""
    object_storage = build_object_storage_client(context)
    database = build_database_client(context)
    with object_storage.with_locked_and_downloaded_file(database.db_path) as f:
        database.remove_collection(collection_name)

    return True


@tool(requires_secrets=REQUIRED_SECRETS)
def list_rag_collections(
    context: ToolContext,
) -> list[str]:
    """List all collections in the RAG database."""
    object_storage = build_object_storage_client(context)
    database = build_database_client(context)
    with object_storage.with_locked_and_downloaded_file(database.db_path) as f:
        return database.list_collections()


@tool(requires_secrets=REQUIRED_SECRETS)
def add_rag_document(
    context: ToolContext,
    collection_name: Annotated[str, "The name of the RAG collection to ad the document to"],
    uri: Annotated[str, "The URI of the document to add"],
    title: Annotated[str, "The title of the document to add"],
    body: Annotated[str, "The body of the document to add"],
    summary: Annotated[
        str,
        "The summary of the document to add.  If a summary is not provided, it can be generated from the body.",
    ],
    metadata: Annotated[
        dict,
        "The metadata of the document to add.  Metadata should be a JSON dictionary.  Extract the most important features from the document's body.",
    ],
) -> bool:
    """Add a document to the RAG database for later retrieval."""
    object_storage = build_object_storage_client(context)
    database = build_database_client(context)
    with object_storage.with_locked_and_downloaded_file(database.db_path) as f:
        database.add_document(collection_name, uri, title, body, summary, metadata)

    return True


@tool(requires_secrets=REQUIRED_SECRETS)
def remove_rag_document(
    context: ToolContext,
    collection_name: Annotated[str, "The name of the RAG collection to remove the document from"],
    uri: Annotated[str, "The URI of the document to remove"],
) -> bool:
    """Remove a document from the RAG database."""
    object_storage = build_object_storage_client(context)
    database = build_database_client(context)
    with object_storage.with_locked_and_downloaded_file(database.db_path) as f:
        database.remove_document(collection_name, uri)

    return True


@tool(requires_secrets=REQUIRED_SECRETS)
def get_rag_document(
    context: ToolContext,
    collection_name: Annotated[str, "The name of the RAG collection to get the document from"],
    uri: Annotated[str, "The URI of the document to get"],
) -> Document | None:
    """Get a document from the RAG database."""
    object_storage = build_object_storage_client(context)
    database = build_database_client(context)
    with object_storage.with_locked_and_downloaded_file(database.db_path) as f:
        return database.get_document(collection_name, uri)


@tool(requires_secrets=REQUIRED_SECRETS)
def find_relevant_documents(
    context: ToolContext,
    collection_name: Annotated[str, "The name of the RAG collection to find relevant documents in"],
    query: Annotated[str, "The plain-text search term to find relevant documents about"],
    limit: Annotated[int, "The maximum number of documents to return"] = 10,
    min_score: Annotated[float, "The minimum score of the documents to return"] = 0.5,
) -> list[Document]:
    """Find documents in the RAG database that are relevant to the query."""
    object_storage = build_object_storage_client(context)
    database = build_database_client(context)
    with object_storage.with_locked_and_downloaded_file(database.db_path) as f:
        return database.find_relevant_documents(collection_name, query, limit, min_score)


def build_object_storage_client(context: ToolContext):
    return S3ObjectStorage(
        access_key=context.get_secret("AWS_ACCESS_KEY"),
        secret_key=context.get_secret("AWS_SECRET_KEY"),
        bucket_name=context.get_secret("AWS_BUCKET_NAME"),
        region_name=context.get_secret("AWS_REGION"),
    )


def build_database_client(context: ToolContext):
    return DuckDBDatabase(context.get_secret("RAG_DATABASE_FILE"))
