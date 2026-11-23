# Treina as "vozes" que rodam DENTRO do jogo (sem Ollama, sem baixar nada):
#   Fala    -> rede neural (n-gramas de letras + palavras) que escolhe o que o habitante diz, pela personalidade e pela situação
#   Diário  -> moldes de abertura/fecho aprendidos dos 6 mil diários do treino; os fatos do dia são copiados sem mudar
#   Crônica -> moldes de abertura/fecho aprendidos das 4 mil crônicas; o tema vem do Chronos (classificador que já está no jogo)
# Saída: modelos/voz.json  (depois: python aplicar_voz.py ilha-viva.html)
import json, random, re, collections, os, sys
import numpy as np, torch, torch.nn as nn
from treinar_pequenos import feats, aug, q8, dev
random.seed(7); torch.manual_seed(7)
sys.stdout.reconfigure(encoding='utf-8')

# ---------- dados de fala (reaproveita as falas originais e acrescenta memórias e atividades) ----------
src = open('gerar_dados_linguagem.py', encoding='utf-8').read().split('def nome')[0]
ns = {}; exec(src, ns)
NOMES, ERAS, SIT = ns['NOMES'], ns['ERAS'], ns['SIT']
TR = ['gentil','egoísta','corajoso(a)','medroso(a)','sociável','reservado(a)','ambicioso(a)','curioso(a)','desconfiado(a)','trabalhador(a)','preguiçoso(a)']
NOVAS = {
 'boa': (['lembra que fiz amizade com {B}','lembra que ajudei {B}','lembra que ensinei {B}','lembra que fiz as pazes com {B}','lembra que me declarei para {B} e deu certo','lembra que enfrentei {B} e venci','lembra que descobri o fogo','lembra que virei pescador','lembra que vamos ter um bebê','lembra que criei uma lei','lembra que consegui voar','lembra que trabalhei na muralha'],
  {'gentil':['Ainda sorrio quando lembro disso.','Foi bom poder fazer o bem.'],'egoísta':['Foi bom pra mim, e é isso que importa.','Mereci cada pedacinho disso.'],'corajoso(a)':['Quero mais desafios assim.','Foi só o começo.'],'medroso(a)':['Ainda não acredito que deu certo.','Foi um alívio imenso.'],'sociável':['Preciso contar isso para todo mundo!','Dividir isso com {B} foi o melhor.'],'reservado(a)':['Guardo isso só para mim.','Foi um bom momento, em silêncio.'],'ambicioso(a)':['Isso é só um degrau. Vou mais alto.','Esse é o começo de algo grande.'],'curioso(a)':['Quero entender por que deu tão certo.','Será que dá para repetir?'],'desconfiado(a)':['Bom demais... será que não tem pegadinha?','Deu certo, mas vou ficar de olho.'],'trabalhador(a)':['Suor bem gasto.','Valeu cada dia de esforço.'],'preguiçoso(a)':['Que bom que não precisei fazer mais nada.','Merecido descanso agora.'],'_':['Foi um dia bom de lembrar.','Gosto de pensar nisso.']}),
 'ma': (['lembra que {B} me deu um fora','lembra que perdi a briga para {B}','lembra que fui pego(a) roubando {B}','lembra que {B} recusou minha ajuda','lembra que {B} não aceitou minhas desculpas','lembra que falhei ao tentar caçar','lembra que não me deixaram ser pescador','lembra que minha lei foi rejeitada','lembra que tentei construir e não saiu','lembra que a conversa com {B} foi estranha'],
  {'gentil':['Mesmo assim não guardo mágoa.','Quem sabe da próxima eu acerto.'],'egoísta':['A culpa foi dos outros, só pode ser.','Isso não vai ficar assim.'],'corajoso(a)':['Vou tentar de novo, e melhor.','Cair faz parte. Eu levanto.'],'medroso(a)':['Sabia que ia dar errado.','Nunca mais quero passar por isso.'],'sociável':['Preciso conversar com alguém sobre isso.','Dói, mas amanhã falo com {B}.'],'reservado(a)':['Vou ficar quieto(a) por uns dias.','Não quero falar disso.'],'ambicioso(a)':['Um tropeço. Nada mais.','Vou provar que eles estavam errados.'],'curioso(a)':['O que eu fiz de errado? Preciso descobrir.','Cada erro ensina alguma coisa.'],'desconfiado(a)':['Eu já esperava por isso.','Tem gente que não quer ver ninguém bem.'],'trabalhador(a)':['Levanto cedo e tento de novo.','Trabalho é isso: errar e refazer.'],'preguiçoso(a)':['Para que insistir, né?','Melhor deitar e esquecer.'],'_':['Foi um dia difícil de lembrar.','Prefiro não pensar nisso.']}),
 'atividade': (['está pescando','está caçando','está descansando','está conversando','está construindo','está pensando na vida','está dançando','está trabalhando','está explorando'],
  {'gentil':['Quem sabe sobra para dividir.','Gosto de fazer as coisas pensando nos outros.'],'egoísta':['Isso aqui é para mim, não para os outros.','Cada um cuida do seu.'],'corajoso(a)':['Hoje eu arrisco um pouco mais.','Se der perigo, eu encaro.'],'medroso(a)':['Só espero que nada dê errado.','Vou com cuidado, bem devagar.'],'sociável':['Melhor ainda se tiver companhia.','Queria que alguém viesse junto.'],'reservado(a)':['Tranquilo, sozinho(a), do meu jeito.','Aqui ninguém me incomoda.'],'ambicioso(a)':['Um dia vão falar de mim.','Estou construindo meu nome.'],'curioso(a)':['Será que descubro algo novo hoje?','Cada canto tem um segredo.'],'desconfiado(a)':['Olho sempre atento, vai que.','Ninguém precisa saber o que faço.'],'trabalhador(a)':['O dia rende quando a gente não para.','Mãos à obra, sem enrolar.'],'preguiçoso(a)':['Devagar, que a pressa não ajuda.','Daqui a pouco eu paro.'],'_':['Mais um dia como outro qualquer.','Vou levando o dia.']}),
}
def monta_sit():
    S = {}
    for s,(fatos,F) in SIT.items(): S[s] = (fatos, F)
    for s,(fatos,F) in NOVAS.items(): S[s] = (fatos, F)
    return S
