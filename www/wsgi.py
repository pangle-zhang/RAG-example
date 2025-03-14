from flask import Flask, request, jsonify, send_from_directory
import os, sys, re, requests
import markdown
import chromadb
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # limit uploading file size 32MB 

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
UPLOAD_DIR = os.path.join(CURRENT_DIR, 'uploads')
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR

sys.path.append(os.path.join(CURRENT_DIR, '../'))
from utils.config import load_config
from utils.embed import embed
from utils.document import split_file, create_ids
configs = load_config()

LLM_SERVICE_URL = configs['llm_url']
EMBEDDING_SERVICE_URL = configs['embedding_url']
CHROMA_SERVER = configs['chroma_server']
CHROMA_PORT = configs['chroma_port']
CHROMA_DBNAME = configs['chroma_dbname']
CHROMA_COLLECTION = configs['chroma_collection']

print(f"Connecting to Chroma database: {CHROMA_SERVER}:{CHROMA_PORT}/{CHROMA_COLLECTION}")
os.environ["NO_PROXY"] = "*"  # disable proxy for local connection
chroma_db = chromadb.HttpClient(
    host=CHROMA_SERVER, 
    port=CHROMA_PORT, 
    ssl=False
)
print("Connected to Chroma database")

@app.route('/')
def index():
    print(CURRENT_DIR)
    return send_from_directory(CURRENT_DIR, 'index.html')

@app.route('/test')
def test():
    return "<h1>I'm working!</h1>"

@app.route('/loading.gif')
def loading():
    return send_from_directory(CURRENT_DIR, 'loading.gif')

@app.route('/chat', methods=['POST'])
def chat():
    ''' Testing with curl:
            curl -X POST http://localhost:5000/chat \
                -H "Content-Type: application/json" \
                -d '{"message": "Hello, how are you?"}'
    '''
    message = request.json.get('message')
    if not message:
        return jsonify({"error": "message parameter is required"}), 400
    print(f"Received message: {message}")

    response = requests.post(
        f"{LLM_SERVICE_URL}/chat/completions", 
        json={
            "messages": [
                {"role": "user", "content": message}
            ]
        }
    )
    if response.status_code != 200:
        return jsonify({"error": "Failed to get response from LLM service"}), 500
    
    answer = response.json()["choices"][0]["message"]["content"]
    pattern = r"<think>(.*?)</think>(.*)"
    match = re.match(pattern, answer, re.DOTALL)
    if match:
        think = match.group(1).strip()
        answer = match.group(2).strip()
    else:
        think = None
    if think:
        print(f"Think: {think}")
    print(f"Answer: {answer}")
    return {"think": think, "answer": markdown.markdown(answer)}

@app.route('/query', methods=['POST'])
def query():
    message = request.json.get('message')
    if not message:
        return jsonify({"error": "message parameter is required"}), 400
    print(f"Received query message: {message}")

    embedding = embed(message)
    collection = chroma_db.get_collection(name=CHROMA_COLLECTION)
    if not collection:
        return jsonify({"error": "没有上传任何文档，请先上传文档"})
    results = collection.query(embedding, n_results=3)
    print(results)
    documents = results["documents"][0]
    n = len(documents)
    print(f"Found {n} results")
    if n == 0:
        return jsonify({"error": "没有找到相关文档"})
    prompt = f"My question is: {message}\n\n"
    prompt += f"Here are the top {n} related documents (please anwser based on them):\n"
    for i, doc in enumerate(documents, 1):
        prompt += f"\n{i}. {doc}\n"
    print(f"Prompt: {prompt}")

    response = requests.post(
        f"{LLM_SERVICE_URL}/chat/completions", 
        json={
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )
    if response.status_code != 200:
        return jsonify({"error": "Failed to get response from LLM service"}), 500
    
    answer = response.json()["choices"][0]["message"]["content"]
    pattern = r"<think>(.*?)</think>(.*)"
    match = re.match(pattern, answer, re.DOTALL)
    if match:
        think = match.group(1).strip()
        answer = match.group(2).strip()
    else:
        think = None
    if think:
        print(f"Think: {think}")
    print(f"Answer: {answer}")
    return {"think": think, "answer": markdown.markdown(answer)}

@app.route('/embed', methods=['POST'])
def embedding():
    ''' Testing with curl:
            curl -X POST http://localhost:5000/embed \
                -H "Content-Type: application/json" \
                -d '{"text": "Hello, how are you?"}'
    '''
    text = request.json.get('text')
    if not text:
        return jsonify({"error": "text parameter is required"}), 400
    print(f"Received text: {text}")
    
    data = embed(text)
    print(f"Embedding: {data}")
    return jsonify(data)

@app.route('/upload', methods=['POST'])
def upload():
    # 检查是否有文件上传
    if 'file' not in request.files:
        return jsonify({"error": "没有上传文件"}), 400

    file = request.files['file']

    # 检查文件名是否为空
    if file.filename == '':
        return jsonify({"error": "文件名不能为空"}), 400

    # 保存文件到指定目录
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # 分割文件
    chunks = split_file(file_path)
    ids = create_ids(chunks)
    embeddings = embed(chunks)
    print(f"Split into {len(chunks)} chunks")

    # 保存到Chroma数据库
    collection = chroma_db.get_or_create_collection(name=CHROMA_COLLECTION)
    n = collection.count()
    print(f"Collection has {n} documents before upserting")
    for i, (chunk, _id, embedding) in enumerate(zip(chunks, ids, embeddings), 1):
        print(f"Inserting chunk {i}/{len(chunks)}")
        collection.upsert(ids=ids, embeddings=embeddings, documents=chunks)
    n = collection.count()
    print(f"Collection has {n} documents after upserting")

    return jsonify({
        "message": "文件上传成功",
        "filename": file.filename,
        "filepath": file_path
    })

@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(e):
    return jsonify({"error": "文件大小超过限制"}), 413

if __name__ == '__main__':
    app.run(port=5000)
