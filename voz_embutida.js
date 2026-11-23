// ---------------------------------------------------------------------
// VOZ EMBUTIDA: fala, diário e crônica sem Ollama (treinadas por treinar_voz.py)
// ---------------------------------------------------------------------
const VOZ=__VOZ_DATA__;
const VOZ_NET=(()=>{const M=VOZ.fala,dq=o=>{const b=atob(o.q),a=new Float32Array(b.length);for(let i=0;i<b.length;i++){let v=b.charCodeAt(i);if(v>127)v-=256;a[i]=v*o.s;}return a;};return {C:M.classes,H:M.H,HID:M.HID,W1:dq(M.W1),b1:M.b1,Wc:dq(M.Wc),bc:M.bc};})();
function vozPick(list){let t=0;list.forEach(x=>t+=x[1]);let r=Math.random()*t;for(const x of list){r-=x[1];if(r<=0)return x[0];}return list[0][0];}
function vozFala(user){const N_=VOZ_NET,t=deuzNorm(user),f=new Set();
  for(const n of [2,3,4])for(let i=0;i<=t.length-n;i++)f.add(fnv(t.slice(i,i+n))%N_.H);
  const ws=t.trim().split(' ');ws.forEach(w=>f.add(fnv('w:'+w)%N_.H));for(let i=0;i+1<ws.length;i++)f.add(fnv('b:'+ws[i]+'_'+ws[i+1])%N_.H);
  const sc=1/Math.max(1,Math.sqrt(f.size)),h=new Float32Array(N_.HID);for(let j=0;j<N_.HID;j++)h[j]=N_.b1[j];
  f.forEach(i=>{const o=i*N_.HID;for(let j=0;j<N_.HID;j++)h[j]+=N_.W1[o+j]*sc;});for(let j=0;j<N_.HID;j++)if(h[j]<0)h[j]=0;
  const k=N_.C.length,z=[];for(let c=0;c<k;c++){let v=N_.bc[c];for(let j=0;j<N_.HID;j++)v+=h[j]*N_.Wc[j*k+c];z.push(v);}
  const m=Math.max(...z),e=z.map(x=>Math.exp((x-m)/1.3)),s=e.reduce((a,b)=>a+b,0);
  const top=e.map((p,i)=>[i,p/s]).sort((a,b)=>b[1]-a[1]).slice(0,3);
  let line=N_.C[vozPick(top)];
  const sit=(user.match(/Situação:\s*(.*)$/)||[0,''])[1],nm=(user.match(/Nome:\s*([^.]+)\./)||[0,''])[1].trim();
  const outro=(sit.match(/\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\p{L}]+/gu)||[]).filter(w=>w!==nm)[0];
  return line.replace(/\{B\}/g,outro||'meu amigo').replace(/\{D\}/g,'essa descoberta').replace(/\{P\}/g,'meu povo');}
function vozDiario(user){const fm=user.match(/Fatos de hoje:\s*(.*?)\.\s*Humor:/s);if(!fm)throw new Error('sem fatos');
  const fatos=fm[1].split(/;\s*/).filter(Boolean);let b=0,r=0;
  fatos.forEach(f=>{try{const w=estoriaWeigh(f);if(w.boa)b++;else r++;}catch(e){}});
  const mood=b&&r?'misturado':b?'bom':r?'ruim':(/difícil/.test(user)?'ruim':/bom dia/.test(user)?'bom':'misturado');
  const D=VOZ.diario[mood];const cap1=s=>s.charAt(0).toUpperCase()+s.slice(1);
  return `${vozPick(D.a)} ${cap1(fatos.join('; '))}. ${vozPick(D.f)}`;}
function vozCronica(user){const fm=user.match(/Acontecimentos:\s*(.*)\.\s*$/s);if(!fm)throw new Error('sem fatos');
  const evs=fm[1].split(/;\s*/).filter(Boolean),cats={};
  evs.forEach(e=>{try{const c=netPredict(CHR_NET,e).cls;if(c!=='cotidiano')cats[c]=(cats[c]||0)+1;}catch(_){}});
  const mk=Object.entries(cats).sort((a,b)=>b[1]-a[1])[0];
  const ab=mk&&VOZ.cronica.marca[mk[0]]?`Uma semana marcada ${VOZ.cronica.marca[mk[0]]}.`:'Uma semana de acontecimentos.';
  return `${ab} ${evs.map(e=>e.replace(/[.!?]+$/,'')).join('. ')}. ${vozPick(VOZ.cronica.f)}`;}
function vozLocal(system,user,json){
  if(json)throw new Error('a voz embutida não interpreta comandos livres (use o Ollama para isso)');
  if(/habitante do jogo/.test(system))return vozFala(user);
  if(/Estoria/.test(system))return vozDiario(user);
  if(/Chronos/.test(system))return vozCronica(user);
  throw new Error('a voz embutida não cobre esse pedido');}
