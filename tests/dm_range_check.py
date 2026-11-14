import asyncio
from playwright.async_api import async_playwright
B='http://localhost:8765/insa-hoedok/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        page = await (await b.new_context()).new_page()
        page.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
        await page.goto(B+'index.html#stay'); await page.wait_for_timeout(800)
        await page.set_input_files('#zipIn','/home/claude/test/test_r01.zip')
        await page.wait_for_selector('.pb button', timeout=60000); await page.click('.pb button'); await page.wait_for_timeout(500)
        await page.goto(B+'app.html'); await page.wait_for_timeout(4000)
        r=await page.evaluate("""(async()=>{await loadWords();const out=[];for(const p of [9,10]){const L=dmLines(p);
          L.forEach((l,j)=>{if(j%1)return;const t={p,r:[l.x0+.002,l.y0,.015,l.y1-l.y0]};const it=dmItems({t:[t]})[0];
          const inc=L.filter(m=>m.cy>=it.r[1]&&m.cy<=it.r[1]+it.r[3]).map(m=>m.t.slice(0,12));out.push(p+' '+(it.head?'H':it.auto)+' | '+l.t.slice(0,18)+' => '+inc.length)})}return out.join('\\n')})()""")
        print(r)
        await b.close()
asyncio.run(main())
