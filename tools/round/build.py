import fitz,re,json,io,os,sys
from PIL import Image
SRC=sys.argv[1]; RK=sys.argv[2]; FIRST=int(sys.argv[3]); TITLE=sys.argv[4]; OUT=f'/home/claude/work/{RK}/pkg'; WD=f'/home/claude/work/{RK}'
os.makedirs(WD,exist_ok=True)
os.makedirs(f'{OUT}/data',exist_ok=True); os.makedirs(f'{OUT}/pages/{RK}',exist_ok=True)
d=fitz.open(SRC); W,H=595.0,841.0
r4=lambda v:round(v,4)
hl=[]
for _i,_p in enumerate(d):
    for _x in _p.get_contents():
        _s=d.xref_stream(_x)
        if b'GSHLmul' not in _s: continue
        col=None; st=[]
        for t in _s.decode('latin1').split():
            if t=='rg': col=tuple(round(float(v),3) for v in st[-3:]); st=[]
            elif t=='re': x0,y0,w,h=[float(v) for v in st[-4:]]; hl.append([_i,col,x0,y0,w,h]); st=[]
            else: st.append(t)
COL={(0.31,0.69,0.423):3,(0.765,0.914,0.651):4,(0.577,0.828,0.353):5,(0.122,0.616,0.333):6}
pages=[];search=[];words={};heads=[]
linesBy={}
for i,p in enumerate(d):
    rd=p.get_text('rawdict')
    L=[];Wd=[]
    for bi,b in enumerate(rd['blocks']):
        if b['type']!=0: continue
        for li,l in enumerate(b['lines']):
            chars=[c for s in l['spans'] for c in s['chars']]
            if not any(c['c'].strip() for c in chars): continue
            x0=min(c['bbox'][0] for c in chars if c['c'].strip());x1=max(c['bbox'][2] for c in chars if c['c'].strip())
            y0=l['bbox'][1];y1=l['bbox'][3]
            txt=''.join(c['c'] for c in chars)
            L.append(dict(x=x0,y=y0,w=x1-x0,h=y1-y0,t=txt,chars=chars,id=f'{bi}-{li}'))
            cur=[]
            def flush():
                if cur:
                    bs=[cur[0]['bbox'][0]]+[c['bbox'][2] for c in cur]
                    Wd.append([r4(bs[0]/W),r4(y0/H),r4((bs[-1]-bs[0])/W),r4((y1-y0)/H),f'{bi}-{li}',[r4(v/W) for v in bs]])
            for c in chars:
                if c['c'].strip(): cur.append(c)
                else: flush(); cur=[]
            flush()
    L.sort(key=lambda l:(l['y']+l['h']/2,l['x']))
    linesBy[i]=L
    for l in L: search.append([i,r4(l['x']/W),r4(l['y']/H),r4(l['w']/W),r4(l['h']/H),re.sub(r'\s+','',l['t'])])
    words[str(i)]=Wd
    body=[l['x']/W for l in L if 0.1<l['y']/H<0.92 and len(l['t'].strip())>=4]
    tl=min(body) if body else 0.121
    pages.append(dict(i=i,label=str(FIRST+i),w=W,h=H,tl=r4(min(max(tl,0.09),0.25))))
# heads
def textIn(i,x0,y0,x1,y1):
    out=[]
    for l in linesBy[i]:
        cy=l['y']+l['h']/2
        if y0-2<=cy<=y1+2:
            s=''.join(c['c'] for c in l['chars'] if x0-3<=(c['bbox'][0]+c['bbox'][2])/2<=x1+3)
            if s.strip(): out.append((l['x'],s.strip(),l))
    out.sort(key=lambda o:o[0])
    return ' '.join(o[1] for o in out), [o[2] for o in out]
raw=[]
for i,col,x,yb,w,h in hl:
    lv=COL[min(COL,key=lambda c:sum(abs(a-b) for a,b in zip(c,col)))]
    y0=H-yb-h; y1=H-yb   # top-based
    if lv==5: y0=y1-h/0.6
    if lv==6:
        # underline: find line just above
        cand=[l for l in linesBy[i] if l['x']<x+w and l['x']+l['w']>x and -3<=y0-(l['y']+l['h'])<=8]
        if cand:
            l=min(cand,key=lambda l:abs(y0-(l['y']+l['h']))); y0=l['y']-1; y1=l['y']+l['h']+1
        else: y0=y0-12
    t,ls=textIn(i,x,y0,x+w,y1)
    raw.append(dict(p=i,lv=lv,t=re.sub(r'\s+',' ',t),x=r4(x/W),y=r4(y0/H),w=r4(w/W),h=r4((y1-y0)/H)))
# 장 제목
for i in range(2,len(d)):
    for l in linesBy[i]:
        t=l['t'].strip()
        if re.match(r'^제\s*\d\s*장',t) and l['h']>9 and l['y']/H>0.08:
            raw.append(dict(p=i,lv=2,t=re.sub(r'\s+',' ',t),x=r4(l['x']/W),y=r4(l['y']/H),w=r4(l['w']/W),h=r4(l['h']/H)))
raw.sort(key=lambda h:(h['p'],h['y']))
heads=[dict(p=0,lv=0,t=TITLE,x=0,y=0,w=0,h=0),dict(p=2,lv=1,t=TITLE.split()[0]+' 기출문제',x=0,y=0,w=0,h=0)]+raw
for k,h in enumerate(heads): h['id']='h%03d'%k
json.dump(dict(pages=pages,heads=heads,search=search),open(f'{WD}/stage1.json','w'),ensure_ascii=False)
json.dump(words,open(f'{OUT}/data/{RK}_words.json','w'),separators=(',',':'))
lab={p['i']:p['label'] for p in pages}
for h in heads: print(lab[h['p']],h['lv'],'  '*max(0,h['lv']-2)+h['t'], '' if h['lv']<2 else (h['x'],h['y'],h['w'],h['h']))
print(len(search),sum(len(v) for v in words.values()),[ (p['label'],p['tl']) for p in pages])
if '--img' in sys.argv:
    # 한 글자만 톡 찍은 형광펜(길이 0인 선)은 렌더러가 그리지 않는다 → 아주 짧은 선으로 바꿔 네모가 찍히게 한다
    ZL=re.compile(rb'([\d.\-]+) ([\d.\-]+) m\s+\1 \2 l\s+S'); nz=0; done=set()
    for i,p in enumerate(d):
        for x in p.get_xobjects():
            if not x[1].startswith('FXX') or x[0] in done: continue
            done.add(x[0]); st=d.xref_stream(x[0])
            def fix(m):
                global nz; nz+=1; X=float(m.group(1)); Y=m.group(2)
                return b'%.4f %s m %.4f %s l S'%(X-0.05,Y,X+0.05,Y)
            st2=ZL.sub(fix,st)
            if st2!=st: d.update_stream(x[0],st2)
    print('zero-length strokes fixed',nz)
    for i,p in enumerate(d):
        for x in p.get_contents():
            if b'GSHLmul' in d.xref_stream(x): d.update_stream(x,b' ')
        pm=p.get_pixmap(matrix=fitz.Matrix(1309/W,1851/H),alpha=False)
        im=Image.frombytes('RGB',(pm.width,pm.height),pm.samples).resize((1309,1851))
        im.save(f'{OUT}/pages/{RK}/p{i:02d}.jpg',quality=72,optimize=True)
    print('images done')
