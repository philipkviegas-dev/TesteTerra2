# Junta o aprendizado exportado pelos jogadores (botão ⬇ do painel 🧠) e embute no jogo como "base",
# para que todo jogo novo comece com as IAs já evoluídas.
#
# Como usar:
#   1. Coloque os arquivos aprendizado_*.json na pasta aprendizado/
#   2. python consolidar_aprendizado.py            (atualiza ilha-viva.html)
#      python consolidar_aprendizado.py ilha-viva.html docs/index.html publicar/index.html   (vários arquivos)
# Os arquivos já somados vão para aprendizado/processados/ (não são contados duas vezes).
# A base acumulada fica em aprendizado/base.json.
import sys, os, json, glob, shutil, re
sys.stdout.reconfigure(encoding='utf-8')

PASTA = 'aprendizado'
MAX_MARCAS = 3000      # características guardadas por IA
LIM = 3.0              # mesmo limite do jogo
os.makedirs(f'{PASTA}/processados', exist_ok=True)

def vazia():
    return {'v': 1, 'jogos': 0, 'anos': 0, 'nets': {}, 'mente': {'n': 0, 'dW': None}, 'tea': {'F': [], 'M': []}}

base = vazia()
if os.path.exists(f'{PASTA}/base.json'):
    base = json.load(open(f'{PASTA}/base.json', encoding='utf-8'))

novos = [f for f in sorted(glob.glob(f'{PASTA}/*.json')) if os.path.basename(f) != 'base.json']
fontes = []
for f in novos:
    try:
        o = json.load(open(f, encoding='utf-8'))
        if o.get('v') != 1: raise ValueError('versão desconhecida')
        fontes.append(o)
    except Exception as e:
        print('ignorado', f, '-', e)

if not fontes and not (len(sys.argv) > 1 and os.path.exists(f'{PASTA}/base.json')):
    print('Nenhum arquivo novo em aprendizado/. Nada a fazer.'); sys.exit(0)

todos = [base] + fontes   # a base entra como mais uma fonte, com o peso das lições que já tem

out = vazia()
out['jogos'] = sum(o.get('jogos', 0) for o in todos)
out['anos'] = sum(o.get('anos', 0) for o in todos)

# redes de texto: média das marcas ponderada pelo número de lições de cada fonte
for nm in sorted({k for o in todos for k in o.get('nets', {})}):
    soma = {}; peso = 0; n_tot = 0
    for o in todos:
        S = o.get('nets', {}).get(nm)
        if not S: continue
        n = max(1, S.get('n', 0)); peso += n; n_tot += S.get('n', 0)
        for i, e in S.get('w', {}).items():
            d = soma.setdefault(i, {})
            for c, v in e.items(): d[c] = d.get(c, 0) + v * n
    if not peso: continue
    w = {}
    for i, d in soma.items():
        e = {c: max(-LIM, min(LIM, v / peso)) for c, v in d.items()}
        e = {c: round(v, 3) for c, v in e.items() if abs(v) >= 0.02}
        if e: w[i] = e
    if len(w) > MAX_MARCAS:
        mag = sorted(w, key=lambda i: max(abs(v) for v in w[i].values()), reverse=True)[:MAX_MARCAS]
        w = {i: w[i] for i in mag}
    out['nets'][nm] = {'w': w, 'n': n_tot}
    print(f'{nm}: {n_tot} lições, {len(w)} marcas')

# Mente: média dos ajustes da última camada ponderada pelas experiências
soma = None; peso = 0
for o in todos:
    m = o.get('mente') or {}
    dW = m.get('dW'); n = m.get('n', 0)
    if not dW or not n: continue
    if soma is None: soma = [0.0] * len(dW)
    if len(dW) != len(soma): continue
    for i, v in enumerate(dW): soma[i] += v * n
    peso += n
if soma and peso:
    out['mente'] = {'n': peso, 'dW': [round(max(-1.5, min(1.5, v / peso)), 3) for v in soma]}
print(f"Mente: {out['mente']['n']} experiências")

# Tea: nomes de líderes (união, sem repetir, os 400 mais recentes)
for x in 'FM':
    vistos = []
    for o in todos:
        for nm in (o.get('tea') or {}).get(x, []):
            if nm not in vistos: vistos.append(nm)
    out['tea'][x] = vistos[-400:]
print(f"Tea: {len(out['tea']['F'])} nomes F, {len(out['tea']['M'])} nomes M")

json.dump(out, open(f'{PASTA}/base.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
for f in novos: shutil.move(f, f'{PASTA}/processados/' + os.path.basename(f))

# embute no jogo
js = 'const LEARN_BASE=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';//FIM_LEARN_BASE'
alvos = sys.argv[1:] or ['ilha-viva.html']
for p in alvos:
    s = open(p, encoding='utf-8').read()
    novo, n = re.subn(r'const LEARN_BASE=.*?;//FIM_LEARN_BASE', lambda m: js, s, count=1, flags=re.S)
    if n != 1: print(p, ': marcador LEARN_BASE não encontrado, pulando'); continue
    open(p, 'w', encoding='utf-8', newline='').write(novo)
    print('base embutida em', p, f'({len(js)//1024} KB)')
