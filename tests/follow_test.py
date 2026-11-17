import asyncio,sys
from playwright.async_api import async_playwright
B='http://localhost:8765/insa-hoedok/'
INFO="""(()=>{const T=$('#tree');const r=T.querySelector('.node.on');const tr=T.getBoundingClientRect();return {cur:CUR&&CUR.t.slice(0,20),on:r?Math.round(r.getBoundingClientRect().top-tr.top):null,h:Math.round(tr.height),p4:[...T.querySelectorAll('.node[data-lv="0"]')].map(x=>Math.round(x.getBoundingClientRect().top-tr.top))}})()"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        ctx=await b.new_context(viewport={'width':1400,'height':900}); page=await ctx.new_page()
        errs=[];page.on('pageerror',lambda e:errs.append(str(e)));page.on('dialog',lambda d:asyncio.ensure_future(d.accept()))
        await page.goto(B+'index.html#stay'); await page.wait_for_timeout(800)
        for z in ['test_r01.zip','교재_r03.zip','교재_r04.zip']:
            await page.set_input_files('#zipIn','/home/claude/test/'+z); await page.wait_for_timeout(7000)
        await page.goto(B+'app.html'); await page.wait_for_timeout(5000)
        print('v',await page.evaluate("caches.keys()"))
        for n in ['4','3']:
            await page.click(f'.pjump button:text-is("{n}")'); await page.wait_for_timeout(2500); print('chip',n,await page.evaluate(INFO))
        await page.evaluate("$('#goPage').value='160';$('#goForm').requestSubmit()"); await page.wait_for_timeout(2000); print('go 160',await page.evaluate(INFO))
        await page.evaluate("$('#goPage').value='109';$('#goForm').requestSubmit()"); await page.wait_for_timeout(2000); print('go 109',await page.evaluate(INFO))
        for k in range(4):
            await page.evaluate("$('#viewer').scrollBy(0,3000)"); await page.wait_for_timeout(1200); print('scroll',await page.evaluate(INFO))
        print('errs',errs); await b.close()
asyncio.run(main())
