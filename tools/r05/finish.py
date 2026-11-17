# 5편(r05) 묶음 완성. 먼저 ../round/build.py <5편 PDF> r05 187 "제5편 확보관리" --img
# 받은 5편 PDF 끝 4쪽(263~266쪽)은 제6편 표지·기출·고득점 답안포인트 앞부분이다. 쪽 순서를 지키려고 그대로 넣고
# 제6편 편 제목(lv0)을 263쪽에 따로 둔다(두문자 묶음이 제6편으로 잡히게).
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'round'))
from finish import finish

A = lambda y, h, img='h1.jpg': [dict(img=img, r=[0.05, y, 0.91, h])]
C = dict(
  rk='r05', first=187, book='/home/claude/in/b5.pdf', quizpdf='/home/claude/in/q6.pdf',
  title='6회차', range='제5편 (187 ~ 266쪽)', exam='6회차 쪽지시험 (제5편 + 이슈 국제)',
  headfix=[(252 - 187, '|준거관련', '② 준거관련 타당성(Criterion-related Validity)'),
           (221 - 187, '(3) 바람직한', '(3) 바람직한 인력관리 방안 - Lepak & Snell의 HR architecture(인력 구성형태별 다차원적')],
  # 6번(PCN·HCN·TCN)은 11편이라 해설만.
  quiz=dict(title='쪽지시험 (제5편 · 이슈 국제)', part='6회차', range='제5편 확보관리 + 이슈(국제)', items=[
    dict(q=1, type='서술', ask=A(0.112, 0.026), ans=A(0.140, 0.335)),
    dict(q=2, type='서술', ask=A(0.472, 0.026), ans=A(0.510, 0.058)),
    dict(q=3, type='서술', ask=A(0.592, 0.055), ans=A(0.660, 0.195)),
    dict(q=4, type='서술', ask=A(0.858, 0.055), ans=A(0.928, 0.028) + A(0.040, 0.172, 'h2.jpg')),
    dict(q=5, type='서술', ask=A(0.244, 0.226, 'h2.jpg'), ans=A(0.494, 0.134, 'h2.jpg')),
    dict(q=6, type='서술', ask=A(0.653, 0.026, 'h2.jpg'), ans=A(0.694, 0.195, 'h2.jpg')),
  ]),
  blanks=[
    # 1 인적자원계획의 흐름
    (1, 195, '환경분석 단계'), (1, 195, '인적자원 수요예측 단계'), (1, 195, '인적자원 공급예측 단계'), (1, 195, '인적자원 수급불균형 조정 단계'),
    # 2 공급예측 개념
    (2, 204, '미래의 t시점', {'after': '1.인적자원공급예측의의'}), (2, 204, '내부에서 보유하게 될 인력의 양과 질'), (2, 204, '외부노동시장의 여건', {'after': '1.인적자원공급예측의의'}),
    # 3 수요>공급 / 공급>수요
    (3, 207, '인력부족 대응 전략'), (3, 207, '신규인력 채용', {'after': '1.인력수요가'}),
    (3, 208, '초과근로(overtime)의 활용'), (3, 208, '임시직 고용', {'after': '1)초과근로'}), (3, 208, '파견근로 활용'), (3, 208, '아웃소싱(outsourcing)', {'after': '3)파견근로'}),
    (3, 208, '인력과잉 대응 전략'), (3, 208, '정리해고와 다운사이징'),
    (3, 209, '직무분할제(job sharing)', {'after': '(2)대체안'}), (3, 209, '조기퇴직제도(early retirement program)', {'after': '1)직무분할제'}),
    (3, 210, '교육훈련 및 연수기회 부여'), (3, 210, '신규채용 억제'), (3, 210, '자연 감원', {'after': '4)신규채용'}),
    # 4 사내공모제도 · 사원추천 모집제도
    (4, 215, '내부 노동시장', {'after': '①사내공모제도'}), (4, 215, '평가의 정확성 확보(reference', {'after': '②사내공모제도의장점'}),
    (4, 219, '현직 종업원(기존직원)들이 적임자를 추천', {'after': '1.사원추천모집제도'}), (4, 219, '모집원천의 신뢰성', {'after': '1.사원추천모집제도'}),
    # 5 칸테라 — 자원기반관점(VRIN), 내부육성(make)
    (5, 191, 'VRIN'), (5, 191, '자체적으로 개발'), (5, 191, '핵심역량은 내부적'),
    (5, 210, '육성(make전략)'),
  ],
  spans=[
    (1, 195, 'Ⅲ.인적자원계획의Flow', '정방안을마련하는과정으로이루어지게된다'),
    (2, 204, '1.인적자원공급예측의의', '고려한계획활동을의미한다'),
    (3, 207, 'VII.인적자원수요와공급의균형', '대체안을찾게된다'),
    (3, 208, '(2)대체안(alternatives)', '(1)정리해고와다운사이징'),
    (3, 209, '(2)대체안(alternatives)', '2)조기퇴직제도(earlyretirementprogram)'),
    (3, 210, '3)교육훈련및연수기회부여', '여러상황을고려하여활용하여야한다'),
    (4, 215, '①사내공모제도', 'check)'),
    (4, 219, '1.사원추천모집제도', '높이는데기여한다'),
    (5, 191, 'Barney는지속적인', '사한다.'),
    (5, 210, '2.기업의전략에따른', '적절한운용이중요하다'),
  ],
  scholars=[
    dict(g='인력확보 관련 이론', s='제1장 고득점 답안포인트 · 인턴제도 예시문제', items=[
      dict(n='O. E. Williamson', k='윌리엄슨', t='거래비용이론(TCT) – 내부거래가 시장거래보다 비용이 적으면 조직을 만든다, 내부조달·외부조달(make or buy)', p=[190, 217]),
      dict(n='Pfeffer', k='페퍼 (Pfeffer & Salancik)', t='자원의존이론(RDT) – 조직은 외부 의존도를 줄이고 자율성을 지키려 환경에 영향력을 행사', p=[190]),
      dict(n='J. Barney', k='바니', t='자원기반관점(RBV) – VRIN/VRIO, 핵심역량은 내부 개발·나머지는 아웃소싱', p=[191])]),
    dict(g='모집', s='제2장 사원추천 예시문제', items=[
      dict(n='Lepak & Snell', k='레팩 & 스넬', t='HR architecture – 인적자원의 가치·고유성에 따른 4가지 고용형태(내부개발·외부획득·계약·제휴)', p=[221])]),
    dict(g='입직관리', s='제4장 인사배치 및 입직관리', items=[
      dict(n='Bauer', k='바우어 (탈리아 바우어)', t='4C 모형(2010) – Compliance · Clarification · Culture · Connection', p=[258, 259])]),
    dict(g='개발관리 관련 이론', s='제6편 고득점 답안포인트 (앞부분)', items=[
      dict(n='O. E. Williamson', k='윌리엄슨', t='거래비용이론(TCT) – make or buy', p=[266]),
      dict(n='Schultz & Becker', k='슐츠 & 베커', t='인적자본이론(HCT) – 일반 기술은 종업원이, 기업 특유 기술은 기업이 투자', p=[266])]),
  ],
)
R = finish(C)

# 제6편 앞부분(263~266쪽) 편 제목. id는 끝에 붙여 기존 목차 id가 밀리지 않게 한다.
OUT = '/home/claude/work/r05/pkg/data/r05.json'
R['heads'].append(dict(p=263 - 187, lv=0, t='제6편 개발관리', x=0, y=0, w=0, h=0, id='h%03d' % len(R['heads'])))
R['heads'].append(dict(p=265 - 187, lv=1, t='제6편 기출문제', x=0, y=0, w=0, h=0, id='h%03d' % len(R['heads'])))
R['heads'].sort(key=lambda h: (h['p'], h['lv'] > 1, h['y']))
json.dump(R, open(OUT, 'w'), ensure_ascii=False, separators=(',', ':'))
print('heads', len(R['heads']))
