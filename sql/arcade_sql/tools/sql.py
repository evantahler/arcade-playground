from typing import Annotated, Any, Literal

from arcade.sdk import ToolContext, tool
from arcade.sdk.errors import RetryableToolError
from sqlalchemy import Engine, create_engine, inspect, text


@tool(requires_secrets=["DATABASE_CONNECTION_STRING"])
def discover_tables(
    context: ToolContext,
    schema_name: Annotated[str, "The database schema to discover tables in"] = "public",
) -> list[str]:
    """Discover all the tables in the SQL database when the list of tables is not known"""
    engine = _get_engine(context.get_secret("DATABASE_CONNECTION_STRING"))
    tables = _get_tables(engine, schema_name)
    return tables


@tool(requires_secrets=["DATABASE_CONNECTION_STRING"])
def get_table_schema(
    context: ToolContext,
    schema_name: Annotated[str, "The database schema to get the table schema of"],
    table_name: Annotated[str, "The table to get the schema of"],
) -> list[str]:
    """
    Get the schema of a table in the SQL database when the schema is not known,
    but the name of the table is provided
    """
    engine = _get_engine(context.get_secret("DATABASE_CONNECTION_STRING"))
    return _get_table_schema(engine, schema_name, table_name)


@tool(requires_secrets=["DATABASE_CONNECTION_STRING"])
def execute_query(
    context: ToolContext, query: Annotated[str, "The SQL query to execute"]
) -> list[str]:
    """
    You have a connection to a SQL database.
    Execute a query and return the results against the SQL database
    """
    engine = _get_engine(context.get_secret("DATABASE_CONNECTION_STRING"))
    try:
        return _execute_query(engine, query)
    except Exception as e:
        raise RetryableToolError(  # noqa: TRY003
            f"Query failed: {e}",
            developer_message=f"Query '{query}' failed.",
            additional_prompt_content="Load the database schema (<GetTableSchema>) and try again.",  # noqa: E501
            retry_after_ms=10,
        ) from e


USER_STATUSES = Literal["active", "inactive", "pending", "banned"]


@tool(requires_secrets=["DATABASE_CONNECTION_STRING"])
def update_user_status(
    context: ToolContext,
    user_id: Annotated[int, "The ID of the user to update"],
    status: Annotated[USER_STATUSES, "The status to update the user to"],
) -> list[str]:
    """
    THIS IS THE ONLY TOOL THAT CAN UPDATE THE DATABASE.  DO NOT USE ANY OTHER TOOL FOR UPDATES.
    You have a connection to a SQL database.
    Update the status of a user in the SQL database.
    The user status is stored in the 'status' column of the 'users' table
    """
    status = status.lower()
    engine = _get_engine(
        context.get_secret("DATABASE_CONNECTION_STRING"), isolation_level="READ COMMITTED"
    )
    query = "UPDATE users SET status = :status WHERE id = :id RETURNING id, email, status"
    return _execute_query(engine, query, params={"id": user_id, "status": status})


def _get_engine(connection_string: str, isolation_level: str = "READ UNCOMMITTED") -> Engine:
    """
    Get a connection to the database.
    Note that we build the engine with an isolation level of READ UNCOMMITTED to prevent all writes.
    """
    return create_engine(connection_string, isolation_level=isolation_level)


def _get_tables(engine: Engine, schema_name: str) -> list[str]:
    """Get all the tables in the database"""
    inspector = inspect(engine)
    schemas = inspector.get_schema_names()
    tables = []
    for schema in schemas:
        if schema == schema_name:
            tables.extend(inspector.get_table_names(schema=schema))
    return tables


def _get_table_schema(engine: Engine, schema_name: str, table_name: str) -> list[str]:
    """Get the schema of a table"""
    inspector = inspect(engine)
    columns_table = inspector.get_columns(table_name, schema_name)
    return [f"{column['name']}: {column['type'].python_type.__name__}" for column in columns_table]


def _execute_query(engine: Engine, query: str, params: dict[str, Any] | None = None) -> list[str]:
    """Execute a query and return the results."""
    with engine.connect() as connection:
        result = connection.execute(text(query), params)
        return [str(row) for row in result.fetchall()]
