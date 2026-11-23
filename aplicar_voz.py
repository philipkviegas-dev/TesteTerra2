# Injeta a voz embutida (fala, diário, crônica) e os botões de exportar/importar partida no jogo.
# Uso: python aplicar_voz.py ilha-viva.html [publicar/index.html ...]
import sys, json, shutil, os
sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open('modelos/voz.json', encoding='utf-8'))
js = open('voz_embutida.js', encoding='utf-8').read().replace('__VOZ_DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')))

SAVE_JS = r"""
// Exportar / importar partida (arquivo .ivsave) para levar o mundo a outro navegador ou computador
function _u8(x){if(typeof x==='string')return new TextEncoder().encode(x);if(ArrayBuffer.isView(x))return new Uint8Array(x.buffer,x.byteOffset,x.byteLength);return new Uint8Array(x);}
async function saveExport(){
  if(!started){setSaveMsg('Comece uma partida antes de exportar.');return;}
  while(saving)await new Promise(r=>setTimeout(r,100));
  if(!await saveGame(true)){setSaveMsg('Não foi possível preparar o arquivo agora.');return;}
  const d=await IDB.get(SAVE_KEY);if(!d){setSaveMsg('Nada para exportar.');return;}
  const parts=[];const add=x=>{const u=_u8(x);parts.push(u);return {s:typeof x==='string'?1:0,n:u.length};};
  const hdr={v:1,day,z:add(d.z),dorm:null};
  if(d.dorm){hdr.dorm={meta:add(d.dorm.meta),bin:{}};for(const k in d.dorm.bin){const e=d.dorm.bin[k];hdr.dorm.bin[k]={t:e.t,z:add(e.z)};}}
  const hb=new TextEncoder().encode(JSON.stringify(hdr)),len=new Uint8Array(4);new DataView(len.buffer).setUint32(0,hb.length);
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([len,hb,...parts],{type:'application/octet-stream'}));a.download=`ilha-viva-ano${day}.ivsave`;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),4000);
  setSaveMsg(`⬇️ Partida exportada (ano ${day}). Guarde o arquivo .ivsave; importe com ⬆️ onde quiser.`);
}
async function saveImport(file){
  try{const buf=await file.arrayBuffer(),dv=new DataView(buf),hl=dv.getUint32(0),hdr=JSON.parse(new TextDecoder().decode(new Uint8Array(buf,4,hl)));
    if(hdr.v!==1)throw new Error('versão desconhecida');let off=4+hl;
    const take=e=>{const s=buf.slice(off,off+e.n);off+=e.n;return e.s?new TextDecoder().decode(s):s;};
    const obj={z:take(hdr.z)};if(hdr.dorm){obj.dorm={meta:take(hdr.dorm.meta),bin:{}};for(const k in hdr.dorm.bin){const e=hdr.dorm.bin[k];obj.dorm.bin[k]={t:e.t,z:take(e.z)};}}
    await IDB.put(SAVE_KEY,obj);setSaveMsg('⬆️ Arquivo lido. Carregando…');await loadGame();
  }catch(e){console.error(e);setSaveMsg('Esse arquivo não é uma partida válida do Ilha Viva.');}
}
"""

def rep(s, a, b, n=1):
    assert s.count(a) == n, (a[:70], s.count(a))
    return s.replace(a, b)

