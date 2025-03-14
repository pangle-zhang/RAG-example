import os, json

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(CURRENT_DIR, '../config.json')

configs = None

def load_config():
    global configs
    if configs:
        return configs

    with open(CONFIG_FILE) as fh:
        configs = json.load(fh)
    assert 'llm_url' in configs, "llm_url is required in config.json"
    assert 'embedding_url' in configs, "embedding_url is required in config.json"
    assert 'chroma_server' in configs, "chroma_server is required in config.json"
    assert 'chroma_port' in configs, "chroma_port is required in config.json"
    assert 'chroma_dbname' in configs, "chroma_dbname is required in config.json"
    assert 'chroma_collection' in configs, "chroma_collection is required in config.json"
    assert 'doc_chunk_size' in configs, "doc_chunk_size is required in config.json"
    print(f"Loaded configs: {json.dumps(configs, indent=2)}")
    return configs

def get_config(key: str):
    configs = load_config()
    return configs[key]

def get_embedding_url():
    return get_config('embedding_url')
