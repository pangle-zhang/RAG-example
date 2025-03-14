import hashlib
from docx import Document
from .config import load_config

configs = load_config()
CHUNK_SIZE = configs['doc_chunk_size']

def split_file(path: str) -> list[str]:
    content = read_file(path)
    return split_content(content)

def read_file(path: str) -> str:
    suffix = path.split('.')[-1]
    assert suffix in ['txt', 'md', 'doc', 'docx'], f"Unsupported file format: {suffix}"
    if suffix in ['txt', 'md']:
        with open(path) as fh:
            return fh.read()
    else:        
        doc = Document(path)
        return '\n'.join([p.text for p in doc.paragraphs])

def split_content(content: str) -> list[str]:
    ''' Split a long document into chunks of CHUNK_SIZE words '''
    lines = content.split("\n")
    chunks, n, chunk = [], len(lines), ""
    for i, line in enumerate(lines, 1):
        if len(chunk) + len(line) > CHUNK_SIZE:
            chunk += "\n" + line
            chunks.append(chunk.strip())
            chunk = ""
        elif len(chunk) == 0:
            chunk = line.strip()
        else:
            chunk += "\n" + line
    if len(chunk) > 0:
        chunks.append(chunk.strip())   
    return chunks

def create_ids(chunks: list[str]) -> list[str]:
    ''' Create unique IDs for each chunk '''
    return [hashlib.sha1(chunk.encode()).hexdigest() for chunk in chunks]
