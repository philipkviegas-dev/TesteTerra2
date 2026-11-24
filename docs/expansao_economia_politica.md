# Expansão: Ecologia, Rotas comerciais e Sucessão

Projeto de design (nada disto está no jogo ainda). Três sistemas ligados entre si, que fazem a economia e a política
nascerem do que os habitantes vivem, em vez de serem números soltos.

Ordem recomendada de construção: **C (Ecologia) → A (Rotas) → B (Sucessão)**. Cada fase fecha sozinha e é testável.

---

## 1. O que já existe (e onde)

| Peça | Estado hoje | Onde |
|---|---|---|
| Acordo de comércio | Existe, mas é **abstrato**: só soma `kp`, melhora a relação e é rompido se a relação cair. Nenhuma mercadoria se move. | `diplomacyPair`, `f.trade` |
| Comida da região | Cada região tem `reserva` e `hunger`. A comida anual sai de `res.*` (mar, floresta, fértil, pedra) × estação × `regionFoodMul(rid)`. | `regionMorning`, `lifeYear`, `regionFoodMul` |
| Ponto único de gancho | `regionFoodMul` já multiplica clima, inverno, praga e insetos. É o lugar natural para ecologia e comércio entrarem. | linha ~4478 |
| Fome → política | `r.hunger` já derruba a lealdade e provoca secessão. | `secession` |
| Líder da facção | Escolhido por **popularidade** (+12 se for da Casa atual). **Não existe herdeiro**. Quando o líder morre, alguém é sorteado por popularidade. | `facLeaders`, `setFacLeader` |
| Casas e dinastias | Registradas (`world.casas`, `world.dinastias`), com rivalidade e paz entre Casas. | `dinastiaRegistra`, `casaRival` |
| Golpe | Existe como **sorteio cego de 3% ao ano** em ditaduras. Não tem causa. | `regimeYear` |
| Anexação | `mergeFactions` junta o povo menor ao maior. Não existe vassalagem. | `diplomacyPair` |
| Herança | Bens passam aos filhos adultos, mas **poder não**. | `die` |
| Regiões longe da câmera | Não têm objetos por pessoa: são vetores (`DORM`). Todo sistema novo tem de ser **por região ou por facção**, nunca por pessoa distante. | `DORM`, `lifeYear` |

Regra de ouro técnica: o formato de entrada dos modelos **não muda**. A "entrada na IA" abaixo usa só os canais que já
existem: `remember`, `shape` (traços), `relate`, `wants`, o valor de cada ação na decisão e o log/crônica.

---

## 2. Fase C: Ecologia (pressão e renovação de recursos)

**Ideia:** a terra cansa quando é muito usada e se recupera quando é cuidada. A comida deixa de ser um número fixo por bioma.

### Ganha / perde / entra na IA
- **Ganha:** quem vive numa região bem cuidada come mais fácil. O lenhador e o pescador veem o resultado do próprio trabalho.
- **Perde:** a mata rala, o rio esvazia, o solo cansa. Fome, migração forçada e, se persistir, secessão.
- **Entra na IA:**
  - `remember` para quem trabalha a terra: "a mata de {região} está rala" (importância 5–7).
  - `shape(n,'diligencia'/'confianca')` pelo resultado do trabalho.
  - O valor das ações de coleta/pesca na decisão do habitante cai quando o recurso está escasso (mesma soma `v+=` já usada em metas).
  - Leis novas nascem do conhecimento (`LAWS`): "Manejo da mata", "Defeso da pesca", "Rodízio de plantio". O líder as cria pelo caminho que já existe (`lawsYear`).

### Dados (por região, 3 números de 0 a 1, guardados como bytes)
- `eco.flo` (floresta), `eco.pes` (pesca; só se `res.mar`), `eco.solo` (fertilidade; só se `res.fertil`). Começam em 1.

### Regras (1 passo por ano, O(regiões ocupadas))
- Pressão `p = população / 60 + obras/ (30) + técnica` (ferro, vapor e eletricidade aumentam a extração).
- Desgaste: `eco.x -= 0.02 * max(0, p - 0.6)`. Recuperação: `eco.x += 0.012 * (1 - p)` mais bônus por lei e tecnologia (reflorestamento, aquedutos, rodízio).
- Efeito: `regionFoodMul` ganha o fator `0.55 + 0.45 * média(eco dos recursos da região)`.
- **Piso 0,25**, em respeito à regra do Deuz de nunca causar extinção. Recuperação sempre possível, só lenta.
- Eventos existentes se somam sem conflito: `blight` e `insect` continuam multiplicando por fora. Desmatamento aumenta o dano de enchente (pequeno).

### Interface
- No painel da região: barras "🌲 mata 82% · 🐟 pesca 40% · 🌾 solo 90%".
- Em `drawCenario`, a densidade de árvores já usa `res.floresta`; passa a usar `eco.flo` (menos árvores quando rala).
- Crônica: frase quando uma região cruza 50% e 30%, e quando se recupera.

