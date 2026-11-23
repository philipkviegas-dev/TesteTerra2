# Retreina na GPU os modelos pequenos que rodam dentro do jogo (Deuz, Arquiteto, Fábula, Estoria, Chronos, Fantasy e a mente dos habitantes).
# Mais dados aumentados, rede maior, parada antecipada. Exporta no mesmo formato que o jogo lê (pesos int8 em base64).
import json, glob, os, random, base64, unicodedata, re, numpy as np, torch, torch.nn as nn
dev = 'cuda' if torch.cuda.is_available() else 'cpu'; print('dispositivo:', dev)
def norm(t):
    t=''.join(c for c in unicodedata.normalize('NFD',t.lower()) if unicodedata.category(c)!='Mn')
    return ' '+' '.join(re.sub(r'[^a-z0-9 ]',' ',t).split())+' '
def fnv(s):
    h=0x811c9dc5
    for ch in s: h^=ord(ch); h=(h*0x01000193)&0xffffffff
    return h
def feats(t,H):
    t=norm(t); f=set()
    for n in (2,3,4):
        for i in range(len(t)-n+1): f.add(fnv(t[i:i+n])%H)
    ws=t.split()
    for w in ws: f.add(fnv('w:'+w)%H)
    for a,b in zip(ws,ws[1:]): f.add(fnv('b:'+a+'_'+b)%H)
    return list(f)
def aug(t):
    w=t.split()
    if len(w)>2 and random.random()<.4: del w[random.randrange(len(w))]
    if len(w)>2 and random.random()<.3: i=random.randrange(len(w)-1); w[i],w[i+1]=w[i+1],w[i]
    t=' '.join(w)
    if len(t)>5 and random.random()<.4: i=random.randrange(1,len(t)-1); t=t[:i]+t[i+1:]
    return t
def q8(a):
    a=a.detach().cpu().numpy().astype(np.float32); s=float(np.abs(a).max())/127 or 1
    return {'s':s,'q':base64.b64encode(np.round(a/s).astype(np.int8).tobytes()).decode(),'shape':list(a.shape)}
def to_x(rows,H):
    X=torch.zeros(len(rows),H)
    for i,r in enumerate(rows):
        f=feats(r['t'],H); X[i,f]=1/np.sqrt(max(1,len(f)))
    return X
RAPIDO=os.environ.get('RAPIDO')  # só para testar o script: poucos dados e poucas épocas
def treinar_texto(nome, arq, H=4096, HID=128, K2=3, mask=None, copias=3, epocas=25):
    D=json.load(open(arq,encoding='utf-8')); C=D['classes']
    if RAPIDO: D['train']=D['train'][:1500]; D['test']=D['test'][:300]; epocas=2; copias=1
    tr=D['train']+[{**r,'t':aug(r['t'])} for r in D['train'] for _ in range(copias)]
    Xtr=to_x(tr,H); ytr=torch.tensor([r['c'] for r in tr]); str_=torch.tensor([r['s'] for r in tr])
    Xte=to_x(D['test'],H); yte=torch.tensor([r['c'] for r in D['test']])
    W1=nn.Linear(H,HID); Wc=nn.Linear(HID,len(C)); Ws=nn.Linear(HID,K2); drop=nn.Dropout(0.25)
    ps=list(W1.parameters())+list(Wc.parameters())+list(Ws.parameters()); [m.to(dev) for m in (W1,Wc,Ws)]
    opt=torch.optim.AdamW(ps,lr=3e-3,weight_decay=1e-4); sched=torch.optim.lr_scheduler.CosineAnnealingLR(opt,epocas)
    ce=nn.CrossEntropyLoss(label_smoothing=0.05); m_id=C.index(mask) if mask in C else -1
    best=-1; keep=None
    for ep in range(epocas):
        perm=torch.randperm(len(Xtr))
        for k in range(0,len(perm),512):
            b=perm[k:k+512]; x=Xtr[b].to(dev); h=drop(torch.relu(W1(x)))
            loss=ce(Wc(h),ytr[b].to(dev)); msk=(ytr[b]!=m_id).to(dev)
            if msk.any(): loss=loss+0.6*ce(Ws(h)[msk],str_[b].to(dev)[msk])
            opt.zero_grad(); loss.backward(); opt.step()
        sched.step()
        with torch.no_grad(): acc=(Wc(torch.relu(W1(Xte.to(dev)))).argmax(1).cpu()==yte).float().mean().item()
        if acc>=best: best=acc; keep={'W1':W1.weight.T.clone(),'b1':W1.bias.clone(),'Wc':Wc.weight.T.clone(),'bc':Wc.bias.clone(),'Ws':Ws.weight.T.clone(),'bs':Ws.bias.clone()}
        print(f'  {nome} época {ep+1}: {acc*100:.1f}%')
    out={'classes':C,'H':H,'HID':HID,'W1':q8(keep['W1']),'b1':keep['b1'].tolist(),'Wc':q8(keep['Wc']),'bc':keep['bc'].tolist(),'Ws':q8(keep['Ws']),'bs':keep['bs'].tolist()}
    os.makedirs('modelos',exist_ok=True); json.dump(out,open(f'modelos/{nome}.json','w')); print(f'{nome}: melhor {best*100:.1f}% → modelos/{nome}.json')
    if os.path.exists(f'testes/{nome}.py'):
        ns={}; exec(open(f'testes/{nome}.py',encoding='utf-8').read(),ns); HAND=ns['HAND']
        with torch.no_grad():
            X=to_x([{'t':t} for t,_ in HAND],H).to(dev); p=Wc.weight.new_tensor(0)
            W1.weight.data=keep['W1'].T; W1.bias.data=keep['b1']; Wc.weight.data=keep['Wc'].T; Wc.bias.data=keep['bc']
            pred=Wc(torch.relu(W1(X))).argmax(1).cpu().tolist()
        print(f'  frases novas: {sum(C[p]==c for p,(t,c) in zip(pred,HAND))}/{len(HAND)}')
