# Acrescenta aos dados de treino as classes dos sistemas novos (economia, banco, profissões, esportes, armas).
# Parte sempre das cópias dados/<nome>_antes_novos.json (criadas na primeira vez), então pode rodar de novo sem duplicar.
import json, os, random, shutil
random.seed(7)
NOMES = ['Lia','Zé','Rafa','Nina','Téo','Malu','Bia','Gui','Duda','Caio','Iara','Bento','Cora','Dante','Elis','Kaela','Ruo','Miara','Moema','Tupã']
LUGARES = ['Kaloor','Sura','Piva','Teteor','Zenaar','Mabael','Ansoar','Rikiis','Nasis','Komior']
POVOS = ['Povo de Sura','Clã Malano','Povo de Teteor','Reino de Piva','Povo de Kaloor']

def ruido(t):
    t = t.strip()
    r = random.random()
    if r < .18 and len(t) > 6:
        i = random.randrange(1, len(t)-1); t = t[:i] + t[i+1:]            # letra a menos
    elif r < .30 and len(t) > 6:
        i = random.randrange(1, len(t)-2); t = t[:i] + t[i+1] + t[i] + t[i+2:]  # letras trocadas
    elif r < .38:
        t = t.lower()
    elif r < .44:
        t = t.capitalize()
    return t

def combinar(base, pre, suf, n):
    out = set()
    tent = 0
    while len(out) < n and tent < n * 30:
        tent += 1
        t = random.choice(base)
        t = t.replace('{N}', random.choice(NOMES)).replace('{L}', random.choice(LUGARES)).replace('{P}', random.choice(POVOS))
        t = random.choice(pre) + t + random.choice(suf)
        out.add(ruido(' '.join(t.split())))
    return sorted(out)

def carregar(nome):
    orig = f'dados/{nome}_antes_novos.json'
    if not os.path.exists(orig): shutil.copy(f'dados/{nome}.json', orig)
    return json.load(open(orig, encoding='utf-8'))

def gravar(nome, D):
    json.dump(D, open(f'dados/{nome}.json', 'w', encoding='utf-8'), ensure_ascii=False)
    print(nome, 'classes:', len(D['classes']), 'treino:', len(D['train']), 'teste:', len(D['test']))

def juntar(D, cls, frases, s_fn, teste=0.06):
    if cls not in D['classes']: D['classes'].append(cls)
    c = D['classes'].index(cls); random.shuffle(frases); k = max(30, int(len(frases) * teste))
    for i, t in enumerate(frases):
        (D['test'] if i < k else D['train']).append({'t': t, 'c': c, 's': s_fn(t)})

