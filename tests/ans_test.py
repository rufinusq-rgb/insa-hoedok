import asyncio
from playwright.async_api import async_playwright
B='http://localhost:8765/insa-hoedok/'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        ctx=await b.new_context(viewport={'width':1400,'height':900}); page=await ctx.new_page()
        errs=[];page.on('pageerror',lambda e:errs.append(str(e)));page.on('dialog',lambda d:asyncio.ensure_future(d.accept()))
        await page.goto(B+'index.html#stay'); await page.wait_for_timeout(800)
        for z in ['test_r01.zip','교재_r03.zip','교재_r04.zip']:
            await page.set_input_files('#zipIn','/home/claude/test/'+z); await page.wait_for_timeout(7000)
        await page.goto(B+'app.html'); await page.wait_for_timeout(5000)
        print(await page.evaluate("D.heads.filter(h=>h.ans).map(h=>pageLabel(h.p)+' '+h.ans+' '+h.t.slice(0,25))"))
        i=await page.evaluate("D.pages.findIndex(p=>p.label==='179')")
        await page.evaluate(f"jumpTo({i},0.5)"); await page.wait_for_timeout(2500)
        await page.screenshot(path='/home/claude/test/ans.png'); print('errs',errs); await b.close()
asyncio.run(main())
