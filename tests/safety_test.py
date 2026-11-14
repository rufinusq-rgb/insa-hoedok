import asyncio
from playwright.async_api import async_playwright
B='http://localhost:8765/insa-hoedok/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        ctx = await b.new_context(viewport={'width':1280,'height':900}); page = await ctx.new_page()
        errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
        page.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
        await page.goto(B+'index.html#stay'); await page.wait_for_timeout(800)
        await page.set_input_files('#zipIn','/home/claude/test/test_r01.zip')
        await page.wait_for_selector('.pb button', timeout=60000); await page.click('.pb button'); await page.wait_for_timeout(500)
        await page.goto(B+'app.html'); await page.wait_for_timeout(4000)
        cnt="(()=>[(U.add.blanks||[]).filter(b=>b.mine).length,(U.add.dumunja||[]).length,JSON.stringify((NOTES.p3||{memos:[]}).memos.map(m=>m.t))])()"
        print('start',await page.evaluate(cnt))
        # 갑자기 꺼짐 흉내: 기기 저장(flush)이 아예 안 일어나게 막고 작업
        await page.evaluate("""(()=>{Store.flush=async()=>{};window.removeEventListener;
          const b={id:'m-test1',q:'me',mine:1,p:12,rk:'r01',lp:12,r:[[.3,.3,.1,.02]],k:[[.3,.3,.1,.02]],chk:false,note:'',t:Date.now()};U.add.blanks.push(b);saveU();
          const m={id:'mm1',x:.3,y:.3,w:.26,h:.09,t:'갑자기꺼짐메모',f:false};note(3).memos.push(m);saveNote(3);})()""")
        await page.wait_for_timeout(1500)
        # 탭을 강제로 닫고(저장 기회 없음) 새로 열기
        await page.close(run_before_unload=False)
        page = await ctx.new_page(); page.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
        await page.goto(B+'app.html'); await page.wait_for_timeout(4000)
        print('after kill+reopen',await page.evaluate(cnt))
        await page.wait_for_timeout(1500)
        print('pend left',await page.evaluate("Object.keys(localStorage).filter(k=>k.startsWith('insa:pend'))"))
        await page.reload(); await page.wait_for_timeout(4000)
        print('after 2nd reload',await page.evaluate(cnt))
        # 줄어듦 장치 (드라이브 흉내)
        r=await page.evaluate("""(async()=>{const I=window.INSA;const names=[];I.Drive.find=async()=>null;I.Drive.saveText=async n=>{names.push(n)};
          await I.Local.meta.put('pushedCounts',{b:1,d:10,m:10});
          let msg='';try{await I.Sync.push()}catch(e){msg=e.code+' '+e.message}
          await I.Local.meta.put('pushedCounts',{b:1,d:0,m:1});names.length=0;let ok='';try{await I.Sync.push();ok='pushed'}catch(e){ok='ERR '+e.message}
          return [msg,ok,names]})()""")
        print(r)
        print('errors',errs)
        await b.close()
asyncio.run(main())