# ---------------------------------------------------------------- Fábula: comandos do jogador para um habitante
ITENS = ['ferramentas','peixe seco','trigo','tecido','couro','sal','ferro','cerâmica','lã','vinho','pão','uma espada','madeira','um cavalo','mel','sandálias','remédios','sementes','um colar','cestos']
PRE_F = ['', '', '', 'vai lá e ', 'manda ele ', 'por favor ', 'agora ', 'tenta ', 'começa a ', 'quero que ', 'faça ', 'meta: ', 'eu quero que ele ', 'ele deve ']
SUF_F = ['', '', '', ' agora', ' hoje', ' de qualquer jeito', ' de vez', ' sem enrolar', ' o quanto antes', ' com calma', '!', '...', ' para o bem da família']
F = {
 'negociar': ['negocia com {N}','compra {I} de {N}','vende {I} para {N}','troca {I} com {N}','faz um negócio com {N}','barganha o preço com {N}','regateia com {N}','fecha um acordo de compra com {N}',
   'vai à feira vender {I}','pede para comprar {I} do {N}','compra {I} no mercado','vende {I} na praça','oferece {I} em troca de comida','comercia {I} com {N}','troca {I} por {I}','abre uma barraca e vende {I}','pechincha com {N}','faz uma proposta de preço a {N}','negociar o preço de {I}','fazer comércio com os vizinhos'],
 'cobrar': ['cobra a dívida de {N}','exige que {N} pague o que deve','manda {N} pagar o empréstimo','cobra o fiado de {N}','pede o dinheiro de volta para {N}','executa a dívida de {N}','toma o penhor de {N}',
   'cobra {N} que está devendo','faz {N} pagar o que deve','vai cobrar o calote de {N}','exige o pagamento de {N}','recupera o dinheiro emprestado a {N}','cobra o que {N} deve','manda um aviso de cobrança para {N}','confisca os bens de {N} pela dívida','pressiona {N} a quitar a dívida'],
 'banco': ['vai ao banco','deposita as moedas no banco','pede um empréstimo no banco','abre uma conta no banco','guarda o dinheiro no banco','saca o dinheiro do banco','paga o empréstimo ao banco','funda um banco',
   'quita a dívida com o banco','pede crédito para abrir um negócio','vai guardar as economias no banco','pega dinheiro emprestado do banqueiro','tira as moedas da conta','empresta dinheiro a juros','vira banqueiro','depositar o salário no banco','pedir um financiamento','abre uma poupança','pede um crédito ao banco','resgata o dinheiro guardado'],
 'esporte': ['joga {S} com {N}','vai treinar para o torneio','disputa uma corrida com {N}','pratica luta','vira atleta','entra no time','participa do torneio','joga xadrez com {N}','compete na natação','treina arco e flecha',
   'aposta no campeonato','quer ser campeão de {S}','desafia {N} para uma partida de {S}','vai treinar {S}','entra para o time de {S}','participa do campeonato','treina todo dia para vencer o torneio','vira treinador de {S}','joga uma partida com {N}','vai torcer pelo time na final','faz exercício e se prepara para competir'],
 'armar': ['arme-se','pega uma espada','compra uma armadura','equipa um escudo','carrega um arco','arma-se com um mosquete','veste um colete','se protege com um escudo','pega as armas do arsenal','ganha um rifle',
   'vai se armar para a guerra','compra uma arma para se defender','pega uma lança','se equipa para a batalha','põe a armadura','pega o arco e as flechas','fica armado','pega um porrete para se proteger','veste couro e pega uma adaga','se prepara para lutar com armas'],
}
SPORTS = ['futebol','corrida','luta','natação','arco e flecha','remo','xadrez','basquete','tênis','salto','cabo de guerra','malabarismo','lança','boxe']
def fab_frases(cls, n):
    base = []
    for b in F[cls]:
        if '{I}' in b or '{S}' in b:
            for _ in range(6): base.append(b.replace('{I}', random.choice(ITENS), 1).replace('{I}', random.choice(ITENS), 1).replace('{S}', random.choice(SPORTS)))
        else: base.append(b)
    return combinar(base, PRE_F, SUF_F, n)

D = carregar('fabula')
for cls in F:
    juntar(D, cls, fab_frases(cls, 2600), lambda t: 0)
gravar('fabula', D)

# ---------------------------------------------------------------- Chronos: manchetes da crônica
E_ECO = ['O banco de {L} quebrou e muita gente perdeu o que tinha guardado','{N} fundou um banco em {L}','Os preços dispararam e o dinheiro perdeu valor','{N} abriu uma loja na feira de {L}','O comércio de {L} prosperou com a nova feira',
  'Uma corrida aos bancos esvaziou os cofres de {L}','{N} faliu e não conseguiu pagar o que devia','O mercado de {L} ficou cheio de mercadores','{P} passou a usar moeda de metal','A inflação corroeu as economias do povo',
  'Os mercadores de {L} fecharam um grande negócio','{N} deu calote e perdeu o crédito','Os preços do trigo subiram com a escassez','{N} ficou rico vendendo ferramentas','O banco central de {L} cobriu as perdas dos depositantes',
  'Um novo imposto encareceu o comércio de {L}','{N} pediu um empréstimo e abriu uma oficina','As taxas de juros subiram em {L}','A feira de {L} bateu recorde de vendas','{N} penhorou a casa para pagar a dívida','Os salários dos ferreiros subiram em {L}','A moeda de {P} foi trocada por uma nova']
