# 바꿔 넣은 교재 그림: 드라이브 보관(올리기), 다른 기기(그림 없음)에서 원래 그림 + 목차 띠, 드라이브에서 받아 오면 바꾼 그림 + 띠 없음
# 필요: /home/claude/test/test_r05rec.zip (r05_test.py 참고). 드라이브는 localStorage 'FAKE_DRIVE'로 흉내.
import asyncio
from playwright.async_api import async_playwright
B='http://localhost:8765/insa-hoedok/'
FAKE="""(()=>{const t=setInterval(()=>{const I=window.INSA;if(!I)return;clearInterval(t);
const ld=()=>JSON.parse(localStorage.getItem('FAKE_DRIVE')||'{}'),sv=o=>localStorage.setItem('FAKE_DRIVE',JSON.stringify(o));
I.Drive.token=()=>localStorage.getItem('FAKE_OFF')?null:'tok';I.Drive.configured=()=>true;
I.Drive.list=async(pre)=>Object.keys(ld()).filter(n=>!pre||n.startsWith(pre)).map(n=>({id:n,name:n,size:1,modifiedTime:new Date().toISOString()}));
I.Drive.saveBlob=async(n,b)=>{const d=await new Promise(r=>{const f=new FileReader();f.onload=()=>r(f.result);f.readAsDataURL(b)});const o=ld();o[n]=d;sv(o);window.UPN=(window.UPN||0)+1;return n};
I.Drive.readBlob=async(id)=>{const d=ld()[id];return await (await fetch(d)).blob()};
I.Sync.push=async()=>Date.now();I.Sync.pull=async()=>({action:'none'});},5)})();"""
async def st(page,i):
    return await page.evaluate(f"({{src:PG[{i}].img.getAttribute('src'),bands:PG[{i}].ov.querySelectorAll('.band').length,noimg:NOIMG.has({i}),nat:PG[{i}].img.naturalWidth}})")
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        ctx=await b.new_context(viewport={'width':1400,'height':1000}); await ctx.add_init_script(FAKE)
        page=await ctx.new_page(); errs=[]; page.on('pageerror',lambda e:errs.append(str(e))); page.on('dialog',lambda d:asyncio.ensure_future(d.accept()))
        await page.goto(B+'index.html#stay'); await page.wait_for_timeout(800)
        await page.evaluate("localStorage.setItem('FAKE_OFF','1')")
        await page.set_input_files('#zipIn','/home/claude/test/test_r05rec.zip')
        await page.wait_for_selector('.pb button',timeout=90000); await page.click('.pb button'); await page.wait_for_timeout(1500)
        await page.goto(B+'app.html'); await page.wait_for_timeout(6000)
        i=await page.evaluate("D.pages.findIndex(p=>p.label==='195')")
        await page.evaluate(f"jumpTo({i},0)"); await page.wait_for_timeout(1500)
        print('before replace',await st(page,i))
        # 바꾸기 흉내: 빨간 그림을 assets.upload로 넣고 기록에 적는다(드라이브 끊긴 상태)
        await page.evaluate(f"""(async()=>{{const c=document.createElement('canvas');c.width=1344;c.height=1900;const x=c.getContext('2d');x.fillStyle='#f88';x.fillRect(0,0,c.width,c.height);
          const blob=await new Promise(r=>c.toBlob(r,'image/jpeg',.8));const a=await window.claude.use('assets');const up=await a.upload(blob,{{type:'image/jpeg'}});
          U.pageImg[sk({i})]=up.id;saveU();NOIMG.delete({i});PG[{i}].img.src=pageSrc({i});renderPage({i});window.LOGS=[];await syncImgs(t=>LOGS.push(t))}})()""")
        await page.wait_for_timeout(1500)
        print('after replace (offline)',await st(page,i),await page.evaluate("LOGS"))
        # 드라이브 연결 → 앱으로 돌아오면 보관
        await page.evaluate("localStorage.removeItem('FAKE_OFF');IMGSYNC_T=0")
        await page.evaluate("syncImgs(t=>LOGS.push(t))"); await page.wait_for_timeout(1500)
        print('drive files',await page.evaluate("Object.keys(JSON.parse(localStorage.getItem('FAKE_DRIVE')||'{}'))"),await page.evaluate("LOGS.slice(-2)"))
        await page.reload(); await page.wait_for_timeout(5000)
        await page.evaluate(f"jumpTo({i},0)"); await page.wait_for_timeout(1500)
        print('reload same device',await st(page,i),'uploads',await page.evaluate("window.UPN||0"))
        # 다른 기기 흉내: 이 기기 그림을 지운다(IDB blobs + 캐시)
        id_=await page.evaluate(f"U.pageImg[sk({i})]")
        await page.evaluate(f"""(async()=>{{const c=await caches.open(INSA.CFG.CONTENT_CACHE);await c.delete(new URL('_blob/{id_}',location.href).href);
          await new Promise(r=>{{const q=indexedDB.open('insa-hoedok');q.onsuccess=()=>{{const t=q.result.transaction('blobs','readwrite');t.objectStore('blobs').delete('{id_}');t.oncomplete=r}}}})}})()""")
        await page.evaluate("localStorage.setItem('FAKE_OFF','1')")
        await page.reload(); await page.wait_for_timeout(5000)
        await page.evaluate(f"jumpTo({i},0)"); await page.wait_for_timeout(2000)
        print('other device, no drive',await st(page,i))
        await page.screenshot(path='/home/claude/test/img_nodrive.png')
        await page.evaluate("localStorage.removeItem('FAKE_OFF')")
        await page.evaluate("syncImgs()"); await page.wait_for_timeout(2500)
        print('other device, after drive sync',await st(page,i))
        await page.reload(); await page.wait_for_timeout(5000); await page.evaluate(f"jumpTo({i},0)"); await page.wait_for_timeout(1500)
        print('after reload',await st(page,i))
        print('blanks kept',await page.evaluate("U.add.blanks.map(b=>b.id).join(',')"))
        print('errors',errs)
        await b.close()
asyncio.run(main())
