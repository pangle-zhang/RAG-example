import re, requests
from .config import get_embedding_url

def embed(text: str|list[str]) -> list[float]:
    if isinstance(text, str):
        return embed_text(text)
    return embed_texts(text)

def embed_text(text: str) -> list[float]:
    url = get_embedding_url() + "/embeddings"
    print(f"Embedding text: {len(text)}")
    response = requests.post(url, json={"input": [text]})
    if response.status_code != 200:
        raise RuntimeError(f"Failed to get embedding from Embedding service: {response.json()}")
    return response.json()["data"][0]["embedding"]

def embed_texts(texts: list[str]) -> list[list[float]]:
    url = get_embedding_url() + "/embeddings"

    # {'error': {'code': 500, 'message': 'input is too large to process. increase the physical batch size', 'type': 'server_error'}}
    # response = requests.post(url, json={"input": texts})
    # if response.status_code != 200:
    #     raise RuntimeError(f"Failed to get embedding from Embedding service: {response.json()}")
    # return [data["embedding"] for data in response.json()["data"]]

    embeddings = []
    for text in texts:
        embeding = embed_text(text)
        embeddings.append(embeding)
    return embeddings
