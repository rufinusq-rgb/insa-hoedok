# 태블릿·PC 번갈아 쓰기 시험: 두 브라우저(기기)가 가짜 드라이브 하나를 같이 쓴다.
# A) PC에서 만든 빈칸이, 태블릿 앱으로 돌아오면(focus) 자동으로 받아져 보이는지
# B) 태블릿에 아직 안 올라간 작업이 있을 때: 묻고(확인) → 받아 오고, 태블릿 작업은 충돌보관 + 되살리기로 남는지
import asyncio,json,time
from playwright.async_api import async_playwright
B='http://localhost:8765/insa-hoedok/'
STORE={}; SEQ=[0]
def drive(op,a):
    a=json.loads(a)
    if op=='find':
        f=STORE.get(a['name']); return json.dumps(f and {'id':f['id'],'name':a['name'],'modifiedTime':f['mt'],'size':len(f['text'])})
    if op=='readText':
        for n,f in STORE.items():
            if f['id']==a['id']: return json.dumps(f['text'])
        return json.dumps(None)
    if op=='saveText':
        SEQ[0]+=1; STORE[a['name']]={'id':'f%d'%SEQ[0],'text':a['text'],'mt':time.strftime('%Y-%m-%dT%H:%M:%S.000Z',time.gmtime(time.time()))}; return json.dumps({'id':STORE[a['name']]['id']})
    if op=='list':
        return json.dumps([{'id':f['id'],'name':n,'size':len(f['text']),'modifiedTime':f['mt']} for n,f in STORE.items()]+[{'id':'z1','name':'교재_r0%d.zip'%k,'size':1} for k in range(1,6)])
    return json.dumps(None)
INIT="""
localStorage.setItem('insa:tok',JSON.stringify({tok:'t',exp:Date.now()+36e5}));
let _I;Object.defineProperty(window,'INSA',{configurable:true,get(){return _I},set(v){_I=v;const D=v.Drive;const c=(op,a)=>window.mockDrive(op,JSON.stringify(a||{})).then(JSON.parse);
  D.connect=async()=>{};D.folder=async()=>'fold';D.find=n=>c('find',{name:n});D.readText=id=>c('readText',{id});D.saveText=(name,text)=>c('saveText',{name,text});
  D.list=()=>c('list');D.saveBlob=async()=>({id:'b'});}});
"""
CNT="JSON.stringify((U.add.blanks||[]).map(b=>b.id).sort())"
async def device(b,name):
    ctx=await b.new_context(viewport={'width':1300,'height':900})
    await ctx.expose_function('mockDrive',drive); await ctx.add_init_script(INIT)
    page=await ctx.new_page(); errs=[]; page.on('pageerror',lambda e:errs.append(name+': '+str(e)))
    page.on('dialog',lambda d:(print(name,'DIALOG:',d.message[:60].replace('\n',' ')),asyncio.ensure_future(d.accept())))
    return page,errs

NT="JSON.stringify({m:(note(3).memos||[]).map(m=>m.t).sort(),s:(note(3).strokes||[]).length,del:note(3).mdel||[]})"
def memo(t,mid): return "(()=>{const m={id:'%s',x:.3,y:.3,w:.26,h:.09,t:'%s',f:false};note(3).memos.push(m);saveNote(3)})()"%(mid,t)
STROKE="(()=>{note(3).strokes.push({c:'#d33',w:2,p:[[.2,.2],[.3,.3]]});penTouch(3);saveNote(3)})()"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        T,eT=await device(b,'TAB'); P,eP=await device(b,'PC')
        await T.goto(B+'index.html#stay'); await T.wait_for_timeout(800)
        await T.set_input_files('#zipIn','/home/claude/test/test_r01.zip'); await T.wait_for_selector('.pb button',timeout=60000); await T.click('.pb button'); await T.wait_for_timeout(1500)
        await T.goto(B+'app.html'); await T.wait_for_timeout(4000)
        await T.evaluate(memo('M0','m0')); await T.evaluate(STROKE); await T.wait_for_timeout(8000)
        print('TAB start',await T.evaluate(NT))
        await P.goto(B+'index.html#stay'); await P.wait_for_timeout(800)
        await P.set_input_files('#zipIn','/home/claude/test/test_r01.zip'); await P.wait_for_timeout(5000)
        await P.evaluate("afterConnect()"); await P.wait_for_timeout(2500)
        await P.goto(B+'app.html'); await P.wait_for_timeout(4000)
        print('PC start',await P.evaluate(NT))
        # PC: 메모 추가 + M0 지우기(앱의 지우기와 같은 방식)
        await P.evaluate(memo('Mpc','mpc'))
        await P.evaluate("(()=>{const N=note(3);const m=N.memos.find(x=>x.id==='m0');N.memos=N.memos.filter(x=>x!==m);(N.mdel=N.mdel||[]).push(m.id);saveNote(3)})()")
        await P.wait_for_timeout(8000)
        # 태블릿: 아직 모르는 채로 메모 + 펜 → 돌아옴
        await T.evaluate(memo('Mtab','mtab')); await T.evaluate(STROKE); await T.wait_for_timeout(1200)
        await T.evaluate("window.dispatchEvent(new Event('focus'))"); await T.wait_for_timeout(12000)
        print('TAB after',await T.evaluate(NT))
        await P.evaluate("window.dispatchEvent(new Event('focus'))"); await P.wait_for_timeout(12000)
        print('PC after',await P.evaluate(NT))
        latest=json.loads(STORE['기록_최신.json']['text']); n=[v['v'] for k,v in latest['docs'].items() if k.endswith('/notes/p3')]
        print('drive p3',n and {'m':sorted(x['t'] for x in n[0]['memos']),'s':len(n[0]['strokes'])})
        print('errors',eT+eP); await b.close()
asyncio.run(main())
