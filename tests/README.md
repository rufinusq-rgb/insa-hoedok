# 시험 스크립트 (교재 데이터는 저장소에 없음)

- 필요: playwright(python), /usr/bin/google-chrome, `python3 -m http.server 8765 --bind 127.0.0.1` 을 /home/claude 에서 실행 (저장소는 /home/claude/insa-hoedok).
- 시험용 묶음 /home/claude/test/test_r01.zip 이 있어야 함: data/r01.json, data/r01_words.json(아티팩트 2b25e2df… 의 파일에서 가져옴), pages/r01/pNN.jpg(빈 그림이어도 됨), backup.json({app,v,round,saved,user,notes}).
- 교재 이미지·기록은 저작권·개인정보라 이 공개 저장소에 올리지 않는다.
- full_test.py: 숨긴 기능, 두문자 만들기·탭·글자/줄/주제 고치기·퀴즈, 메모, 틀린 빈칸 단원, 새로고침 뒤 내 빈칸 보존.
- pen_scroll_test.py: 두문자 만들기 중 펜 끌기 = 화면 넘김.
- dm_range_check.py: 두문자 설명 범위 규칙을 실제 OCR 줄에 돌려 보기.
- r02_test.py: 2편 추가 시험. /home/claude/test/교재_r02.zip(실제 2편 묶음)이 있어야 함. ① 2편이 목록에만 있고 기기에 없을 때 1편만 열림 ② 2편을 넣은 뒤 기록(U.add·ov·res·qres)과 내 빈칸 위치가 그대로 ③ 2편 묶음이 기기에서 사라져도 2편 빈칸 기록은 남고, 다시 넣으면 보임.
- mig_test.py: 책 순서 정렬과 저장 번호(sk) 시험. test_mig.zip(1편 + 옛 번호 p57·p79로 저장된 2편 메모), 교재_r02.zip, 가짜 test_r11.zip·test_r03.zip(2편 데이터의 쪽 번호만 바꾼 것)이 필요. 11편을 먼저 넣고 3편을 나중에 넣어도 메모·빈칸·이미지 교체가 제 쪽에 남는지 확인.
