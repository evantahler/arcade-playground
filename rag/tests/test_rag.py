import pytest
from arcade.sdk.errors import ToolExecutionError

from rag.arcade_rag.tools.rag import say_hello


def test_hello() -> None:
    assert say_hello("developer") == "Hello, developer!"


def test_hello_raises_error() -> None:
    with pytest.raises(ToolExecutionError):
        say_hello(1)
