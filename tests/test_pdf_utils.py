from app.utils.pdf_utils import extract_text_from_pdf


class DummyPage:
    def __init__(self, text):
        self._text = text

    def extract_text(self):
        return self._text


def test_extract_text_from_pdf_monkeypatched(monkeypatch, tmp_path):
    # Create a temporary file path to satisfy open()
    pdf_path = tmp_path / "fake.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 dummy")

    class DummyReader:
        def __init__(self, f):
            self._f = f
            self.pages = [DummyPage("Hello "), DummyPage("World")]

    # Patch the PdfReader symbol imported in module
    monkeypatch.setattr("app.utils.pdf_utils.PdfReader", DummyReader)

    text = extract_text_from_pdf(str(pdf_path))
    assert text == "Hello \nWorld"
