import fitz,re,json,sys
d=fitz.open('/home/claude/in/quiz_or_book.pdf')
out=[]
for i,p in enumerate(d):
    H=p.rect.height
    for x in p.get_contents():
        s=d.xref_stream(x)
        if b'GSHLmul' not in s: continue
        col=None
        toks=s.decode('latin1').split()
        st=[]
        for t in toks:
            if t=='rg': col=tuple(round(float(v),3) for v in st[-3:]); st=[]
            elif t=='re':
                x0,y0,w,h=[float(v) for v in st[-4:]]; out.append([i,col,x0,y0,w,h]); st=[]
            else: st.append(t)
json.dump(out,open('hl.json','w'))
from collections import Counter
print(Counter(o[1] for o in out))
print(out[:6])
s=[d.xref_stream(x) for x in d[5].get_contents() if b'GSHLmul' in d.xref_stream(x)][0]
print(s[:400])
print(d[5].rect, d[5].rotation, d[5].transformation_matrix)
