@echo off
chcp 65001 >nul
call venv\Scripts\activate
where git >nul 2>nul || (echo Instale o Git em git-scm.com. & pause & exit /b)
where ollama >nul 2>nul || (echo Instale o Ollama em ollama.com. & pause & exit /b)
if not exist llama.cpp git clone --depth 1 https://github.com/ggerganov/llama.cpp
pip install -r llama.cpp\requirements\requirements-convert_hf_to_gguf.txt
python llama.cpp\convert_hf_to_gguf.py ilhaviva-merged --outfile ilhaviva.gguf --outtype q8_0
(echo FROM ./ilhaviva.gguf& echo PARAMETER temperature 0.7& echo PARAMETER num_ctx 2048) > Modelfile
ollama create ilhaviva -f Modelfile
echo.
echo Pronto! No jogo: painel "IA de linguagem gratis" ^> Modo: Ollama. O jogo acha o modelo "ilhaviva" sozinho.
echo Lembre de abrir o Ollama com a variavel OLLAMA_ORIGINS=* para o navegador conseguir falar com ele.
pause
