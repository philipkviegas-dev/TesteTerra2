# Gera os dados para ensinar o modelo de linguagem a "falar Ilha Viva":
# falas e pensamentos dos habitantes, diário (Estoria), crônica (Chronos), narração da Fábula e da Fantasy,
# e interpretação de comandos em JSON. Tudo em português do Brasil.
import json, random
random.seed(42)
NOMES=['Lia','Zé','Rafa','Nina','Téo','Malu','Bia','Gui','Duda','Caio','Iara','Bento','Cora','Dante','Elis','Kaela','Ruo','Miara','Moema','Tupã']
TRACOS={'gentil':['gentil','bondoso(a)'],'egoísta':['egoísta'],'corajoso(a)':['corajoso(a)'],'medroso(a)':['medroso(a)'],'sociável':['sociável'],'reservado(a)':['reservado(a)'],'ambicioso(a)':['ambicioso(a)'],'curioso(a)':['curioso(a)'],'desconfiado(a)':['desconfiado(a)'],'trabalhador(a)':['trabalhador(a)'],'preguiçoso(a)':['preguiçoso(a)']}
ERAS=['Bando','Tribo','Aldeia','Cidade-Estado','Reino','Era Medieval','Renascimento','Era Industrial','Era Moderna','Era Digital']
SIT={ # situação -> (fatos, falas possíveis por traço dominante)
 'fome':(['está com muita fome','a reserva acabou'],{'gentil':['Se eu achar comida, divido com quem está pior.','A barriga dói, mas as crianças comem primeiro.'],'egoísta':['Primeiro eu. Depois eu penso nos outros.','Alguém aqui está escondendo comida, tenho certeza.'],'corajoso(a)':['Vou caçar algo grande hoje, nem que seja perigoso.'],'medroso(a)':['E se não tiver comida amanhã também?'],'preguiçoso(a)':['Alguém vai trazer comida... espero.'],'trabalhador(a)':['Não adianta reclamar. Vou trabalhar até conseguir comer.']}),
 'amor':(['viu {B} sorrindo','passou a tarde com {B}'],{'sociável':['Hoje eu falo com {B}. Hoje!'],'reservado(a)':['Gosto de {B}, mas como eu digo isso?'],'corajoso(a)':['Vou dizer para {B} o que eu sinto.'],'medroso(a)':['E se {B} rir de mim?'],'gentil':['Quero fazer {B} feliz, só isso.']}),
 'luto':(['{B} morreu ontem'],{'gentil':['{B} era a melhor pessoa que eu conhecia.','Vou cuidar da família de {B}.'],'reservado(a)':['Não quero falar com ninguém hoje.'],'curioso(a)':['Para onde vamos quando morremos?'],'desconfiado(a)':['Ninguém me diz como {B} morreu de verdade.']}),
 'descoberta':(['o povo descobriu {D}'],{'curioso(a)':['{D}! Quero entender como funciona.','Imagina o que mais existe para descobrir.'],'ambicioso(a)':['Quem dominar {D} vai mandar em todos.'],'desconfiado(a)':['Isso de {D} ainda vai dar problema.']}),
 'guerra':(['o povo está em guerra com {P}'],{'corajoso(a)':['Se precisar lutar, eu luto na frente.'],'medroso(a)':['Eu só queria que a guerra acabasse.'],'gentil':['Do outro lado também tem mães e filhos.'],'ambicioso(a)':['Depois da guerra, a terra deles será nossa.']}),
 'festa':(['tem festa na aldeia'],{'sociável':['Hoje eu danço até o sol nascer!'],'reservado(a)':['Muita gente... vou ficar no canto.'],'preguiçoso(a)':['Festa é bom porque ninguém trabalha.']}),
 'insetos':(['os insetos tomaram a região vizinha'],{'corajoso(a)':['Eles sangram como qualquer bicho. Vamos expulsá-los.'],'medroso(a)':['Eu ouço os estalos deles à noite.'],'curioso(a)':['De onde eles vêm? Tem um mundo inteiro do outro lado?']}),
 'magia':(['{B} fez fogo sair das mãos'],{'curioso(a)':['Eu vi com meus olhos. Quero aprender também.'],'desconfiado(a)':['Isso é truque. Só pode ser truque.'],'medroso(a)':['Isso não é coisa deste mundo.']}),
}
SIT.update({
 'divida':(['deve moedas a {B}','está sendo cobrado(a) por {B}','emprestou moedas a {B} e não recebeu de volta'],{'gentil':['Posso esperar mais um pouco, mas preciso do dinheiro.','Vou dar um jeito de pagar {B}, nem que seja trabalhando.'],'egoísta':['Cada moeda que eu devo é uma moeda que eu perco. Pago só se me obrigarem.','{B} que espere.'],'medroso(a)':['E se tomarem minhas coisas por causa da dívida?','Não durmo pensando no que devo a {B}.'],'corajoso(a)':['Vou ao encontro de {B} e resolvo isso de frente.'],'ambicioso(a)':['Essa dívida é só um degrau. Com o lucro eu pago tudo.']}),
 'negocio':(['está na feira negociando com {B}','conseguiu vender tudo o que trouxe','fechou um bom negócio com {B}'],{'ambicioso(a)':['Hoje o preço está a meu favor.','Quem sabe negociar nunca passa fome.'],'gentil':['Fechei justo, para os dois saírem ganhando.'],'egoísta':['Paguei menos do que valia. {B} nem percebeu.'],'desconfiado(a)':['Contei as moedas duas vezes, nunca se sabe.'],'sociável':['Adoro a feira, todo dia encontro alguém novo.']}),
 'banco':(['guardou as economias no banco','o banco da região quebrou','pediu um empréstimo no banco'],{'medroso(a)':['E se o banco quebrar e levar tudo?','Prefiro guardar as moedas debaixo da cama.'],'ambicioso(a)':['Com esse empréstimo abro meu próprio negócio.','Dinheiro parado é dinheiro perdido.'],'gentil':['Pelo menos minha família tem o que comer se algo me acontecer.'],'desconfiado(a)':['Banco só serve a quem tem muito.']}),
 'esporte':(['venceu o torneio da região','perdeu a final do campeonato','está treinando para competir'],{'corajoso(a)':['Ano que vem eu ganho de novo.','Perder faz parte, mas eu volto mais forte.'],'ambicioso(a)':['O título é só o começo.','Quero ser o maior atleta que essa terra já viu.'],'sociável':['Que festa depois do jogo!'],'preguiçoso(a)':['Treinar todo dia cansa, mas a torcida compensa.']}),
 'armas':(['ganhou uma espada nova','teme que {P} ataque','comprou uma armadura'],{'corajoso(a)':['Agora estou pronto(a) para defender o que é meu.'],'medroso(a)':['Carrego a arma, mas rezo para nunca usar.'],'gentil':['Arma é para proteger, nunca para ferir.'],'ambicioso(a)':['Quem tem as melhores armas decide o rumo da guerra.']}),
 'crime':(['foi roubado(a) esta noite','viu {B} ser preso','foi condenado(a) pelo juiz'],{'gentil':['Se {B} roubou foi por necessidade. Ainda assim a lei existe.'],'desconfiado(a)':['Eu sabia que alguém ia mexer nas minhas coisas.'],'egoísta':['Se me pegarem, nego tudo.'],'corajoso(a)':['Vou atrás de quem fez isso.'],'medroso(a)':['Agora tranco a porta toda noite.']}),
})
def nome():return random.choice(NOMES)
def tr():return random.choice(list(TRACOS))
def ex(instr,inp,out):return {'instruction':instr,'input':inp,'output':out}
data=[]
D=['o fogo','a roda','a escrita','o bronze','os barcos','a medicina','a eletricidade']
P=['Povo de Sura','Clã Malano','Povo de Teteor']
# 1) falas e pensamentos
for _ in range(12000):
  s=random.choice(list(SIT));f,F=SIT[s];t=random.choice([k for k in F]+[tr()]);a=nome();b=nome()
  falas=F.get(t) or random.choice(list(F.values()))
  fala=random.choice(falas).replace('{B}',b).replace('{D}',random.choice(D)).replace('{P}',random.choice(P))
  fato=random.choice(f).replace('{B}',b).replace('{D}',random.choice(D)).replace('{P}',random.choice(P))
  data.append(ex('Você é um habitante do jogo Ilha Viva. Responda com o que você pensa ou fala agora, em primeira pessoa, numa frase curta, de acordo com sua personalidade.',
    f'Nome: {a}. Personalidade: {t}. Era: {random.choice(ERAS)}. Situação: {a} {fato}.',fala))