S = monta_sit()
D = ['o fogo','a roda','a escrita','o bronze','os barcos','a medicina','a eletricidade']; P = ['Povo de Sura','Clã Malano','Povo de Teteor']
def ph(t): return t   # as falas já usam {B},{D},{P}
rows = []; classes = {}
def cid(t):
    if t not in classes: classes[t] = len(classes)
    return classes[t]
for s,(fatos,F) in S.items():
    for t in F:
        for l in F[t]: cid(l)
for _ in range(14000):
    s = random.choice(list(S)); fatos, F = S[s]
    a = random.choice(NOMES); b = random.choice([x for x in NOMES if x != a])
    r = random.random()
    if r < .12 and '_' in F: pers = 'ainda indefinida'; valid = F['_']
    else:
        ts = random.sample(TR, random.choice([1,1,2,2,3])); pers = ', '.join(ts)
        t0 = ts[0]; valid = F.get(t0) or [l for k,v in F.items() if k != '_' for l in v]
    fato = random.choice(fatos).replace('{B}',b).replace('{D}',random.choice(D)).replace('{P}',random.choice(P))
    t = f'Nome: {a}. Personalidade: {pers}. Era: {random.choice(ERAS)}. Situação: {a} {fato}.'
    rows.append({'t': t, 'v': [classes[l] for l in valid]})
