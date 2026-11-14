import json,re,fitz,os
from PIL import Image
OUT='/home/claude/work/pkg'; RK='r02'
S=json.load(open('stage1.json')); heads=S['heads']
ROM=['Ⅰ','Ⅱ','Ⅲ','Ⅳ','Ⅴ','Ⅵ','Ⅶ','Ⅷ']
CIRC='①②③④⑤⑥⑦⑧⑨⑩'
n=0
for h in heads:
    t=h['t']
    m=re.match(r'^([IVⅠ-Ⅹ]+)\s*\.\s*(.*)$',t)
    if h['lv']==3 and m:
        if re.match(r'^(I|Ⅰ)$',m.group(1)): n=1
        else: n+=1
        t=ROM[n-1]+'. '+m.group(2)
    t=re.sub(r'^\((\d)\)\s*표\s*(\S)번\s*-\s*',lambda m:'(%s) 표 %s번 - '%(m.group(1),CIRC[int(m.group(2))-1] if m.group(2) in '123456789' else m.group(2)),t)
    t=re.sub(r'^(\(\d\)|\d\.)\s*(개)\s+(요|념|발)$',r'\1 \2\3',t)
    t=re.sub(r'^(\(\d\))(\S)',r'\1 \2',t)
    t=re.sub(r'^(\(\d\)|\d\.)\s*([가-힣])\s+([가-힣])$',r'\1 \2\3',t)
    t=t.replace('개인주의 집단주의','개인주의-집단주의').replace('남성중심성 여성중심성','남성중심성-여성중심성').replace('성숙미성숙','성숙-미성숙')
    t=re.sub(r'\s+:',' :',t); t=re.sub(r'(\S):(\S)',r'\1: \2',t)
    h['t']=t
for k,h in enumerate(heads): h['id']='h%03d'%k
bl=json.load(open('blanks.json'))
qspans=[dict(q=1,p=7,y=0.468,h=0.436),dict(q=1,p=8,y=0.1146,h=0.492),dict(q=2,p=12,y=0.828,h=0.078),dict(q=2,p=13,y=0.1263,h=0.259)]
quiz=dict(title='3회차 쪽지시험',range='제2편 환경 + 이슈 제1장',items=[
 dict(q=1,type='서술',ask=[dict(img='h1.jpg',r=[0.05,0.107,0.91,0.067])],ans=[dict(img='h1.jpg',r=[0.05,0.180,0.91,0.326])]),
 dict(q=2,type='서술',ask=[dict(img='h1.jpg',r=[0.05,0.518,0.91,0.026])],ans=[dict(img='h1.jpg',r=[0.05,0.552,0.91,0.402])]),
 dict(q=3,type='서술',ask=[dict(img='h2.jpg',r=[0.05,0.046,0.91,0.026])],ans=[dict(img='h2.jpg',r=[0.05,0.081,0.91,0.502])]),
 dict(q=4,type='서술',ask=[dict(img='h2.jpg',r=[0.05,0.593,0.91,0.026])],ans=[dict(img='h2.jpg',r=[0.05,0.628,0.91,0.318])]),
])
scholars=[
 dict(g='사회문화적 환경',s='제2장 · 예시문제 답안',items=[
   dict(n='Hofstede',k='홉스테드',t='5가지 문화차원 – 권력의 거리 · 개인주의-집단주의 · 남성-여성성 · 불확실성의 회피 · 장기-단기 지향성',p=[7,8]),
   dict(n='Minkov',k='민코프 (마이클 민코프)',t='Hofstede와 함께 6번째 차원 추가 – 자적(indulgence)-자제(restraint)',p=[9])]),
 dict(g='최고경영자의 조직관리방식',s='제3장 · 22회 기출·예시문제 답안',items=[
   dict(n='McGregor',k='맥그리거',t='X론·Y론 – 인간전제에 따른 조직관리방식',p=[21,23,24]),
   dict(n='Argyris',k='아지리스',t='성숙-미성숙이론(1957)',p=[21,24])]),
]
R=dict(round=2,title='3회차',range='제2편 (55 ~ 84쪽)',exam='3회차 쪽지시험 (제2편 + 이슈 제1장)',pages=S['pages'],heads=heads,blanks=bl,links=[],dumunja=[],search=S['search'],clues=[],maps={},stats=[],caseMarks=[],proseMarks=[],quiz=quiz,qspans=qspans,scholars=scholars)
json.dump(R,open(f'{OUT}/data/{RK}.json','w'),ensure_ascii=False,separators=(',',':'))
os.makedirs(f'{OUT}/quiz/{RK}',exist_ok=True)
d=fitz.open('/home/claude/in/new.pdf')
for i,p in enumerate(d):
    pm=p.get_pixmap(matrix=fitz.Matrix(1500/595,1500/595),alpha=False)
    Image.frombytes('RGB',(pm.width,pm.height),pm.samples).save(f'{OUT}/quiz/{RK}/h{i+1}.jpg',quality=82,optimize=True)
for h in heads:
    if h['lv']<=3 or '표' in h['t'] or '개' in h['t'][:6]: print(h['p']+55,h['lv'],h['t'])
print(len(heads), os.path.getsize(f'{OUT}/data/{RK}.json'))
