from typing import Annotated
from sqlalchemy import create_engine,Engine,inspect,text

from arcade.sdk import tool, ToolContext

# NOTE: it looks like tool responses are limited to simple python types (str, int, list, etc.)
# class SqlColumn(BaseModel):
#     column_name: str
#     column_type: str

@tool(requires_secrets=["DATABASE_CONNECTION_STRING"])
def discover_tables(context: ToolContext, schema_name: Annotated[str, "The database schema to discover tables in"] = "public") -> list[str]:
    """Discover all the tables in the database"""
    engine = _get_engine(context.get_secret("DATABASE_CONNECTION_STRING"))
    tables = _get_tables(engine, schema_name)
    return tables


@tool(requires_secrets=["DATABASE_CONNECTION_STRING"])
def get_table_schema(context: ToolContext, schema_name: Annotated[str, "The database schema to get the table schema of"], table_name: Annotated[str, "The table to get the schema of"]) -> list[str]:
    """Get the schema of a table"""
    engine = _get_engine(context.get_secret("DATABASE_CONNECTION_STRING"))
    return _get_table_schema(engine, schema_name, table_name)


@tool(requires_secrets=["DATABASE_CONNECTION_STRING"])
def execute_query(context: ToolContext, query: Annotated[str, "The SQL query to execute"]) -> list[str]:
    """Execute a query and return the results"""
    engine = _get_engine(context.get_secret("DATABASE_CONNECTION_STRING"))
    return _execute_query(engine, query)


def _get_engine(connection_string: str) -> Engine:
    """Get a connection to the database"""
    return create_engine(connection_string)


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
    # return [SqlColumn(column_name=column['name'], column_type=column['type'].python_type.__name__) for column in columns_table]
    return [f"{column['name']}: {column['type'].python_type.__name__}" for column in columns_table]

def _execute_query(engine: Engine, query: str) -> list[str]:
    """Execute a query and return the results"""
    with engine.connect() as connection:
        result = connection.execute(text(query))
        return [str(row) for row in result.fetchall()]
