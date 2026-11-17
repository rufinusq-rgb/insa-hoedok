# rNN.json 완성: stage1(목차·쪽·OCR) + 빈칸 + 쪽지 + 학자. 사용: finish(cfg) — cfg는 tools/rNN/finish.py 참고
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import *

def finish(C):
    RK = C['rk']; WD = f'/home/claude/work/{RK}'; OUT = f'{WD}/pkg'
    S = json.load(open(f'{WD}/stage1.json'))
    heads = clean_heads(S['heads'], C.get('headfix'))
    B = Book(C['book']); L0 = C['first']; P = lambda lab: lab - L0
    bl = []; n = 0
    for spec in C['blanks']:
        q, lab, ph = spec[:3]; opt = spec[3] if len(spec) > 3 else {}
        if 'rect' in opt: rs = [opt['rect']]
        else: rs = B.find(P(lab), ph, opt.get('after'), opt.get('nth', 0))
        n += 1
        b = dict(id=f"b{int(RK[1:])}-{n:03d}", q=q, p=P(lab), r=rs, k=rs, chk=False, note='')
        if opt.get('qr'): b['qr'] = opt['qr']
        bl.append(b)
    qspans = []
    for sp in C['spans']:
        q, lab, a, z = sp[:4]; opt = sp[4] if len(sp) > 4 else {}
        y0 = B.lineTop(P(lab), a, opt.get('after')); y1 = B.lineBottom(P(lab), z, opt.get('after'))
        s = dict(q=q, p=P(lab), y=r4(y0 - 0.004), h=r4(y1 - y0 + 0.008))
        if opt.get('qr'): s['qr'] = opt['qr']
        qspans.append(s)
    sch = [dict(g=g['g'], s=g['s'], items=[dict(it, p=[P(x) for x in it['p']]) for it in g['items']]) for g in C['scholars']]
    R = dict(round=int(RK[1:]), title=C['title'], range=C['range'], exam=C['exam'], pages=S['pages'], heads=heads,
             blanks=bl, links=[], dumunja=[], search=S['search'], clues=[], maps={}, stats=[], caseMarks=[], proseMarks=[],
             quiz=C['quiz'], qspans=qspans, scholars=sch)
    json.dump(R, open(f'{OUT}/data/{RK}.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    if C.get('quizpdf'): quiz_images(C['quizpdf'], f'{OUT}/quiz/{RK}')
    for h in heads:
        if h['lv'] <= 3 or h.get('r2'): print(h['p'] + L0, h['lv'], h['t'], 'r2' if h.get('r2') else '')
    print('heads', len(heads), 'bands', sum(1 for h in heads if h['lv'] >= 3) + sum(len(h.get('r2', [])) for h in heads),
          'blanks', len(bl), 'spans', len(qspans), 'size', os.path.getsize(f'{OUT}/data/{RK}.json'))
    return R