### Teste de aceite
- Região de 60 pessoas por 100 anos sem lei: `eco` desce, comida cai, a pressão migratória sobe.
- A mesma região com lei de manejo: estabiliza acima de 0,5.
- Nunca abaixo de 0,25. Tempo do passo anual ≤ 1 ms com todas as regiões ocupadas.

---

## 3. Fase A: Rotas comerciais e caravanas

**Ideia:** o acordo de comércio vira um caminho real no mapa, por onde excedentes viajam. Quem tem sobra ajuda quem tem falta, e por isso a guerra e o bloqueio passam a doer.

### Ganha / perde / entra na IA
- **Ganha:** o **comerciante** enriquece (moedas); povoados famintos são salvos; regiões ricas em recurso raro (pedra, mar) vendem mais caro.
- **Perde:** o **caravaneiro** pode ser assaltado ou morrer na rota; povos viram **dependentes** de quem lhes vende comida; bloqueio em guerra corta o abastecimento.
- **Entra na IA:**
  - Cada rota tem 1 **caravaneiro nomeado** (um comerciante real da região de origem; se está em `DORM`, é "hidratado" como já ocorre com líderes). Viagem bem-sucedida: `remember` + `shape ambicao/confianca`. Assalto: `remember` forte (8) + medo (`shape coragem` para cima ou para baixo conforme o traço) + rancor contra a facção agressora (`relate`).
  - O ofício `comerciante` ganha motivo novo na decisão: "tem rota livre, mercadoria sobrando" soma ao valor da ação `trade`.
  - Moedas ganhas entram em `n.coins`, que a Mente já usa (`medoPerder`, banco, empréstimo).

### Dados
- `world.rotas = [{id, a, b, fa, fb, caminho:[regionIds], desde, vol, risco, estado}]` com no máximo ~1 por par de facções com `f.trade`.
- `r.dep` (dependência de comida importada, 0–1) por região, calculado, não guardado.
- Bônus de comida de importação entra em `regionFoodMul` (teto +20%).

### Regras (passo anual, O(rotas))
1. **Nasce** quando `f.trade[b.id]` existe (hoje isso só muda a relação). Escolhe o par de regiões vizinhas/litorâneas mais próximo (`bordering`, `r.sea` com barcos). Caminho = BFS curto por `nb` e `sea`, máximo ~8 regiões.
2. **Volume** = menor excedente entre as pontas: `reserva - população` do exportador (e `eco` alto), limitado pela técnica (carroça, barco, ferrovia).
3. **Troca por especialidade:** mar → peixe/sal; floresta → madeira; pedra → metal/ferramenta; fértil → grão. O importador ganha comida (para o que falta) ou material para obras (`arq`).
4. **Risco** sobe com guerra no caminho, fome nos bandos que cruzam e baixa com guarda/lei. Evento de assalto tira parte do volume e pode matar o caravaneiro.
5. **Bloqueio:** guerra entre as pontas ou uma ocupação no caminho muda o estado para `cortada`; dependência alta + corte → `r.hunger`, que já alimenta a secessão.
6. **Ecologia:** o exportador que extrai demais esgota `eco` mais rápido (tragédia dos comuns). Liga as fases C e A.

### Interface
- Mapa: linha pontilhada entre as pontas, ponto andando, cor da facção, espessura = volume; linha vermelha tracejada quando cortada. Filtro "Rotas" ligado/desligado (barato: desenha só rotas visíveis na janela).
- Livro do Mundo: nova aba "🚚 Rotas" (quem comercia com quem, volume, dependências, caravaneiros famosos).
- Crônica: "a rota de {A} a {B} foi aberta / cortada pela guerra / assaltada".

### Teste de aceite
- Duas facções vizinhas com comércio: aparece rota; a região faminta passa a ter `hunger=0` em até 5 anos.
- Declarar guerra entre elas: rota vira `cortada`, a fome volta.
- 1 milhão de capacidade: rotas ≤ N facções × 3; passo anual ≤ 1 ms.

---

## 4. Fase B: Crises de sucessão e política interna

**Ideia:** o poder passa por herdeiros, e quando passa mal, vira drama. Aproveita Casas, dinastias e traços emergentes (`ambicao`, `coragem`, `bondade`).

### Ganha / perde / entra na IA
- **Ganha:** o herdeiro designado tem futuro; o pretendente ambicioso tem chance de poder; o líder tem legado.
- **Perde:** o pretendente derrotado perde laços e Casa (pode morrer ou ir ao exílio); o líder sem herdeiro vê o reino rachar; quem assassina parente carrega a culpa.
- **Entra na IA:**
  - Ser herdeiro vira **meta/sonho** natural (`n.meta`): "reinar". Já existe o sistema de metas e o bônus `v+=40` na decisão.
  - `shape ambicao/coragem` ao disputar; `shape bondade` negativo ao matar parente; `remember` com importância 9–10 nos fatos de sucessão; `relate` forte entre irmãos rivais.
  - Crime de fratricídio registra em `world.crimes`, que a Fábula/Estoria já leem.

