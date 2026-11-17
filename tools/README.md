# 교재 묶음 만드는 스크립트 (2편에서 쓴 것)

교재 PDF·이미지는 저장소에 올리지 않는다. 스크립트만 둔다. 경로(/home/claude/in, /home/claude/work)는 작업할 때 맞춰 고친다.

순서: extract_hl.py(목차 형광펜 사각형 꺼내기) → build.py --img(쪽 그림·OCR 줄·글자 경계·목차) → blanks.py(쪽지시험 답 키워드 위치) → finish.py(rNN.json 완성, 쪽지시험 해설 그림) → zip.

주의: 플렉슬에서 한 글자만 톡 찍은 형광펜(두문자 표시 등)은 길이 0인 선이라 렌더러가 그리지 않는다. build.py가 아주 짧은 선으로 바꿔서 그린다. 새 편을 만들 때 이 부분을 빼지 말 것.

## 3편부터: tools/round (공통) + tools/rNN/finish.py (편별 설정)
1. `python3 tools/round/build.py <편 PDF> rNN <첫 쪽 번호> "제N편 제목" --img` → /home/claude/work/rNN/pkg 에 쪽 그림·rNN_words.json·stage1.json
2. `python3 tools/rNN/finish.py` → rNN.json(목차 다듬기·두 줄 제목 r2·빈칸·답 범위·쪽지·학자) + 해설 그림
3. `cd /home/claude/work/rNN/pkg && zip -qr -0 ../교재_rNN.zip data pages quiz`
- 쪽지 문항의 답이 다른 편 쪽에 있으면 빈칸·답 범위에 qr:'r03' 처럼 문항이 속한 편을 적는다(4회차 4~7번 → 4편 쪽).
- quiz.part 를 적으면 문항 이름이 「4회차 6번」처럼 나온다(없으면 「제2편 1번」).
- 5편(r05): 받은 PDF 끝 4쪽(263~266쪽)이 제6편 표지·기출·고득점 앞부분이라 그대로 넣고, finish.py 끝에서 제6편 편 제목(lv0)·기출(lv1)을 덧붙인다. 6편 묶음(267쪽~)을 만들 때 편 제목이 두 번 나오지 않게 볼 것.