E_ESP = ['O torneio de {L} terminou com a vitória de {N}','{N} foi campeão de corrida em {L}','{N} se machucou durante o torneio','O time de {L} venceu a final do campeonato','Uma multidão assistiu à luta entre {N} e {N}',
  '{N} treinou anos e virou o maior atleta de {L}','A arena de {L} recebeu os jogos de verão','{N} perdeu a final e jurou vingança','Os jogadores de {L} derrotaram o time rival','O estádio de {L} foi inaugurado com um grande jogo',
  'Apostadores perderam tudo na final do torneio','{N} ganhou a medalha de natação','Nasceu uma rivalidade entre os times de {L} e {L}','O campeonato de luta de {L} reuniu os melhores lutadores','{N} foi contratado como treinador pelo time de {L}','O patrocínio de {N} garantiu o torneio']
E_CRI = ['{N} foi preso por roubo em {L}','Ladrões saquearam o celeiro de {L}','{N} foi condenado pelo juiz de {L}','O armazém de {L} foi assaltado de noite','Houve um assassinato em {L}','{N} foi pego com armas proibidas',
  'A guarda confiscou as armas dos moradores de {L}','{N} fugiu depois de roubar o mercado','Uma quadrilha atacou a caravana de {L}','{N} foi acusado de fraude','O contrabando de armas cresceu em {L}','Soldados saquearam a vila vencida',
  '{N} foi exilado por trair o povo','O banco de {L} foi roubado','A polícia prendeu o bando que assaltava viajantes','{N} sofreu um golpe e perdeu as economias']
def chr_frases(base, n):
    out = set(); tent = 0
    while len(out) < n and tent < n * 20:
        tent += 1; t = random.choice(base)
        while '{N}' in t: t = t.replace('{N}', random.choice(NOMES), 1)
        while '{L}' in t: t = t.replace('{L}', random.choice(LUGARES), 1)
        t = t.replace('{P}', random.choice(POVOS))
        if random.random() < .15: t = t + '.'
        out.add(ruido(t))
    return sorted(out)
D = carregar('chronos')
import re
juntar(D, 'economia', chr_frases(E_ECO, 1100), lambda t: 2 if re.search(r'quebrou|corrida|faliu|infla', t, re.I) else 1)
juntar(D, 'esporte', chr_frases(E_ESP, 800), lambda t: 1 if re.search(r'campe|final|inaugur|vit', t, re.I) else 0)
juntar(D, 'crime', chr_frases(E_CRI, 800), lambda t: 2 if re.search(r'assassin|saquear|saquearam|quadrilha', t, re.I) else 1)
gravar('chronos', D)

# ---------------------------------------------------------------- Deuz: acasos econômicos e esportivos
SEV = {0: ['leve','pequena','fraca','pequeno','discreta','de leve'], 1: ['', '', '', 'média','forte','de verdade'], 2: ['terrível','devastadora','enorme','apocalíptica','gigantesca','total','devastador']}
PRE_D = ['quero ','chama ','deixa ','Ei deuz, ','faça ','manda ','crie ','provoque ','traga ','','','deuz, ']
SUF_D = ['',' em {L}',' na capital',' onde eu estou',' agora',' por favor',' no continente do leste',' sobre {L}',' essa noite','']
D_ = {
 'crise': ['uma crise financeira','a quebra dos bancos','os preços disparando','uma corrida aos bancos','inflação','o dinheiro perdendo valor','um colapso da economia','uma crise no comércio','a falência dos mercadores','um crash na bolsa','os bancos sem dinheiro','a moeda desvalorizando','uma recessão','todo mundo perdendo as economias','um pânico financeiro'],
 'prosperidade': ['uma era de riqueza','ouro por todo lado','o comércio florescendo','uma onda de prosperidade','mercadores ricos','a economia crescendo','um boom econômico','moedas para todo mundo','dinheiro sobrando no bolso do povo','tempos de abundância no comércio','os negócios indo muito bem','uma febre do ouro','feira cheia de compradores','salários subindo'],
 'torneio': ['um torneio','um campeonato','os jogos olímpicos','uma grande competição esportiva','uma disputa de atletas','um torneio de luta','uma final de campeonato','jogos e competições','uma corrida entre os atletas','um festival de esportes','os melhores atletas competindo','uma olimpíada','uma copa entre as regiões','os times se enfrentando'],
}
def deuz_frases(base, n):
    out = {}; tent = 0
    while len(out) < n and tent < n * 20:
        tent += 1; s = random.choice([0, 1, 1, 2]); adj = random.choice(SEV[s])
        core = random.choice(base); mid = (' ' + adj) if adj and random.random() < .7 else ''
        t = random.choice(PRE_D) + core + mid + random.choice(SUF_D).replace('{L}', random.choice(LUGARES))
        out[ruido(' '.join(t.split()))] = s
    return out