# 2) diário da Estoria
FATOS_B=['pesquei três peixes','ajudei {B} a construir a cabana','fiz amizade com {B}','aprendi a lascar pedra','dancei na festa','ganhei um colar de conchas','nasceu meu filho']
FATOS_R=['passei fome','briguei com {B}','me machuquei caçando','perdi minha lança','choveu a noite toda e a cabana molhou','{B} me humilhou na frente de todos']
for _ in range(6000):
  a=nome();fb=random.sample(FATOS_B,random.randint(0,2));fr=random.sample(FATOS_R,random.randint(0,2))
  if not fb and not fr:fb=[random.choice(FATOS_B)]
  fatos=[x.replace('{B}',nome()) for x in fb+fr];random.shuffle(fatos)
  humor='bom' if len(fb)>len(fr) else 'ruim' if len(fr)>len(fb) else 'misturado'
  abre={'bom':['Hoje foi um dia bom.','Que dia!','Vou dormir feliz hoje.'],'ruim':['Hoje foi difícil.','Que dia ruim.','Não vejo a hora deste dia acabar.'],'misturado':['Hoje teve de tudo.','Dia estranho.','Teve coisa boa e coisa ruim hoje.']}[humor]
  corpo=' '.join((x[0].upper()+x[1:]+'.') for x in fatos)
  fecha={'bom':['Amanhã quero repetir.','Acho que estou no caminho certo.'],'ruim':['Amanhã tem que ser melhor.','Pelo menos estou vivo.'],'misturado':['A vida é assim mesmo.','Vamos ver o que amanhã traz.']}[humor]
  data.append(ex('Você é Estoria, que escreve o diário dos habitantes de Ilha Viva. Escreva a entrada do diário em primeira pessoa, em até 3 frases simples, usando só os fatos dados.',
    f'Habitante: {a}. Humor: {humor}. Fatos de hoje: {"; ".join(fatos)}.',f'{random.choice(abre)} {corpo} {random.choice(fecha)}'))
