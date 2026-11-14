import asyncio
from playwright.async_api import async_playwright
B='http://localhost:8765/insa-hoedok/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        ctx = await b.new_context(viewport={'width':1100,'height':800}); page = await ctx.new_page()
        page.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
        await page.goto(B+'index.html#stay'); await page.wait_for_timeout(800)
        await page.set_input_files('#zipIn','/home/claude/test/test_r01.zip')
        await page.wait_for_selector('.pb button', timeout=60000); await page.click('.pb button'); await page.wait_for_timeout(500)
        await page.goto(B+'app.html'); await page.wait_for_timeout(4000)
        st = lambda: page.evaluate("document.querySelector('#viewer').scrollTop")
        await page.evaluate("setMK('dm')"); await page.wait_for_timeout(1500)
        await page.evaluate("document.querySelector('#pg12').scrollIntoView()"); await page.wait_for_timeout(800)
        pt=await page.evaluate("(()=>{const w=wordsOf(12).find(w=>w[1]>0.15&&w[1]<0.5);const r=PG[12].box.getBoundingClientRect();return [r.left+(w[0]+w[2]*0.2)*r.width, r.top+(w[1]+w[3]/2)*r.height]})()")
        await page.mouse.click(pt[0],pt[1]); await page.wait_for_timeout(800)   # 마우스(=펜과 같은 경로) 톡
        print('letters after mouse tap:', await page.evaluate("DMB.t.length"))
        s0=await st(); await page.mouse.move(550,600); await page.mouse.down()
        for k in range(1,13): await page.mouse.move(550,600-25*k); await asyncio.sleep(0.02)
        await page.mouse.up(); await page.wait_for_timeout(600)
        print('mouse drag scroll', s0,'->',await st(), 'letters', await page.evaluate("DMB.t.length"))
        await b.close()
asyncio.run(main())
