# 새 편 묶음을 만들 때 공통으로 쓰는 함수 (3편·4편에서 정리)
import fitz, re, json, os
from PIL import Image
W, H = 595.0, 841.0
r4 = lambda v: round(v, 4)

class Book:
    def __init__(self, path):
        self.d = fitz.open(path); self.PC = {}
    def chars(self, i):
        if i in self.PC: return self.PC[i]
        rd = self.d[i].get_text('rawdict'); L = []
        for b in rd['blocks']:
            if b['type'] != 0: continue
            for l in b['lines']:
                cs = [c for s in l['spans'] for c in s['chars'] if c['c'].strip()]
                if cs: L.append((l['bbox'], cs))
        L.sort(key=lambda x: ((x[0][1]+x[0][3])/2, x[0][0]))
        out = []
        for li, (bb, cs) in enumerate(L):
            for c in cs: out.append((c['c'], c['bbox'], li, bb))
        self.PC[i] = out; return out
    def find(self, i, phrase, after=None, nth=0):
        """쪽 i에서 phrase(띄어쓰기 무시)의 글자 상자들을 줄별 사각형(쪽 비율)으로"""
        cs = self.chars(i); s = ''.join(c[0] for c in cs); ph = re.sub(r'\s+', '', phrase)
        start = 0
        if after:
            start = s.find(re.sub(r'\s+', '', after))
            if start < 0: raise Exception(f'after not found p{i}: {after}')
        k = start - 1
        for _ in range(nth+1):
            k = s.find(ph, k+1)
            if k < 0: raise Exception(f'not found p{i}: {phrase} | near: ' + s[start:start+160])
        seg = cs[k:k+len(ph)]; rects = []
        for li in sorted(set(c[2] for c in seg)):
            g = [c for c in seg if c[2] == li]; bb = g[0][3]
            x0 = min(c[1][0] for c in g); x1 = max(c[1][2] for c in g)
            lh = (bb[3]-bb[1])/H; hh = max(0.0128, lh)
            rects.append([r4(x0/W), r4(bb[1]/H-(hh-lh)/2), r4((x1-x0)/W), r4(hh)])
        return rects
    def lineTop(self, i, phrase, after=None):
        return self.find(i, phrase, after)[0][1]
    def lineBottom(self, i, phrase, after=None):
        r = self.find(i, phrase, after)[-1]; return r4(r[1]+r[3])

def clean_heads(heads, fixes=None):
    """목차 글자 다듬기: 로마 숫자 다시 매김, 띄어쓰기, 두 줄 제목 합치기"""
    ROM = ['Ⅰ','Ⅱ','Ⅲ','Ⅳ','Ⅴ','Ⅵ','Ⅶ','Ⅷ','Ⅸ','Ⅹ']
    n = 0
    for h in heads:
        t = h['t']
        m = re.match(r'^([IVⅠ-Ⅹ]+)\s*\.\s*(.*)$', t)
        if m and h['lv'] >= 3:
            if re.match(r'^(I|Ⅰ)$', m.group(1)): n = 1
            else: n += 1
            t = ROM[n-1] + '. ' + m.group(2)
        t = re.sub(r'^(\(\d\)|\d\)|\d\.)(\S)', r'\1 \2', t)
        t = re.sub(r'^(\(\d\)|\d\)|\d\.|[①-⑳])\s*([가-힣])\s+([가-힣])$', r'\1 \2\3', t)
        t = re.sub(r'\s+:', ' :', t); t = re.sub(r'(\S):(\S)', r'\1: \2', t)
        h['t'] = t
    for (p, old, new) in (fixes or []):
        hit = [h for h in heads if h['p'] == p and h['t'].startswith(old)]
        assert len(hit) == 1, (p, old, len(hit)); hit[0]['t'] = new
    # 두 줄 제목: 같은 쪽·같은 단계에서 바로 아랫줄이 번호 없이 이어지면 앞 제목에 붙이고 띠는 r2로 남긴다
    out = []
    num = re.compile(r'^([IVⅠ-Ⅹ]+\.|\(\d+\)|\d+\)|\d+\.|[①-⑳]|제\s*\d)')
    for h in heads:
        pv = out[-1] if out else None
        if pv and h['lv'] >= 3 and pv['p'] == h['p'] and pv['lv'] == h['lv'] and not num.match(h['t']) \
           and 0 < h['y'] - pv['y'] < 0.035:
            pv['t'] = pv['t'] + ' ' + h['t']
            pv.setdefault('r2', []).append([h['x'], h['y'], h['w'], h['h']])
            continue
        out.append(h)
    for k, h in enumerate(out): h['id'] = 'h%03d' % k
    return out

def quiz_images(src, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    d = fitz.open(src)
    for i, p in enumerate(d):
        pm = p.get_pixmap(matrix=fitz.Matrix(1500/595, 1500/595), alpha=False)
        Image.frombytes('RGB', (pm.width, pm.height), pm.samples).save(f'{out_dir}/h{i+1}.jpg', quality=82, optimize=True)

def quiz_lines(src):
    """해설 PDF에서 문항 시작 줄 y(쪽 비율) 찾기용"""
    d = fitz.open(src); out = []
    for i, p in enumerate(d):
        ph = p.rect.height
        for b in p.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                t = ''.join(s['text'] for s in l['spans']).strip()
                if t: out.append((i+1, r4(l['bbox'][1]/ph), r4(l['bbox'][3]/ph), t))
    return out
