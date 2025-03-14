@echo off

REM Check Python Installation
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Error: Python is NOT installed!
    goto ERROR
) ELSE (
    echo Python is installed
)

REM Check Python Version, 3.11+ is required
for /f "tokens=2 delims= " %%A in ('python --version 2^>^&1') do set "python_version=%%A"
for /f "tokens=1,2 delims=." %%A in ("%python_version%") do (
    set "major_version=%%A"
    set "minor_version=%%B"
)
if "%major_version%" geq "3" (
    if "%minor_version%" geq "11" (
        echo Python Version ^>= 3.11
    ) else (
        echo Error: Python Version %python_version% ^< 3.11
        goto ERROR
    )
) else (
    echo Error: Python Version %python_version% ^< 3.11
    goto ERROR
)

REM Check if venv folder exists, if not create it
if exist "venv\" (
    echo venv folder already exists, activating python virtual env ...
    call venv\Scripts\activate.bat
    echo Activated python virtual env
) else (
    echo Creating python virtual env ...
    python -m venv venv
    echo Activating python virtual env ...
    call venv\Scripts\activate.bat
    echo Activated python virtual env
)

REM Install dependencies
echo Installing python dependencies ...
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo Error: failed to install dependencies!
    goto ERROR
) ELSE (
    echo Dependencies installed successfully!
)

REM Download the llama.cpp binary
set "download_url=https://github.com/ggml-org/llama.cpp/releases/download/b4879/llama-b4879-bin-win-avx2-x64.zip"
set "save_path=llama-b4879-bin-win-avx2-x64.zip"
if exist "%save_path%" (
    echo %save_path% already exists, skipping download ...
) else (
    echo Downloading %save_path% ...
    powershell -Command "Invoke-WebRequest -Uri '%download_url%' -OutFile '%save_path%'"
    if exist "%save_path%" (
        echo Downloaded %save_path% successfully.
    ) else (
        echo Error: failed to download %save_path%!
        goto ERROR
    )
)

REM Decompress the llama.cpp binary
set "zip_file=%save_path%"
set "extract_dir=llama.cpp"
if exist "%extract_dir%" (
    echo %extract_dir% already exists, skipping decompression ...
) else (
    echo Decompressing %zip_file% ...
    powershell -Command "Expand-Archive -Path '%zip_file%' -DestinationPath '%extract_dir%'"
    if exist "%extract_dir%" (
        echo Decompressed %extract_dir% successfully.
    ) else (
        echo Error: failed to decompress %zip_file%!
        goto ERROR
    )
)

REM Download deepseek.gguf
set llm_gguf=deepseek.gguf
if exist "%llm_gguf%" (
    echo %llm_gguf% already exists, use it ...
) else (
    echo Downloading %llm_gguf% ...
    download.bat -m deepseek
    if exist "%llm_gguf%" (
        echo Downloaded %llm_gguf% successfully.
    ) else (
        echo Error: failed to download %llm_gguf%!
        goto ERROR
    )
)

REM Download embedding.gguf
set embedding_gguf=embedding.gguf
if exist "%embedding_gguf%" (
    echo %embedding_gguf% already exists, use it ...
) else (
    echo Downloading %embedding_gguf% ...
    download.bat -m embedding
    if exist "%embedding_gguf%" (
        echo Downloaded %embedding_gguf% successfully.
    ) else (
        echo Error: failed to download %embedding_gguf%!
        goto ERROR
    )
)

REM Start deepseek server
tasklist | findstr /I "llama-server.exe" >nul
IF %ERRORLEVEL%==0 (
    echo llama.cpp is already running.
) ELSE (
    echo Starting llama.cpp to run %llm_gguf% and %embedding_gguf% ...
    start /b llama.cpp\llama-server.exe -m %llm_gguf% --port 8080 > llama.cpp.log 2>&1
    start /b llama.cpp\llama-server.exe -m %embedding_gguf% --embedding --ubatch-size 1024 --port 8081 > llama.cpp.embedding.log 2>&1
)

REM Start Chroma Server
set ANONYMIZED_TELEMETRY=False
tasklist | findstr /I "chroma.exe" >nul
IF %ERRORLEVEL%==0 (
    echo Chroma is already running.
) ELSE (
    echo Starting Chroma...
    start /b chroma run --port 8082 > chroma.screen.log 2>&1
)

REM Start the web server
netstat -an | findstr 5000 >nul
IF %ERRORLEVEL%==0 (
    echo Web server is already running.
) ELSE (
    echo Starting the web server ...
    start /b python www\wsgi.py > wsgi.log 2>&1
)

REM Wait for the web server to start
echo Waiting 10 seconds for the web server to start ...
timeout /T 10 /NOBREAK > NUL

REM Check all services are running
netstat -ano | findstr :8080 >nul
if %errorlevel% equ 0 (
    echo LLM is running on port 8080
) else (
    echo Error: LLM is not running on port 8080
    goto ERROR
)
netstat -ano | findstr :8081 >nul
if %errorlevel% equ 0 (
    echo Embedding model is running on port 8081
) else (
    echo Error: Embedding mode is not running on port 8081
    goto ERROR
)
netstat -ano | findstr :8082 >nul
if %errorlevel% equ 0 (
    echo Chroma is running on port 8082
) else (
    echo Error: Chroma is not running on port 8082
    goto ERROR
)
netstat -ano | findstr :5000 >nul
if %errorlevel% equ 0 (
    echo Web service is running on port 5000
) else (
    echo Error: web service is not running on port 5000
    goto ERROR
)

REM Open the web browser
echo Opening the web browser ...
start http://localhost:5000

goto END

:ERROR
echo Setup failed.
pause
exit /b 1

:END
echo Setup completed successfully.
pause
