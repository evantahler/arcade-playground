import pytest
from arcade.core.schema import ToolSecretItem
from arcade.sdk import ToolContext

from arcade_sql.tools.sql import (
    discover_tables,
    execute_query,
    get_table_schema,
    update_user_status,
)


@pytest.fixture
def mock_context():
    context = ToolContext()
    context.secrets = []
    context.secrets.append(
        ToolSecretItem(
            key="DATABASE_CONNECTION_STRING", value="postgresql://evan@localhost:5432/postgres"
        )
    )

    return context


def test_discover_tables(mock_context) -> None:
    assert discover_tables(mock_context) == ["users", "messages"]


def test_get_table_schema(mock_context) -> None:
    assert get_table_schema(mock_context, "public", "users") == [
        "id: int",
        "name: str",
        "email: str",
        "password_hash: str",
        "created_at: datetime",
        "updated_at: datetime",
        "status: str",
    ]


def test_execute_query(mock_context) -> None:
    assert execute_query(mock_context, "SELECT id, name, email FROM users WHERE id = 1") == [
        "(1, 'Mario', 'mario@example.com')"
    ]


def test_update_user_status(mock_context) -> None:
    print(update_user_status(mock_context, 1, "active"))
    assert update_user_status(mock_context, 1, "active") == ["(1, 'mario@example.com', 'active')"]
