@echo off
cd /d "%~dp0"
if exist venv\Scripts\python.exe (venv\Scripts\python.exe consolidar_aprendizado.py ilha-viva.html docs\index.html publicar\index.html) else (python consolidar_aprendizado.py ilha-viva.html docs\index.html publicar\index.html)
pause
