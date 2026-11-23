@echo off
chcp 65001 >nul
echo === Ilha Viva: preparando o ambiente de treino (RTX 4050) ===
where python >nul 2>nul || (echo Instale o Python 3.11 em python.org e marque "Add to PATH". & pause & exit /b)
python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install transformers peft bitsandbytes datasets accelerate numpy sentencepiece
python -c "import torch;print('GPU encontrada:',torch.cuda.is_available(),torch.cuda.get_device_name(0) if torch.cuda.is_available() else '')"
pause
