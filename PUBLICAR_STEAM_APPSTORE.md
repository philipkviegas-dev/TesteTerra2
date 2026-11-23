# Ilha Viva — plano para Steam e App Store

Legenda: ✅ confirmado em fonte oficial ou citada · ⚠️ precisa conferir antes de pagar ou enviar.

## Visão geral
O jogo é um único `ilha-viva.html` (≈5,7 MB, tudo embutido, funciona offline). Isso ajuda: dá para embrulhar o mesmo arquivo para as duas lojas.

| | Steam (PC) | App Store (iPhone/iPad) |
|---|---|---|
| Embrulho | Electron (+ Greenworks para conquistas/nuvem, opcional) | Capacitor (WebView nativo) |
| Custo de entrada | US$ 100 por jogo (✅, recuperável após US$ 1.000 de receita) | ⚠️ US$ 99/ano (só vi fonte de terceiros) |
| Precisa de Mac? | Não | ⚠️ Provavelmente sim (Xcode só roda em macOS) |
| Risco de recusa | Baixo (revisão técnica rápida) | **Alto** (guideline 4.2, "app que é só um site") |
| Espera | ✅ 30 dias entre pagar a taxa e lançar | Revisão de dias; recusas comuns |

**Recomendação:** começar pela **Steam**. É mais barata, não exige Mac e o risco de recusa é bem menor. A App Store vem depois, com recursos nativos de verdade.

---

## STEAM

### Fase 1 — Conta e custos
- [ ] Criar conta de parceiro no Steamworks (partner.steamgames.com).
- [ ] Onboarding: dados bancários, impostos e verificação de identidade. ✅ leva de 1 a 5 dias.
- [ ] Pagar a taxa Steam Direct: ✅ US$ 100 por app, não reembolsável, mas recuperada no pagamento após US$ 1.000 de receita bruta ajustada. Só quem tem permissão Admin paga.
- [ ] ✅ Contar 30 dias entre pagar a taxa e poder lançar (Valve). Uma fonte de terceiros diz 21 dias; vale a regra da Valve.

### Fase 2 — Empacotar (Electron)
- [ ] Criar a pasta `steam/` com `package.json`, `main.js` (abre `ilha-viva.html` em janela) e ícone 512×512.
- [ ] Empacotar com electron-builder para `.exe` (Windows). Mac/Linux são opcionais.
- [ ] Testar offline: voz embutida, salvar/carregar e exportar `.ivsave` (o IndexedDB funciona no Electron).
- [ ] Opcional, depois: Greenworks para conquistas e Steam Cloud. Para testar precisa de `steam_appid.txt`. ⚠️ Não confirmei o steamworks.js como alternativa mais nova. NW.js foi relatado como descontinuado, então fica Electron.
- [ ] Enviar a build com o SteamPipe (ferramenta da Valve, no Steamworks).

### Fase 3 — Página da loja
- [ ] Capsules (imagens de vitrine), capturas de tela, trailer curto, descrição em PT-BR e inglês, tags, classificação etária.
- [ ] ⚠️ A lista exata de tamanhos de imagem fica no painel do Steamworks; conferir lá.
- [ ] Publicar a página "Em breve" cedo para juntar lista de desejos. ⚠️ Fontes divergem sobre prazo mínimo; conferir no Steamworks.
- [ ] ✅ Revisão da Valve: eles rodam o jogo e conferem se bate com a página. Costuma levar de 1 a 5 dias úteis.

### Fase 4 — Lançamento
- [ ] Definir preço (ou gratuito) e data. Lançar depois dos 30 dias.
- [ ] Acompanhar avaliações e corrigir em atualizações.

---

## APP STORE

### Fase 1 — Conta
- [ ] Inscrição no Apple Developer Program. ⚠️ US$ 99/ano: só vi em fonte de terceiros; confirmar em developer.apple.com.
- [ ] ⚠️ Mac com Xcode para compilar e enviar o app (Capacitor/iOS normalmente exige). Sem Mac, dá para alugar um Mac na nuvem, mas confirmar antes.

### Fase 2 — Empacotar (Capacitor)
- [ ] Criar projeto Capacitor apontando para o `ilha-viva.html`.
- [ ] Ajustar para toque: botões maiores, sem dependência de mouse e teclado, tela cheia, orientação.
- [ ] Testar desempenho no iPhone (o mundo grande pesa; talvez limitar população no celular).
- [ ] Salvar dentro do app (IndexedDB do WebView pode ser apagado pelo iOS; o botão `.ivsave` ajuda).

### Fase 3 — Passar pela revisão (o ponto crítico)
- [ ] ✅ A guideline 4.2 (funcionalidade mínima) recusa app que é basicamente um site. Relatos: "não é suficientemente diferente da navegação no celular".
- [ ] Adicionar recursos nativos reais: notificações locais ("seu habitante tem novidades"), vibração tátil, compartilhar o mundo, integração com o Game Center. ⚠️ Recursos nativos sozinhos não garantem aprovação (há relato de recusa mesmo assim).
- [ ] Mostrar valor de jogo de verdade: o app precisa ser um jogo completo, não uma demonstração.
- [ ] Ficha: ícone, capturas por tamanho de tela, política de privacidade (o jogo não coleta dados, ajuda), classificação etária.

### Fase 4 — Enviar
- [ ] Enviar pelo Xcode / App Store Connect, responder ao revisor se pedirem esclarecimentos, lançar.

---

## O que posso fazer por você (nada foi enviado nem pago)
1. Montar a pasta `steam/` com Electron e gerar o `.exe` para testar.
2. Escrever a política de privacidade e os textos da loja (PT-BR e inglês).
3. Adaptar o jogo para toque (preparação para o celular).
4. Pesquisar o que ficou ⚠️ (taxa e requisitos oficiais da Apple, lista de imagens da Steam).

Taxas, contas e envios são todos seus; eu não pago nem envio nada.

## Fontes
- [Steamworks: taxa do app](https://partner.steamgames.com/doc/gettingstarted/appfee)
- [Steamworks: onboarding](https://partner.steamgames.com/doc/gettingstarted/onboarding)
- [Steam Direct](https://partner.steamgames.com/steamdirect)
- [Phaser: publicar jogos web na Steam com Electron](https://phaser.io/news/2025/03/publishing-web-games-on-steam-with-electron)
- [DEV: publicar jogo web na Steam com Electron](https://dev.to/jacklehamster/publish-your-web-game-to-steam-using-electron-670)
- [Greenworks (GitHub)](https://github.com/greenheartgames/greenworks)
- [Apple App Review](https://developer.apple.com/distribute/app-review)
- [Fórum Apple: recusa pela 4.2](https://developer.apple.com/forums/thread/835422)
- [Capawesome: 11 passos para levar um app web à App Store](https://capawesome.io/blog/11-steps-to-get-your-web-app-on-the-app-store/)
- [Capgo: passar na revisão da App Store em 2026](https://capgo.app/de/blog/how-to-pass-app-store-review-2026/)
