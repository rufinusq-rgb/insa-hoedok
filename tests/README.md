# 시험 스크립트 (교재 데이터는 저장소에 없음)

- 필요: playwright(python), /usr/bin/google-chrome, `python3 -m http.server 8765 --bind 127.0.0.1` 을 /home/claude 에서 실행 (저장소는 /home/claude/insa-hoedok).
- 시험용 묶음 /home/claude/test/test_r01.zip 이 있어야 함: data/r01.json, data/r01_words.json(아티팩트 2b25e2df… 의 파일에서 가져옴), pages/r01/pNN.jpg(빈 그림이어도 됨), backup.json({app,v,round,saved,user,notes}).
- 교재 이미지·기록은 저작권·개인정보라 이 공개 저장소에 올리지 않는다.
- full_test.py: 숨긴 기능, 두문자 만들기·탭·글자/줄/주제 고치기·퀴즈, 메모, 틀린 빈칸 단원, 새로고침 뒤 내 빈칸 보존.
- pen_scroll_test.py: 두문자 만들기 중 펜 끌기 = 화면 넘김.
- dm_range_check.py: 두문자 설명 범위 규칙을 실제 OCR 줄에 돌려 보기.
