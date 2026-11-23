# Ilha Viva — contexto para o Claude Code

Este é o kit de treino das IAs do jogo **Ilha Viva**, um simulador de vida estilo Tomodachi Life feito pelo Philip,
em que "tudo é possível" e cada habitante decide a própria vida. O jogo inteiro é um único arquivo: `ilha-viva.html`.
Fale sempre em **português do Brasil**.

## Sua tarefa
Rodar nesta máquina (Windows, **NVIDIA RTX 4050 Laptop, 6 GB**) o treino completo e deixar o jogo usando os modelos novos:
1. Preparar o ambiente: o mesmo que `1_instalar.bat` faz (venv, PyTorch com CUDA, transformers, peft, bitsandbytes, datasets, accelerate). Confirme que `torch.cuda.is_available()` é True.
2. `python treinar_pequenos.py` → retreina na GPU os 7 modelos que rodam dentro do jogo e salva em `modelos/`.
   Mostra o acerto em frases novas (`testes/`). Compare com os números de referência abaixo.
3. `python aplicar_modelos.py ilha-viva.html` → injeta os modelos no jogo (guarda cópia `ilha-viva_antes_do_treino.html`).
4. `python gerar_dados_linguagem.py` e `python treinar_linguagem.py` → QLoRA do Qwen2.5-1.5B-Instruct com 29 mil exemplos
   (falas, diário, crônica, narrações, comandos em JSON). Saídas: `ilhaviva-lora/` e `ilhaviva-merged/`.
5. Exportar para o Ollama (o mesmo que `3_exportar_ollama.bat`): converter com o llama.cpp para `ilhaviva.gguf` (q8_0),
   criar o Modelfile e rodar `ollama create ilhaviva -f Modelfile`. Teste com `ollama run ilhaviva`.
6. Abrir o jogo para conferir: no painel "IA de linguagem grátis" o modo Ollama acha o modelo `ilhaviva` sozinho
   (o Ollama precisa estar com `OLLAMA_ORIGINS=*`).

Se der erro de versão de biblioteca, memória (6 GB) ou conversão, corrija e siga. Em caso de falta de memória no passo 4:
reduza `per_device_train_batch_size` para 4 e aumente `gradient_accumulation_steps` para 4, ou `max_length` para 256.
Os scripts foram testados só em CPU (modo `RAPIDO=1`); o caminho de GPU e a conversão GGUF nunca rodaram de verdade.

## As IAs do jogo (o que cada modelo faz)
| IA | Função | Modelo no jogo |
|---|---|---|
| Deuz | acasos e catástrofes (peste, praga, meteoro, invasão dos insetos), nunca extinção (piso de 40) | texto → evento + intensidade |
| Arquiteto | tudo que se constrói: 40 obras + 116 tipos de objeto × materiais × acabamentos | texto → obra/objeto + tamanho |
| Fábula | comandos do jogador para um habitante (19 ações, incl. crença/visão e magia) | texto → ação |
| Estoria | memória e diário dos habitantes | texto → boa/ruim + importância |
| Chronos | história do mundo, crônica semanal | texto → categoria + importância |
| Tea | genealogia e nomes | trigramas de letras (não retreina aqui) |
| Fantasy | magia, supertecnologia, arcano e outros mundos (Dimensão Mágica, Planeta Novo, Mundo dos Insetos) | texto → feito |
| Mente dos habitantes | escolha do tempo livre, aprendida pela experiência | estado (48 números) → valor de 10 ações |

Todos os modelos de texto usam o mesmo formato: n-gramas de letras (2–4) + palavras + pares de palavras, com hash FNV-1a
para H posições, uma camada escondida ReLU e duas saídas. Pesos em int8 + base64. **Não mude o formato de entrada**
sem mudar também o código JS do jogo (`netPredict`, `deuzPredict`, `arqPredict`, `menteFeat`).

## Números de referência (antes deste treino, frases novas escritas à mão)
Fábula 18/20 · Arquiteto 14/20 · Deuz 9/12 (teste4) / 19/20 (teste3) · Estoria 13–14/16 · Chronos 11/12 · Fantasy 22/27.
Mente: erro 0,180 (prever só pela média de cada ação: 0,221).

## Decisões de design do Philip (respeitar)
- Todos os habitantes começam iguais; a personalidade nasce das interações. Só eventos externos mudam a sensibilidade.
- 1 dia de jogo = 1 ano. Regiões com área para 60 pessoas; mapa com 2 continentes e capacidade para mais de 1 milhão.
- Cada pessoa é um indivíduo próprio mesmo longe da câmera ("Livro do Mundo", fichas compactas).
- Culturas começam iguais (dos 10 fundadores) e divergem; há leis, regimes, diplomacia, guerras e secessões.
- Próximo patch combinado: a história deve levar ao menos 5 mil anos até os dias de hoje.
