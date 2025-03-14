import os, sys
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(CURRENT_DIR, '../'))

from utils.document import read_file, split_content

file = os.path.join(CURRENT_DIR, 'docs/天府新区.docx')
content = read_file(file)
print(content)
print("-"*100)

chunks = split_content(content)
print(chunks)
print("-"*100)
print(f"Split into {len(chunks)} chunks")