D = carregar('deuz')
for cls, base in D_.items():
    fr = deuz_frases(base, 1500); juntar(D, cls, list(fr), lambda t, fr=fr: fr[t])
gravar('deuz', D)

# ---------------------------------------------------------------- Arquiteto: obras novas
TAM = {0: ['pequeno','simples','básico','modesto','de leve'], 1: ['', '', 'bom','médio','bonito'], 2: ['grande','imenso','enorme','gigante','monumental']}
PRE_A = ['construa ','Arquiteto, quero ','faz ','me faça ','precisamos de ','comece a construir ','levante ','monte ','quero ','mande construir ','erga ','Arquiteto, constrói ']
SUF_A = ['',' agora',' perto de {L}',' no meio do povoado',' para o povo de {L}',' na região de {L}',' para as crianças',' que dure mil anos','']
A_ = {
 'banco': ['um banco','um lugar para guardar dinheiro','uma casa de empréstimos','um cofre público','uma agência bancária','uma casa de câmbio','uma tesouraria','um banco para guardar as moedas do povo','um prédio para depositar e emprestar dinheiro','um banco com cofre forte'],
 'estadio': ['um estádio','um campo de futebol','uma quadra de esportes','uma pista de corrida','um ginásio','um campo de treino para atletas','um estádio para os jogos','um lugar para competições esportivas','uma pista de atletismo','um campo para os torneios','uma quadra de basquete','uma piscina para competições'],
 'ferraria': ['uma ferraria','uma forja','uma oficina de ferreiro','um lugar para forjar armas e ferramentas','um forno de fundição','uma forja com bigorna e fole','uma oficina de metal','um ateliê de ferreiro','uma fundição'],
 'quartel': ['um quartel','um arsenal','uma caserna','uma armaria','uma casa de armas','um campo de treinamento militar','um depósito de armas','um quartel para os soldados','um lugar para guardar as armas do exército','um forte de treinamento para a guarda'],
}
def arq_frases(base, n):
    out = {}; tent = 0
    while len(out) < n and tent < n * 25:
        tent += 1; s = random.choice([0, 1, 1, 1, 2]); adj = random.choice(TAM[s])
        core = random.choice(base); mid = (' ' + adj) if adj else ''
        t = random.choice(PRE_A) + core + mid + random.choice(SUF_A).replace('{L}', random.choice(LUGARES).lower() if random.random() < .5 else random.choice(LUGARES))
        out[ruido(' '.join(t.split()))] = s
    return out
D = carregar('arquiteto')
mover = D['classes'].index('arena'); novo = len(D['classes'])
# "estádio" estava dentro de arena: passa para a classe nova
D['classes'] += [c for c in A_ if c not in D['classes']]
ie = D['classes'].index('estadio')
for lst in (D['train'], D['test']):
    for r in lst:
        if r['c'] == mover and 'estadio' in r['t'].lower().replace('á', 'a'): r['c'] = ie
for cls, base in A_.items():
    fr = arq_frases(base, 600); juntar(D, cls, list(fr), lambda t, fr=fr: fr[t])
gravar('arquiteto', D)