# 3) crônica do Chronos
EV={'guerra':'{P} declarou guerra a {Q}','descoberta':'{N} descobriu {D}','obra':'a muralha de {R} ficou pronta','morte':'{N} morreu de velhice','nascimento':'{k} bebês nasceram','catastrofe':'uma peste começou em {R}','politica':'{P} virou uma república','cultura':'surgiu o costume de dançar na lua cheia em {R}'}
R=['Kaloor','Sura','Piva','Teteor','Zenaar']
EV.update({'economia':'o banco de {R} quebrou e muitos perderam as economias','esporte':'{N} foi campeão do torneio de {R}','crime':'{N} foi preso por roubo em {R}'})
for _ in range(4000):
  ks=random.sample(list(EV),random.randint(2,4));evs=[EV[k].replace('{P}',random.choice(P)).replace('{Q}',random.choice(P)).replace('{N}',nome()).replace('{D}',random.choice(D)).replace('{R}',random.choice(R)).replace('{k}',str(random.randint(2,30))) for k in ks]
  marca={'guerra':'pela guerra','catastrofe':'pela tragédia','descoberta':'pelas descobertas','politica':'pela política','obra':'por grandes obras','cultura':'por mudanças nos costumes','morte':'pelas perdas','nascimento':'pelos nascimentos','economia':'pela economia','esporte':'pelos esportes','crime':'pelos crimes'}[ks[0]]
  txt=f'Uma semana marcada {marca}. '+' '.join(e[0].upper()+e[1:]+'.' for e in evs)+' '+random.choice(['O mundo segue mudando.','Os mais velhos dizem que nada será como antes.','E a vida continua.','Quem viver, verá.'])
  data.append(ex('Você é Chronos, o cronista do mundo de Ilha Viva. Escreva a crônica da semana em um parágrafo curto, começando pelo que mais marcou.',f'Era: {random.choice(ERAS)}. Acontecimentos: {"; ".join(evs)}.',txt))
