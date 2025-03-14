@echo off

echo Stopping chroma server ...
for /f "tokens=5" %%A in ('netstat -ano ^| findstr :8082') do echo PID: %%A
tasklist | findstr /I "chroma.exe" && taskkill /F /IM chroma.exe

echo Stopping llama-server ...
for /f "tokens=5" %%A in ('netstat -ano ^| findstr :8080') do echo PID: %%A
for /f "tokens=5" %%A in ('netstat -ano ^| findstr :8081') do echo PID: %%A
tasklist | findstr /I "llama-server.exe" && taskkill /F /IM llama-server.exe /T

echo Stopping web server ...
for /f "tokens=5" %%A in ('netstat -ano ^| findstr :5000') do echo PID: %%A
for /f "tokens=5" %%A in ('netstat -ano ^| findstr :5000') do taskkill /F /PID %%A

pause