# classes só das falas usadas
C = [None]*len(classes)
for k,v in classes.items(): C[v] = k
random.shuffle(rows); n = len(rows); te = rows[:n//10]; tr = rows[n//10:]
H, HID = 4096, 128
def to_x(rs):
    X = torch.zeros(len(rs), H)
    for i,r in enumerate(rs):
        f = feats(r['t'], H); X[i,f] = 1/np.sqrt(max(1,len(f)))
    return X
def to_y(rs):
    Y = torch.zeros(len(rs), len(C))
    for i,r in enumerate(rs): Y[i, r['v']] = 1/len(r['v'])
    return Y
tr2 = tr + [{**r,'t':aug(r['t'])} for r in tr]
Xtr, Ytr, Xte = to_x(tr2), to_y(tr2), to_x(te)
W1 = nn.Linear(H, HID); Wc = nn.Linear(HID, len(C)); drop = nn.Dropout(0.2)
[m.to(dev) for m in (W1, Wc)]
opt = torch.optim.AdamW(list(W1.parameters())+list(Wc.parameters()), lr=3e-3, weight_decay=1e-4)
EP = 25; sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, EP); best = -1; keep = None
for ep in range(EP):
    perm = torch.randperm(len(Xtr))
    for k in range(0, len(perm), 256):
        b = perm[k:k+256]; h = drop(torch.relu(W1(Xtr[b].to(dev)))); lp = torch.log_softmax(Wc(h), 1)
        loss = -(Ytr[b].to(dev)*lp).sum(1).mean(); opt.zero_grad(); loss.backward(); opt.step()
    sched.step()
    with torch.no_grad(): pred = Wc(torch.relu(W1(Xte.to(dev)))).argmax(1).cpu().tolist()
    acc = sum(p in r['v'] for p, r in zip(pred, te))/len(te)
    if acc >= best: best = acc; keep = {'W1':W1.weight.T.clone(),'b1':W1.bias.clone(),'Wc':Wc.weight.T.clone(),'bc':Wc.bias.clone()}
    if ep % 5 == 4 or ep == EP-1: print(f'  fala época {ep+1}: {acc*100:.1f}% das falas escolhidas combinam com personalidade e situação')
print(f'fala: melhor {best*100:.1f}% ({len(C)} falas possíveis)')
fala = {'classes':C,'H':H,'HID':HID,'W1':q8(keep['W1']),'b1':keep['b1'].tolist(),'Wc':q8(keep['Wc']),'bc':keep['bc'].tolist()}

# ---------- diário e crônica: moldes aprendidos dos dados de treino ----------
dia = {'bom':[collections.Counter(), collections.Counter()], 'ruim':[collections.Counter(), collections.Counter()], 'misturado':[collections.Counter(), collections.Counter()]}
cro_f = collections.Counter(); cro_m = collections.Counter()
def sents(t): return [x.strip() for x in re.split(r'(?<=[.!?])\s+', t) if x.strip()]
for l in open('dados_linguagem.jsonl', encoding='utf-8'):
    d = json.loads(l); ins = d['instruction']
    if ins.startswith('Você é Estoria'):
        m = re.search(r'Humor: (\w+)', d['input']).group(1); ss = sents(d['output'])
        dia[m][0][ss[0]] += 1; dia[m][1][ss[-1]] += 1
    elif ins.startswith('Você é Chronos'):
        ss = sents(d['output']); cro_f[ss[-1]] += 1; cro_m[ss[0]] += 1
# enriquece com algumas variações escritas à mão (o treino original só tem 3 aberturas por humor)
EXTRA_A = {'bom':['O sol estava bonito hoje.','Dia de agradecer.'],'ruim':['Hoje o mundo pesou.','Dia para esquecer.'],'misturado':['Hoje foi meio a meio.','Dia que não sei explicar.']}
EXTRA_F = {'bom':['Durmo em paz.','Que venham mais dias assim.'],'ruim':['Amanhã o sol volta.','Vou dormir cedo e esperar o próximo dia.'],'misturado':['Fico com o lado bom.','Cada dia traz o seu pouco de tudo.']}
diario = {m: {'a':[[t,c] for t,c in v[0].items()] + [[t,2] for t in EXTRA_A[m]], 'f':[[t,c] for t,c in v[1].items()] + [[t,2] for t in EXTRA_F[m]]} for m,v in dia.items()}
MARCA = {'guerra':'pela guerra','catastrofe':'pela tragédia','descoberta':'pelas descobertas','politica':'pela política','obra':'por grandes obras','cultura':'por mudanças nos costumes','morte':'pelas perdas','nascimento':'pelos nascimentos','migracao':'por migrações','amor':'por romances'}
cronica = {'marca':MARCA, 'f':[[t,c] for t,c in cro_f.items()]}
print('diário:', {m:(len(v['a']),len(v['f'])) for m,v in diario.items()}, '· crônica fechos:', len(cronica['f']))
os.makedirs('modelos', exist_ok=True)
json.dump({'fala':fala,'diario':diario,'cronica':cronica}, open('modelos/voz.json','w',encoding='utf-8'), ensure_ascii=False)
print('salvo em modelos/voz.json (%d KB)' % (os.path.getsize('modelos/voz.json')//1024))