# 4) narração da Fábula e da Fantasy
ACOES=[('declarar amor para {B}','{A} juntou coragem e disse a {B} o que sentia.','{A} tentou falar com {B}, mas as palavras não saíram.'),('fazer amizade com {B}','{A} e {B} passaram a tarde rindo juntos.','{B} não quis muita conversa com {A}.'),
 ('tentar liderar a tribo','O povo ouviu {A} e decidiu segui-lo(a).','Riram de {A} quando ele(a) quis mandar em todos.'),('caçar','{A} voltou com um javali nas costas.','{A} passou o dia na mata e voltou de mãos vazias.'),
 ('voar sem asas','{A} subiu no ar diante de todos. O impossível aconteceu.','{A} pulou do rochedo achando que ia voar e se machucou.'),('negociar com {B}','{A} e {B} acertaram o preço e fecharam o negócio.','{B} achou o preço alto e a conversa terminou sem acordo.'),('cobrar a dívida de {B}','{B} pagou o que devia a {A}.','{B} deu uma desculpa e {A} saiu sem receber.'),('ir ao banco','{A} depositou as moedas e saiu aliviado(a).','O banco estava fechado e {A} voltou para casa.'),('competir no torneio','{A} venceu a prova e foi aplaudido(a) pela multidão.','{A} tropeçou na reta final e perdeu.'),('se armar para a guerra','{A} saiu do arsenal com a espada afiada.','{A} não achou arma nenhuma e ficou de mãos abanando.'),('abrir um portal para outra dimensão','O ar rasgou e uma luz de outro mundo apareceu diante de {A}.','Nada aconteceu. {A} ficou dias ouvindo vozes.')]
for _ in range(5000):
  ac,ok,ko=random.choice(ACOES);a,b=random.sample(NOMES,2);s=random.random()<.5;ch=random.randint(5,95)
  out=(ok if s else ko).replace('{A}',a).replace('{B}',b)
  data.append(ex('Você é Fábula (ou Fantasy, para o impossível), que narra o resultado de um comando no jogo Ilha Viva. Narre em uma ou duas frases, em português do Brasil.',f'Habitante: {a}. Comando: {ac.replace("{B}",b)}. Chance: {ch}%. Resultado: {"sucesso" if s else "falha"}.',out))
# 5) interpretação de comandos em JSON (substitui o classificador pequeno, se você quiser)
INT=[('declara seu amor para {B}','declarar'),('briga com {B}','brigar'),('vira o líder','liderar'),('inventa a roda','descobrir'),('vai caçar um mamute','cacar'),('faz uma festa','festa'),('declara guerra aos vizinhos','guerra'),
 ('na sua cabeça os insetos vão invadir','crenca'),('aprende a voar','magia'),('rouba a comida de {B}','roubar'),('ensina {B} a pescar','ensinar'),('pede desculpas para {B}','desculpas'),('vira pescador','funcao'),('negocia com {B}','negociar'),('cobra a dívida de {B}','cobrar'),('vai ao banco','banco'),('joga futebol com {B}','esporte'),('treina para o torneio','esporte'),('pega uma espada e se arma','armar'),('compra uma armadura','armar'),('vende peixe para {B}','negociar'),('pede um empréstimo no banco','banco')]
for _ in range(5000):
  c,acao=random.choice(INT);b=nome();txt=c.replace('{B}',b)
  data.append(ex('Interprete o comando do jogador para um habitante de Ilha Viva. Responda só com JSON: {"acao": ..., "alvo": nome ou null}.',txt,json.dumps({'acao':acao,'alvo':b if '{B}' in c else None},ensure_ascii=False)))
random.shuffle(data)
with open('dados_linguagem.jsonl','w',encoding='utf-8') as f:
  for d in data:f.write(json.dumps(d,ensure_ascii=False)+'\n')
print('exemplos:',len(data))
