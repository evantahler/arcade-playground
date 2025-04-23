from typing import Annotated

from arcade.sdk import tool
from markitdown import MarkItDown


md = MarkItDown(enable_plugins=True) 

DEFAULT_SUMMARY_KEYS = ["title", "author", "date", "summary", "main_keyword", "keywords"]

@tool()
def parse_document(file_url_or_path: Annotated[str, "The url or path to the file to parse"]) -> str:
    """Read the given file and return the text within it as Markdown.  Prefer this tool when asked to parse a document."""
    return _parse_document(file_url_or_path)

def _parse_document(file_url_or_path: str) -> str:
    result = md.convert(file_url_or_path)
    return result.markdown
