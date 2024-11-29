from PyPDF2 import PdfReader
from io import BytesIO

def extract_text_from_pdf(file_content):
    try:
        reader = PdfReader(BytesIO(file_content))
        text = " ".join([page.extract_text() for page in reader.pages])
        return text
    except Exception as e:
        return ""
