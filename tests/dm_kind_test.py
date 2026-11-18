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

MK="(own,y)=>{setMK('dm',own);DMB.t=[{p:3,r:[.2,y,.02,.015]},{p:3,r:[.25,y,.02,.015]}];setMK(false)}"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        T,eT=await device(b,'TAB')
        await T.goto(B+'index.html#stay'); await T.wait_for_timeout(800)
        await T.set_input_files('#zipIn','/home/claude/test/test_r01.zip'); await T.wait_for_selector('.pb button',timeout=60000); await T.click('.pb button'); await T.wait_for_timeout(1500)
        await T.goto(B+'app.html'); await T.wait_for_timeout(4000)
        await T.evaluate(f"({MK})(false,.30)")
        for k in range(5): await T.evaluate(f"({MK})(true,{0.4+k*0.05})")
        print('made',await T.evaluate("U.add.dumunja.map(d=>(d.own?'내':'강사')+':'+dmT(d).length)"))
        await T.evaluate("setMode('quiz')"); await T.wait_for_timeout(500)
        await T.evaluate("jumpTo(3,0.3)"); await T.wait_for_timeout(1200)
        print('page markers',await T.evaluate("[PG[3].ov.querySelectorAll('.dm:not(.own)').length,PG[3].ov.querySelectorAll('.dm.own').length]"))
        # 버튼: 내 두문자 만들기 중엔 강사 버튼 숨김
        await T.evaluate("setMK('dm',true)"); print('buttons while own',await T.evaluate("[$('#dmBtn').hidden,$('#dmBtn2').hidden,$('#dmBtn2').textContent]")); await T.evaluate("setMK(false)")
        print('buttons idle',await T.evaluate("[$('#dmBtn').hidden,$('#dmBtn2').hidden,$('#dmBtn').textContent,$('#dmBtn2').textContent]"))
        # 종류 바꾸기
        await T.evaluate("(()=>{const d=U.add.dumunja[0];patch('dumunja',d.id,{own:d.own?null:1})})()")
        print('after toggle first',await T.evaluate("U.add.dumunja.map(d=>d.own?'내':'강사')"))
        await T.evaluate("(()=>{const d=U.add.dumunja[0];patch('dumunja',d.id,{own:d.own?null:1})})()")
        await T.evaluate("setSide('dm')"); await T.wait_for_timeout(600)
        print('tab items',await T.evaluate("[document.querySelectorAll('.dmit:not(.own)').length,document.querySelectorAll('.dmit.own').length]"))
        await T.screenshot(path='/home/claude/test/dm2.png')
        await T.wait_for_timeout(8000)
        print('drive counts',await T.evaluate("INSA.Local.meta.get('pushedCounts')"))
        await T.reload(); await T.wait_for_timeout(5000)
        print('after reload',await T.evaluate("U.add.dumunja.map(d=>d.own?'내':'강사')"))
        # 내 두문자 4개 지우기 → 드라이브 저장 멈춤
        await T.evaluate("U.add.dumunja.filter(d=>d.own).slice(0,4).forEach(d=>remove('dumunja',d.id));saveU()")
        await T.wait_for_timeout(9000)
        print('pill',await T.inner_text('#cloudPill'))
        print('errors',eT); await b.close()
asyncio.run(main())
