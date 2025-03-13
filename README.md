# RAG-example

A RAG application example for windows.

## Requirements

Python 3.11+, Windows 11

## Setup

### Auto Setup

You can just run *setup.bat* script to setup the full enviroment.

    setup.bat

### Manual Setup

You can also setup by manual with the following steps:

1. Install python 3.11.x

2. Create and activate virtual env:

        python -m venv venv
        venv\Scripts\activate.bat   # Run it in "Command Prompt" instead of PowerShell env

3. Install dependent packages

        pip install -r requirements.txt

4. Download *llama.cpp* binaries from: [llama-b4879-bin-win-avx2-x64.zip](https://github.com/ggml-org/llama.cpp/releases/download/b4879/llama-b4879-bin-win-avx2-x64.zip) and unzip it into diretory *llama.cpp*

5. Download LLM GGUF model file, for example: [deepseek.gguf](https://huggingface.co/unsloth/DeepSeek-R1-Distill-Llama-8B-GGUF/resolve/main/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf)

6. Start *llama.cpp* server to run LLM, for example: 

        llama.cpp/llama-server.exe -m deepseek.gguf --port 8080

7. Start *chroma* server:

        chroma run --port 8000

