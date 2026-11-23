# Coloca os modelos recém-treinados dentro do arquivo do jogo (ilha-viva.html), sem mexer no resto.
import json, os, shutil, sys
JOGO = sys.argv[1] if len(sys.argv)>1 else 'ilha-viva.html'
shutil.copy(JOGO, JOGO.replace('.html','_antes_do_treino.html'))
s = open(JOGO, encoding='utf-8').read()
def trocar(marca, novo):
    global s
    if marca not in s: print('  não achei', marca); return
    a = s.index(marca)+len(marca); i=a; d=0
    while True:
        c=s[i]
        if c=='{': d+=1
        elif c=='}':
            d-=1
            if d==0: break
        elif c=='"':
            i+=1
            while s[i]!='"':
                if s[i]=='\\': i+=1
                i+=1
        i+=1
    s = s[:a]+novo+s[i+1:]
M = lambda n: open(f'modelos/{n}.json').read() if os.path.exists(f'modelos/{n}.json') else None
for nome, marca in [('deuz','const DEUZ_MODEL='),('arquiteto','const ARQ_NET=(()=>{const M='),('fabula','const FAB_NET=makeNet('),
                    ('estoria','EST_NET=makeNet('),('chronos','CHR_NET=makeNet('),('fantasy','const FAN_NET=makeNet('),('mente','const MENTE=(()=>{const M=')]:
    m = M(nome)
    if m: trocar(marca, m); print('aplicado:', nome)
open(JOGO, 'w', encoding='utf-8').write(s)
print('Jogo atualizado. Uma cópia do original ficou em', JOGO.replace('.html','_antes_do_treino.html'))
