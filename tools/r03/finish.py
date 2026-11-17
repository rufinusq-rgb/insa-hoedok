# 3편(r03) 묶음 완성. 먼저 ../round/build.py <3편 PDF> r03 85 "제3편 전략적 인적자원관리(SHRM)와 e-HRM" [--img]
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'round'))
from finish import finish

A = lambda y, h, img='h1.jpg': [dict(img=img, r=[0.05, y, 0.91, h])]
C = dict(
  rk='r03', first=85, book='/home/claude/in/b3.pdf', quizpdf='/home/claude/in/q4.pdf',
  title='4회차', range='제3편 (85 ~ 118쪽)', exam='4회차 쪽지시험 (제3편 + 제4편 + 이슈 윤리)',
  headfix=[],
  # 4회차 4~7번 답은 4편에 있다 → tools/r04/finish.py 에서 qr:'r03' 으로 넣는다. 8번(윤리)은 11편이라 해설만.
  quiz=dict(title='쪽지시험 (제3편 · 제4편 · 이슈 윤리)', part='4회차', range='제3편 전략 + 제4편 직무 + 이슈(윤리)', items=[
    dict(q=1, type='서술', ask=A(0.112, 0.027), ans=A(0.150, 0.166)),
    dict(q=2, type='서술', ask=A(0.330, 0.027), ans=A(0.368, 0.053)),
    dict(q=3, type='서술', ask=A(0.434, 0.027), ans=A(0.472, 0.053)),
    dict(q=4, type='단답', ask=A(0.538, 0.027), ans=A(0.577, 0.094)),
    dict(q=5, type='단답', ask=A(0.694, 0.027), ans=A(0.733, 0.054)),
    dict(q=6, type='나열', ask=A(0.800, 0.027), ans=A(0.839, 0.097) + A(0.080, 0.259, 'h2.jpg')),
    dict(q=7, type='서술', ask=A(0.362, 0.027, 'h2.jpg'), ans=A(0.401, 0.170, 'h2.jpg')),
    dict(q=8, type='서술', ask=A(0.584, 0.054, 'h2.jpg'), ans=A(0.650, 0.280, 'h2.jpg')),
  ]),
  blanks=[  # (문항, 교재 쪽, 답 글자, {after})
    (1, 90, '수직적 적합성'), (1, 90, '수평적 적합성'), (1, 90, '전략목적', {'after': '조화(수평적'}),
    (1, 92, '경쟁우위 추구', {'after': '(1)실행'}), (1, 93, '경영전략과의 통합', {'after': '(2)'}), (1, 94, '문화 간 시너지', {'after': '(3)SHRM'}),
    (2, 109, 'P-HRM', {'after': 'e-HRM이란'}), (2, 109, '쌍방향 커뮤니케이션', {'after': 'e-HRM이란'}),
    (2, 109, 'IT 기술', {'after': 'e-HRM이란'}), (2, 109, 'HR 정보와 서비스', {'after': 'e-HRM이란'}),
    (3, 115, '통계, 모델링, AI', {'after': '1.개념'}), (3, 115, '가공·해석', {'after': '1.개념'}), (3, 115, '의사결정을 지원', {'after': '1.개념'}),
  ],
  spans=[  # (문항, 교재 쪽, 시작 글자, 끝 글자)
    (1, 90, '1.전략적인적자원관리(Strategic', '다(Wright&McMahan,1992)'),
    (1, 92, '(1)실행주체로서', '(1)실행주체로서'), (1, 93, '(2)경영전략과의통합', '(2)경영전략과의통합'), (1, 94, '(3)SHRM과문화', '(3)SHRM과문화'),
    (2, 109, '1.e-HRM(electronic', '는체제를말한다'),
    (3, 115, '1.개념', '지원하는활동을말한다'),
  ],
  scholars=[
    dict(g='전략적 인적자원관리', s='제2장 SHRM', items=[
      dict(n='Wright & McMahan', k='라이트 & 맥마한', t='SHRM 정의(1992) – 수직적 적합성 · 수평적 적합성', p=[90]),
      dict(n='Huselid', k='휴슬리드', t='인적자본 투자 → 기업성과 실증연구(1995), 고성과작업관행(HPWP)', p=[92]),
      dict(n='Collins & Clark', k='콜린스 & 클라크', t='블랙박스 – 인적자본·사회적 자본·조직자본(2003)', p=[92]),
      dict(n='Chandler', k='챈들러', t='환경 → 전략 → 구조·과정 → 성과(1962)', p=[93]),
      dict(n='Ramanujam', k='라마누잠', t='수직적 적합성 – 행정적·일방적·쌍방적·통합적 연계', p=[93, 94]),
      dict(n='Ulrich', k='울리히', t='SPOT 현상 – 조직역량을 세우는 것이 HRM의 전략적 역할', p=[95])]),
    dict(g='전략의 유형', s='제3장 전략의 유형과 HRM', items=[
      dict(n='Porter', k='포터 (마이클 포터)', t='본원적 경쟁전략 – 저원가 · 차별화 · 집중화', p=[96, 97]),
      dict(n='Miles & Snow', k='마일즈 & 스노우', t='공격형 · 방어형 · 분석형 · 반응형', p=[98, 99, 100]),
      dict(n='Baron & Hannan', k='배런 & 하난', t='SPEC 모형 – 스타 · 엔지니어링 · 몰입 · 관료 · 전제형', p=[101, 102])]),
    dict(g='HR Analytics', s='제5장 참고 상자', items=[
      dict(n='Taylor', k='테일러', t='과학적 관리론 – 인사관리에 처음 과학적 접근', p=[115]),
      dict(n='Fitz-enz', k='피츠엔츠', t='인적자본 가치평가 · HR 벤치마킹 지표 체계화(1980년대)', p=[115])]),
  ],
)
finish(C)
