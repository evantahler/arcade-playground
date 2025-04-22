import json
from typing import Annotated

from arcade.sdk import tool, ToolContext
from markitdown import MarkItDown
from openai import OpenAI


md = MarkItDown(enable_plugins=True) 

DEFAULT_SUMMARY_KEYS = ["title", "author", "date", "summary", "main_keyword", "keywords"]

@tool()
def parse_document(file_url_or_path: Annotated[str, "The url or path to the file to parse"]) -> str:
    """Parse the given file and return the text within it."""
    return _parse_document(file_url_or_path)

@tool(requires_secrets=['OPENAI_API_KEY'])
def summarize(context: ToolContext, text: Annotated[str, "The text to summarize"]) -> str:
    """Summarize the given text."""
    return _summarize(context.secrets['OPENAI_API_KEY'], text)

@tool(requires_secrets=['OPENAI_API_KEY'])
def extract_metadata(context: ToolContext, text: Annotated[str, "The text to summarize"]) -> dict:
    """Extract the metadata from the given file."""
    return _extract_metadata(context.secrets['OPENAI_API_KEY'], text)

def _parse_document(file_url_or_path: str) -> str:
    result = md.convert(file_url_or_path)
    return result.text_content

def _summarize(OPENAI_API_KEY:str, text: str, keys: list[str] = DEFAULT_SUMMARY_KEYS) -> str:
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        system_message="You are a helpful assistant that summarizes text.  You should be concise and to the point.  You should not include any other text than the summary.",
        messages=[{"role": "user", "content": text}],
        max_tokens=1000,
        temperature=0.5,
    )
    return response.choices[0].message.content

def _extract_metadata(OPENAI_API_KEY:str, text: str, keys: list[str] = DEFAULT_SUMMARY_KEYS) -> dict:
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        system_message="You are a helpful assistant that extracts metadata from text.  You should extract the metadata from the given text.  You only return JSON.  The keys should be the following: " + ", ".join(keys),
        messages=[{"role": "user", "content": text}],        
        max_tokens=1000,
        temperature=0.5,
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)