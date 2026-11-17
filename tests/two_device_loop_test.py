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

W="(()=>{U.add.blanks.push({id:'m-'+Math.random().toString(36).slice(2,7),q:'me',mine:1,p:4,rk:'r01',lp:4,r:[[.3,.5,.1,.02]],k:[[.3,.5,.1,.02]],chk:false,note:'',t:Date.now()});saveU()})()"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        T,eT=await device(b,'TAB'); P,eP=await device(b,'PC')
        nav={'TAB':0,'PC':0}
        T.on('framenavigated',lambda f:nav.__setitem__('TAB',nav['TAB']+1) if f==T.main_frame else None)
        P.on('framenavigated',lambda f:nav.__setitem__('PC',nav['PC']+1) if f==P.main_frame else None)
        await T.goto(B+'index.html#stay'); await T.wait_for_timeout(800)
        await T.set_input_files('#zipIn','/home/claude/test/test_r01.zip'); await T.wait_for_selector('.pb button',timeout=60000); await T.click('.pb button'); await T.wait_for_timeout(1500)
        await T.goto(B+'app.html'); await T.wait_for_timeout(9000)
        await P.goto(B+'index.html#stay'); await P.wait_for_timeout(800)
        await P.set_input_files('#zipIn','/home/claude/test/test_r01.zip'); await P.wait_for_timeout(5000)
        await P.evaluate("afterConnect()"); await P.wait_for_timeout(2500)
        await P.goto(B+'app.html'); await P.wait_for_timeout(5000)
        n0=dict(nav)
        # 1) 태블릿은 열린 채 가만히, PC에서 공부(저장 6번)
        for k in range(6):
            await P.evaluate(W); await P.wait_for_timeout(8000)
        print('1 idle tablet: extra navigations',{k:nav[k]-n0[k] for k in nav},'pill PC',await P.inner_text('#cloudPill'))
        # 2) 태블릿으로 돌아옴(focus) → 한 번 받기
        n1=dict(nav); await T.evaluate("window.dispatchEvent(new Event('focus'))"); await T.wait_for_timeout(10000)
        print('2 tablet back: navigations',{k:nav[k]-n1[k] for k in nav},'TAB blanks',await T.evaluate("U.add.blanks.filter(b=>b.mine).length"),'PC',await P.evaluate("U.add.blanks.filter(b=>b.mine).length"))
        # 3) 두 기기에서 번갈아 계속 저장(동시에 쓰기) → 되풀이가 멈추는지
        n2=dict(nav)
        for k in range(8):
            try: await (T if k%2 else P).evaluate(W)
            except Exception as e: pass
            await asyncio.sleep(7)
        await asyncio.sleep(8)
        print('3 both active: navigations',{k:nav[k]-n2[k] for k in nav})
        for pg,nm in ((T,'TAB'),(P,'PC')):
            try: print(nm,'pill',await pg.inner_text('#cloudPill'))
            except Exception as e: print(nm,'pill ?',e)
        print('errors',eT+eP); await b.close()
asyncio.run(main())