### Dados
- `f.gov.heir` (id do herdeiro designado ou `null`), `f.gov.crise = {desde, pretendentes:[ids], ate}`, `f.vassal = {de: facId, tributo, desde}`.

### Regras
1. **Herdeiro por regime:**
   - monarquia/império: filho adulto mais velho da Casa (primogenitura), senão parente da Casa mais popular.
   - anciãos/conselho: o conselho escolhe o mais respeitado.
   - república/democracia: eleição (já existe); sem herdeiro.
   - ditadura: o mais ambicioso e forte (aumenta golpes).
2. **Morte do líder** (gancho em `die`): se há herdeiro adulto, assume. Se **não há**, ou há 2+ pretendentes (`ambicao>0.2` com popularidade a menos de 10 de diferença), abre **crise** de 1–3 anos.
3. **Resolução da crise (anual):** acordo (casamento ou divisão de poder), golpe (quem tem mais `coragem` + apoio da guarda), **guerra civil** (reusa `secession` e `declareWar` entre a facção-mãe e a nova) ou intervenção externa.
4. **Golpe com causa:** substitui o sorteio cego de 3% por uma conta de impopularidade do líder + pretendente forte + fome (`r.hunger`).
5. **Vassalagem:** em vez de só `mergeFactions`, uma facção bem menor, em guerra perdida ou em crise, pode virar **vassala**: paga tributo anual (comida/moedas, via rota se existir), mantém líder próprio, e pode se rebelar se o tributo pesa e a fome sobe.

### Interface
- Painel da facção: "Herdeiro: …", "Crise de sucessão (2 anos)". Árvore de família: o herdeiro marcado com 👑.
- Livro: aba Casas ganha histórico de sucessões e crises; crônica contextual.

### Teste de aceite
- Monarquia com herdeiro: transição sem crise.
- Líder morto sem herdeiro, com dois ambiciosos: crise abre, e em até 3 anos resolve por uma das 4 vias, sem facção "sem líder" por mais que isso.
- Vassalo faminto com tributo alto: rebelião mensurável.

---

## 5. Como as três se ligam

```
Ecologia -> menos comida -> fome -> (Rotas importam comida) -> dependência
Rotas   -> riqueza/tributo -> poder do herdeiro e do comerciante
Sucessão -> guerra civil/bloqueio -> rota cortada -> fome -> secessão
```

Um ciclo de causa e efeito que gera histórias sozinho, sem script, e todo ele cabe nos ganchos que já existem
(`regionFoodMul`, `r.hunger`, `facLeaders`, `diplomacyPair`, `secession`).

## 6. Regras transversais

- **Todos começam iguais** (CLAUDE.md): `eco` começa em 1 em toda parte; nenhuma região nem Casa recebe bônus inicial.
- **Piso de sobrevivência:** `eco ≥ 0,25`, como o piso 40 do Deuz.
- **Escala:** passo anual só por região/facção/rota. Nenhuma varredura de pessoas em `DORM`.
- **Saves:** campos novos opcionais (`r.eco`, `world.rotas`, `f.gov.heir`, `f.vassal`), com valores padrão ao carregar saves antigos.
- **Preço no desempenho:** cada fase mede o custo do passo anual no teste de aceite (alvo ≤ 1 ms).
- **IAs treinadas:** as frases novas do log podem cair em categorias que o Chronos já conhece. Se a nota cair, um retreino fica para depois (a GPU está ocupada com o Qwen).

## 7. Decisões que dependem do Philip

1. **Herdeiro:** primogenitura estrita (previsível) ou herdeiro escolhido pelo líder, que pode errar (mais drama)?
2. **Caravaneiro:** uma pessoa real que pode morrer na rota (mais emoção, mais custo de hidratação), ou só um evento abstrato com nome?
3. **Ecologia permanente:** deixar uma região cair a 0,25 por muito tempo e ficar assim (cicatriz), ou sempre recuperar em ~100 anos?
4. **Ordem:** seguir C → A → B (recomendado) ou começar pela sucessão, que é a mais visível?

## 8. Estimativa de trabalho (por fase)

| Fase | Mexe em | Tamanho | Risco |
|---|---|---|---|
| C Ecologia | `regionFoodMul`, passo anual, painel da região, `drawCenario`, 3 leis | pequeno | baixo |
| A Rotas | `diplomacyPair`, novo passo anual, `drawMap`, aba no Livro, caravaneiro | médio | médio (desenho e hidratação) |
| B Sucessão | `die`, `facLeaders`, `regimeYear`, `secession`, `mergeFactions`, painel e árvore | médio-grande | médio (muitos casos de borda) |
