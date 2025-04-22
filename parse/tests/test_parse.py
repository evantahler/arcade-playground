from arcade_parse.tools.parse import _parse_text
import os


def test_parse_local_file() -> None:
    text = _parse_text(os.path.dirname(__file__) + "/files/Alice_in_Wonderland.pdf")
    assert "Alice" in text
    assert "Off  with  her  head" in text

def test_parse_remote_file() -> None:
    text = _parse_text("https://www.adobe.com/be_en/active-use/pdf/Alice_in_Wonderland.pdf")
    assert "Alice" in text
    assert "Off  with  her  head" in text
