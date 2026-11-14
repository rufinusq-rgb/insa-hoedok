import fitz,re,json
d=fitz.open('/home/claude/in/quiz_or_book.pdf'); W,H=595.0,841.0
r4=lambda v:round(v,4)
def pagechars(i):
    rd=d[i].get_text('rawdict'); L=[]
    for b in rd['blocks']:
        if b['type']!=0: continue
        for l in b['lines']:
            cs=[c for s in l['spans'] for c in s['chars'] if c['c'].strip()]
            if cs: L.append((l['bbox'],cs))
    L.sort(key=lambda x:((x[0][1]+x[0][3])/2, x[0][0]))
    out=[]
    for li,(bb,cs) in enumerate(L):
        for c in cs: out.append((c['c'],c['bbox'],li,bb))
    return out
PC={}
def find(i,phrase,after=None,nth=0):
    if i not in PC: PC[i]=pagechars(i)
    cs=PC[i]; s=''.join(c[0] for c in cs); ph=re.sub(r'\s+','',phrase)
    start=0
    if after: start=s.index(re.sub(r'\s+','',after))
    k=start-1
    for _ in range(nth+1):
        k=s.find(ph,k+1)
        if k<0: raise Exception(f'not found p{i}: {phrase} | near: '+s[start:start+200])
    seg=cs[k:k+len(ph)]; rects=[]
    for li in sorted(set(c[2] for c in seg)):
        g=[c for c in seg if c[2]==li]; bb=g[0][3]
        x0=min(c[1][0] for c in g); x1=max(c[1][2] for c in g)
        lh=(bb[3]-bb[1])/H; hh=max(0.0128,lh)
        rects.append([r4(x0/W),r4(bb[1]/H-(hh-lh)/2),r4((x1-x0)/W),r4(hh)])
    return rects
SPEC=[ # q, page idx, phrase, after
 (1,7,'불균등','1)권력의거리'),(1,7,'수용하는','1)권력의거리'),(1,7,'차이를 받아들이는 정도','1)권력의거리'),
 (1,7,'개인의 이익과 집단의 이익','2)개인주의'),(1,7,'더 중요시','2)개인주의'),
 (1,7,'남성적 특성','3)남성'),(1,7,'여성적 특성','3)남성'),(1,7,'더 가치 있게','3)남성'),
 (1,8,'불확실한 상황이나 위험','4)불확실성'),(1,8,'불안을 느끼는 정도','4)불확실성'),
 (1,8,'현재의 즐거움을 유보','5)장기'),(1,8,'미래지향적 가치','5)장기'),(1,8,'과거나 현재','단기 지향성 문화권'),(1,8,'단기적인 성과','단기 지향성 문화권'),(1,8,'체면 유지','단기 지향성 문화권'),(1,8,'사회적 책무의 준수','단기 지향성 문화권'),
 (2,12,'작업자의 근무방식','3.4차산업혁명이'),(2,12,'플랫폼','3.4차산업혁명이'),(2,12,'임시직 고용관계(gig economy)','3.4차산업혁명이'),
 (2,13,'복잡한 문제해결 능력',None),(2,13,'비주얼 능력',None),
 (2,13,'교육훈련의 질적 변화',None),(2,13,'공통적이고 범용적인 능력',None),
 (2,13,'다수의 프로젝트',None),(2,13,'수시평가',None),
 (2,13,'개별적으로 보상',None),(2,13,'빅데이터와 인공지능',None),
]
bl=[]
for n,(q,p,ph,af) in enumerate(SPEC):
    try: rs=find(p,ph,af)
    except Exception as e: print('ERR',e); continue
    bl.append(dict(id='b2-%03d'%(n+1),q=q,p=p,r=rs,k=rs,chk=False,note=''))
    print(q,p,ph,rs)
json.dump(bl,open('blanks.json','w'))
# qspan helper: print lines
for i,a,b in [(7,'3.5가지문화차원',None),(8,None,'그림30'),(12,'3.4차산업혁명이',None),(13,None,'4.AI시대')]:
    cs=PC[i]; s=''.join(c[0] for c in cs)
    if a: k=s.index(a); print(i,'start y',r4(cs[k][3][1]/H))
    if b: k=s.index(b); print(i,'end before y',r4(cs[k][3][1]/H), 'prev line bottom', r4(max(c[3][3] for c in cs[:k] if c[3][3]<cs[k][3][1])/H))
    print(i,'first body y',r4(min(c[3][1] for c in cs if c[3][1]/H>0.1)/H),'last y',r4(max(c[3][3] for c in cs if c[3][3]/H<0.93)/H))