def treinar_mente():
    X=[];A=[];R=[]
    for f in glob.glob('dados/mente/*.json')[: (1 if RAPIDO else 99)]:
        for d in json.load(open(f)): X.append(d['x']); A.append(d['a']); R.append(d['r'])
    X=torch.tensor(X,dtype=torch.float32); A=torch.tensor(A); R=torch.tensor(R,dtype=torch.float32)/20
    n=len(X); idx=torch.randperm(n); te=idx[:n//10]; tr=idx[n//10:]
    net=nn.Sequential(nn.Linear(X.shape[1],128),nn.ReLU(),nn.Linear(128,128),nn.ReLU(),nn.Linear(128,10)).to(dev)
    opt=torch.optim.AdamW(net.parameters(),lr=1e-3,weight_decay=1e-4); best=9; keep=None
    for ep in range(2 if RAPIDO else 30):
        perm=tr[torch.randperm(len(tr))]
        for k in range(0,len(perm),1024):
            b=perm[k:k+1024]; q=net(X[b].to(dev)); loss=((q.gather(1,A[b].to(dev)[:,None]).squeeze(1)-R[b].to(dev))**2).mean()
            opt.zero_grad(); loss.backward(); opt.step()
        with torch.no_grad(): e=((net(X[te].to(dev)).gather(1,A[te].to(dev)[:,None]).squeeze(1)-R[te].to(dev))**2).mean().item()
        print(f'  mente época {ep+1}: erro {e:.4f}')
        if e<best: best=e; keep=[p.clone() for p in net.parameters()]
    L=keep; out={'D':X.shape[1],'HID':128,'NA':10,'W1':q8(L[0].T),'b1':L[1].tolist(),'W2':q8(L[2].T),'b2':L[3].tolist(),'W3':q8(L[4].T),'b3':L[5].tolist()}
    json.dump(out,open('modelos/mente.json','w')); print(f'mente: melhor erro {best:.4f} → modelos/mente.json')
if __name__=='__main__':
    random.seed(1); torch.manual_seed(1)
    treinar_texto('deuz','dados/deuz.json',K2=3,mask='nada')
    treinar_texto('arquiteto','dados/arquiteto.json',K2=3,mask='nada',copias=1)
    treinar_texto('fabula','dados/fabula.json',K2=2,mask='outro')
    treinar_texto('estoria','dados/estoria.json',K2=3,HID=64)
    treinar_texto('chronos','dados/chronos.json',K2=3)
    treinar_texto('fantasy','dados/fantasy.json',K2=2,mask='nada')
    treinar_mente()
    print('Pronto. Agora rode: python aplicar_modelos.py')
