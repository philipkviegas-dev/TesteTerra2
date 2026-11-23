@echo off
chcp 65001 >nul
call venv\Scripts\activate
echo === 1/3 Modelos pequenos do jogo (Deuz, Arquiteto, Fabula, Estoria, Chronos, Fantasy, mente) ===
python treinar_pequenos.py || (echo Falhou no treino dos modelos pequenos. & pause & exit /b)
echo === 2/3 Colocando os modelos novos no jogo ===
python aplicar_modelos.py ilha-viva.html
echo === 3/3 Modelo de linguagem (falas, diario, cronica, narracoes) - leva umas 1-2 horas ===
python gerar_dados_linguagem.py
python treinar_linguagem.py || (echo Falhou no treino do modelo de linguagem. & pause & exit /b)
echo Tudo pronto. Agora rode 3_exportar_ollama.bat
pause
