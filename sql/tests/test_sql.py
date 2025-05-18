from arcade.core.schema import ToolSecretItem
from arcade.sdk import ToolContext

from arcade_sql.tools.sql import discover_tables, execute_query, get_table_schema

context = ToolContext()
context.secrets = []
context.secrets.append(
    ToolSecretItem(
        key="DATABASE_CONNECTION_STRING", value="postgresql://evan@localhost:5432/postgres"
    )
)


def test_discover_tables() -> None:
    assert discover_tables(context) == ["users", "messages"]


def test_get_table_schema() -> None:
    assert get_table_schema(context, "public", "users") == [
        "id: int",
        "name: str",
        "email: str",
        "password_hash: str",
        "created_at: datetime",
        "updated_at: datetime",
    ]


def test_execute_query() -> None:
    assert execute_query(context, "SELECT id, name, email FROM users WHERE id = 1") == [
        "(1, 'Mario', 'mario@example.com')"
    ]