def patch(path):
    if os.path.exists(path) and 'VOZ_NET' in open(path, encoding='utf-8').read():
        print(path, 'já tem a voz embutida, pulando'); return
    base = path.replace('.html', '_antes_voz.html')
    if not path.startswith('publicar'): shutil.copyfile(path, base)
    s = open(path, encoding='utf-8').read()
    s = rep(s, "const LLM={mode:'ollama',", js + "const LLM={mode:'embutida',")
    s = rep(s, "    if(LLM.mode==='ollama'){\n      const body", "    if(LLM.mode==='embutida'){text=vozLocal(system,user,json);}\n    else if(LLM.mode==='ollama'){\n      const body")
    s = rep(s, "catch(e){LLM.fail++;LLM.lastErr=e.message;throw e;}", "catch(e){if(LLM.mode!=='embutida')LLM.fail++;LLM.lastErr=e.message;throw e;}")
    s = rep(s, "function updateAiStatus(){const el=document.getElementById('aiStatus');if(el)el.textContent=`· ${LLM.model}", "function updateAiStatus(){const el=document.getElementById('aiStatus');const b=document.getElementById('aiOllama');if(b)b.textContent=LLM.mode==='ollama'?'Voltar para a voz embutida':'Usar o Ollama no meu PC (opcional)';if(el)el.textContent=LLM.mode==='embutida'?`· voz embutida (funciona offline) · ${LLM.ok} falas/textos`:`· ${LLM.model}")
    s = rep(s, "LLM.up=false;setAiLog('Ollama aberto, mas", "LLM.mode='embutida';LLM.up=true;updateAiStatus();setAiLog('Ollama aberto, mas")
    s = rep(s, "LLM.up=false;setAiLog('Ollama não encontrado: o jogo usa as regras internas até você abri-lo.');", "LLM.mode='embutida';LLM.up=true;updateAiStatus();setAiLog('Ollama não encontrado: voltei para a voz embutida.');")
    s = rep(s, "  if(!LLM.up)setTimeout(detectaIA,15000);}\ndetectaIA();\n", "  }\ndocument.getElementById('aiOllama').onclick=()=>{if(LLM.mode==='ollama'){LLM.mode='embutida';LLM.up=true;updateAiStatus();setAiLog('Voz embutida ativada.');}else{LLM.mode='ollama';LLM.up=undefined;setAiLog('Procurando o Ollama…');updateAiStatus();detectaIA();}};\n")
    s = rep(s, "O jogo usa a IA treinada do Ilha Viva (modelo <b>ilhaviva</b>, rodando no seu PC pelo Ollama). Ela interpreta comandos livres, narra os resultados e escreve o diário e a crônica. Se o Ollama estiver fechado, o jogo continua com as regras internas.",
      "O jogo já traz <b>pequenas IAs treinadas dentro dele</b>: uma para as <b>falas</b>, uma para o <b>diário</b> e uma para a <b>crônica</b>. Funcionam no navegador, sem baixar nada nem internet. (A narração da Fábula e os comandos livres continuam por regras.) <br>Opcional, só para quem quer mais: se você instalou o <b>Ollama</b> com o modelo <b>ilhaviva</b>, dá para usá-lo no lugar.")
    s = rep(s, '<div style="margin-top:6px"><button id="aiTest">Testar IA</button></div>', '<div style="margin-top:6px"><button id="aiTest">Testar IA</button> <button id="aiOllama">Usar o Ollama no meu PC (opcional)</button></div>')
    s = rep(s, '<button id="loadBtn" title="Continuar a partida salva">📂</button>', '<button id="loadBtn" title="Continuar a partida salva">📂</button><button id="expBtn" title="Baixar a partida como arquivo .ivsave">⬇️</button><button id="impBtn" title="Carregar uma partida de arquivo .ivsave">⬆️</button><input type="file" id="impFile" accept=".ivsave" style="display:none">')
    s = rep(s, "function savedInfo(){", SAVE_JS + "function savedInfo(){")
    s = rep(s, "document.getElementById('loadBtn').onclick=()=>loadGame();", "document.getElementById('loadBtn').onclick=()=>loadGame();\ndocument.getElementById('expBtn').onclick=()=>saveExport();\ndocument.getElementById('impBtn').onclick=()=>document.getElementById('impFile').click();\ndocument.getElementById('impFile').onchange=e=>{const f=e.target.files[0];e.target.value='';if(f)saveImport(f);};")
    open(path, 'w', encoding='utf-8').write(s)
    print('ok', path, len(s)//1024, 'KB')

for p in sys.argv[1:]: patch(p)
