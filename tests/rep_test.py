import asyncio
from playwright.async_api import async_playwright
B='http://localhost:8765/insa-hoedok/'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox']);ctx=await b.new_context(viewport={'width':1400,'height':1000});page=await ctx.new_page()
        errs=[];page.on('pageerror',lambda e:errs.append(str(e)));page.on('dialog',lambda d:asyncio.ensure_future(d.accept()))
        await ctx.route('**/pdf.js/3.11.174/pdf.min.js',lambda r:r.fulfill(path='/home/claude/pdfjs/package/build/pdf.min.js',content_type='application/javascript'))
        await ctx.route('**/pdf.js/3.11.174/pdf.worker.min.js',lambda r:r.fulfill(path='/home/claude/pdfjs/package/build/pdf.worker.min.js',content_type='application/javascript'))
        for z in ['test_r01.zip','교재_r02.zip']:
            await page.goto(B+'index.html#stay');await page.wait_for_timeout(700);await page.set_input_files('#zipIn','/home/claude/test/'+z);await page.wait_for_timeout(5500)
        await page.goto(B+'app.html');await page.wait_for_timeout(5000)
        nb=await page.evaluate("items('blanks').filter(b=>b.mine||b.core).length")
        # 2편 PDF를 2편 첫 쪽(55쪽)부터 교체
        await page.evaluate("openReplace()");await page.wait_for_timeout(500)
        await page.select_option('#repStart',label=await page.evaluate("[...document.querySelectorAll('#repStart option')].find(o=>o.textContent.includes('(55쪽)')).textContent"))
        async with page.expect_file_chooser() as fc: await page.click('#sheet >> text=PDF 고르기')
        await (await fc.value).set_files('/home/claude/in/quiz_or_book.pdf')
        await page.wait_for_function("document.querySelector('#sheet').innerText.includes('끝났습니다')",timeout=180000)
        print(await page.evaluate("document.querySelector('#sheet').innerText.split('\\n').filter(l=>/넣습니다|끝났|건너|못했/.test(l))"))
        print('pageImg keys',await page.evaluate("Object.keys(U.pageImg).slice(0,4)+' … '+Object.keys(U.pageImg).length"),'pages',await page.evaluate("D.pages.length"),'blanks same',nb==await page.evaluate("items('blanks').filter(b=>b.mine||b.core).length"))
        await page.evaluate("$('#sheet').hidden=true;setSide(false);jumpTo(54,0.55)");await page.wait_for_timeout(2500)
        await page.screenshot(path='rep59.png')
        print(errs);await b.close()
asyncio.run(main())
