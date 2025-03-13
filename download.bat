@echo off
setlocal enabledelayedexpansion

:: 设置下载地址
set llama_url=https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
set deepseek_url=https://huggingface.co/unsloth/DeepSeek-R1-Distill-Llama-8B-GGUF/resolve/main/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf
set embedding_url=https://huggingface.co/gaianet/Nomic-embed-text-v1.5-Embedding-GGUF/resolve/main/nomic-embed-text-v1.5.f16.gguf

:: 解析参数
set MODEL=
set HELP=0

:parse_args
if "%~1"=="" goto check_args
if /I "%~1"=="-m" (
    set "MODEL=%~2"
    shift
    shift
    goto parse_args
)
if /I "%~1"=="--model" (
    set "MODEL=%~2"
    shift
    shift
    goto parse_args
)
if /I "%~1"=="-h" (
    set HELP=1
    goto check_args
)
if /I "%~1"=="--help" (
    set HELP=1
    goto check_args
)
echo Invalid argument: %~1
exit /b 1

:check_args
if %HELP%==1 (
    echo Usage: download.bat -m ^<model^>
    echo Supported models: llama, deepseek
    exit /b 0
)

if "%MODEL%"=="" (
    echo Error: Missing required parameter -m ^<model^>
    exit /b 1
)
echo Selected model: %MODEL%

if "%MODEL%"=="llama" (
    set URL=%llama_url%
    set FILE=llama.gguf
) else if "%MODEL%"=="deepseek" (
    set URL=%deepseek_url%
    set FILE=deepseek.gguf
) else if "%MODEL%"=="embedding" (
    set URL=%embedding_url%
    set FILE=embedding.gguf
) else (
    echo Error: Unsupported model "%MODEL%"
    echo Supported models: llama, deepseek, embedding
    exit /b 1
)

:: 使用 PowerShell 下载文件
echo Downloading %MODEL% model from %URL%...
powershell -Command "& {Invoke-WebRequest -Uri '%URL%' -OutFile '%FILE%'}"

if %ERRORLEVEL% NEQ 0 (
    echo Download failed!
    exit /b 1
) else (
    echo Download completed: %FILE%
)
exit /b 0
