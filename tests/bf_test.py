import asyncio,json
from playwright.async_api import async_playwright
B='http://localhost:8765/insa-hoedok/'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox']);page=await (await b.new_context()).new_page()
        errs=[];page.on('pageerror',lambda e:errs.append(str(e)));page.on('dialog',lambda d:asyncio.ensure_future(d.accept()))
        await page.goto(B+'index.html#stay');await page.wait_for_timeout(800)
        await page.set_input_files('#zipIn','/home/claude/test/test_r01.zip');await page.wait_for_timeout(5000)
        await page.set_input_files('#zipIn','/home/claude/test/교재_r02.zip');await page.wait_for_timeout(6000)
        # 드라이브 흉내: 1편은 이미 보관됨, 2편은 없음
        await page.evaluate("""()=>{const D=INSA.Drive;window.UP=[];window.FILES=[{id:'a',name:'교재_r01.zip'}];
          D.token=()=>'x';D.configured=()=>true;D.list=async()=>FILES.slice();
          D.saveBlob=async(name,blob)=>{const z=await JSZip.loadAsync(blob);UP.push([name,blob.size,Object.keys(z.files).filter(n=>!z.files[n].dir).length,Object.keys(z.files).filter(n=>/backup|users/.test(n)).length]);FILES.push({id:'b',name});return 'b'};}""")
        await page.evaluate("refreshAll()");await page.wait_for_timeout(1500)
        print('before',await page.evaluate("[...document.querySelectorAll('#ctRows .row')].map(r=>r.innerText.replace(/\\n/g,' '))"))
        await page.click("#ctRows button:has-text('드라이브에 보관')");await page.wait_for_timeout(6000)
        print('uploaded',await page.evaluate("JSON.stringify(UP)"))
        print('after',await page.evaluate("[...document.querySelectorAll('#ctRows .row')].map(r=>r.innerText.replace(/\\n/g,' '))"),'go disabled',await page.evaluate("document.querySelector('#go').disabled"))
        # 올린 묶음을 다시 넣어도 같은 내용인지
        print('errors',errs);await b.close()
asyncio.run(main())
