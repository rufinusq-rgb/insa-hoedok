import asyncio,json,re
from playwright.async_api import async_playwright
B='http://localhost:8765/insa-hoedok/'
MEMO="JSON.stringify(D.pages.map((p,i)=>[pageLabel(i),((NOTES['p'+sk(i)]||{}).memos||[]).map(m=>m.t).join('|'),((NOTES['p'+sk(i)]||{}).strokes||[]).length]).filter(x=>x[1]||x[2]))"
BL="JSON.stringify(items('blanks').filter(b=>b.mine||b.core).map(b=>[b.id,pageLabel(b.p)]))"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        ctx = await b.new_context(viewport={'width':1400,'height':1000}); page = await ctx.new_page()
        errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
        page.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
        async def core(route):
            r=await route.fetch(); t=await r.text()
            t=t.replace("{key:'r02', title:'제2편', file:'교재_r02.zip'}","{key:'r11', title:'제11편', file:'교재_r11.zip'},\n    {key:'r02', title:'제2편', file:'교재_r02.zip'},\n    {key:'r03', title:'제3편', file:'교재_r03.zip'}")
            await route.fulfill(response=r,body=t)
        await ctx.route('**/js/core.js',core)
        async def put(z,rec=False):
            await page.goto(B+'index.html#stay'); await page.wait_for_timeout(800)
            await page.set_input_files('#zipIn',z)
            if rec: await page.wait_for_selector('.pb button',timeout=60000); await page.click('.pb button'); await page.wait_for_timeout(800)
            else: await page.wait_for_timeout(6000)
        async def app():
            await page.goto(B+'app.html'); await page.wait_for_timeout(5000)
            return dict(order=await page.evaluate("D.rounds.map(r=>r.key+'@'+r.start).join(' ')"),memo=await page.evaluate(MEMO),bl=await page.evaluate(BL),img=await page.evaluate("JSON.stringify([5,52].map(i=>pageLabel(i)+':'+pageSrc(i)))"))
        # 1. 지금 사용자 상태: 1편+2편, 2편 메모는 옛 번호(p57,p79)
        await put('/home/claude/test/test_mig.zip',True); await put('/home/claude/test/교재_r02.zip')
        s1=await app(); print('1',s1)
        print('  keys',await page.evaluate("Object.keys(NOTES).sort().join(',')"),'| old kept:',await page.evaluate("JSON.stringify([NOTES.p57.memos.length,NOTES.p57.mv,NOTES.p79.memos.length])"))
        await page.wait_for_timeout(1500)
        # 2. 2편 62쪽 메모를 지우고 새로고침 → 다시 살아나지 않아야 함. 84쪽 것은 그대로
        await page.evaluate("(()=>{const i=57;note(i).memos=[];note(i).strokes=[];saveNote(i)})()"); await page.wait_for_timeout(1500)
        s2=await app(); print('2 after delete+reload',s2['memo'])
        # 새 메모를 2편 70쪽에
        await page.evaluate("(()=>{const i=D.pages.findIndex((p,k)=>pageLabel(k)==='70쪽');note(i).memos.push({id:'n70',x:.3,y:.3,w:.26,h:.09,t:'2편70쪽새메모',f:false});saveNote(i)})()"); await page.wait_for_timeout(1500)
        # 3. 11편을 먼저 넣음 (목록에서는 2편보다 앞에 적혀 있음)
        await put('/home/claude/test/test_r11.zip'); s3=await app(); print('3 +r11',s3['order'],s3['memo'])
        await page.evaluate("(()=>{const i=D.pages.findIndex((p,k)=>pageLabel(k)==='650쪽');note(i).memos.push({id:'n650',x:.3,y:.3,w:.26,h:.09,t:'11편650쪽메모',f:false});saveNote(i);setMode('blank')})()")
        await page.evaluate("(()=>{const i=D.pages.findIndex((p,k)=>pageLabel(k)==='650쪽');const rr=roundOf(i);U.add.blanks.push({id:'m-r11',q:'me',mine:1,p:i,rk:rr.key,lp:i-rr.start,r:[[.3,.5,.08,.0128]],k:[[.3,.5,.08,.0128]],chk:false,note:'',t:3});saveU()})()"); await page.wait_for_timeout(1500)
        # 4. 나중에 3편을 넣음 → 2편과 11편 사이로
        await put('/home/claude/test/test_r03.zip'); s4=await app(); print('4 +r03',s4['order']); print('  memo',s4['memo']); print('  blanks',s4['bl']); print('  img',s4['img'])
        print('  toc 편 순서',await page.evaluate("D.heads.filter(h=>h.lv===0).map(h=>h.t+'@'+pageLabel(h.p))"))
        print('  2편 문항',await page.evaluate("D.quiz.items.filter(i=>i.part==='제2편').map(i=>i.q+'/'+i.key)"),'빈칸 수',await page.evaluate("D.blanks.filter(b=>b.q===2001).length"),'qres',await page.evaluate("JSON.stringify(U.qres)"))
        # 5. 2편 묶음이 사라져도 나머지는 열리고 기록은 남음
        await page.evaluate("(async()=>{const c=await caches.open('insa-content-v1');for(const k of await c.keys())if(k.url.includes('r02'))await c.delete(k)})()")
        s5=await app(); print('5 r02 없음',s5['order'],s5['memo']); print('  stored',await page.evaluate("U.add.blanks.length"),'notes keys',await page.evaluate("Object.keys(NOTES).sort().join(',')"))
        print('errors',errs); await b.close()
asyncio.run(main())
