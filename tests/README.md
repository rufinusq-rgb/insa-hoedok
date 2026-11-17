# 시험 스크립트 (교재 데이터는 저장소에 없음)

- 필요: playwright(python), /usr/bin/google-chrome, `python3 -m http.server 8765 --bind 127.0.0.1` 을 /home/claude 에서 실행 (저장소는 /home/claude/insa-hoedok).
- 시험용 묶음 /home/claude/test/test_r01.zip 이 있어야 함: data/r01.json, data/r01_words.json(아티팩트 2b25e2df… 의 파일에서 가져옴), pages/r01/pNN.jpg(빈 그림이어도 됨), backup.json({app,v,round,saved,user,notes}).
- 교재 이미지·기록은 저작권·개인정보라 이 공개 저장소에 올리지 않는다.
- full_test.py: 숨긴 기능, 두문자 만들기·탭·글자/줄/주제 고치기·퀴즈, 메모, 틀린 빈칸 단원, 새로고침 뒤 내 빈칸 보존.
- pen_scroll_test.py: 두문자 만들기 중 펜 끌기 = 화면 넘김.
- dm_range_check.py: 두문자 설명 범위 규칙을 실제 OCR 줄에 돌려 보기.
- r02_test.py: 2편 추가 시험. /home/claude/test/교재_r02.zip(실제 2편 묶음)이 있어야 함. ① 2편이 목록에만 있고 기기에 없을 때 1편만 열림 ② 2편을 넣은 뒤 기록(U.add·ov·res·qres)과 내 빈칸 위치가 그대로 ③ 2편 묶음이 기기에서 사라져도 2편 빈칸 기록은 남고, 다시 넣으면 보임.
- mig_test.py: 책 순서 정렬과 저장 번호(sk) 시험. test_mig.zip(1편 + 옛 번호 p57·p79로 저장된 2편 메모), 교재_r02.zip, 가짜 test_r11.zip·test_r03.zip(2편 데이터의 쪽 번호만 바꾼 것)이 필요. 11편을 먼저 넣고 3편을 나중에 넣어도 메모·빈칸·이미지 교체가 제 쪽에 남는지 확인.
- r0304_test.py: 3편·4편 추가 시험. /home/claude/test/test_r01.zip(가짜 1편 + 기록), 교재_r03.zip, 교재_r04.zip. 4편을 먼저 넣어도 순서·기록 그대로, 4회차 4~7번이 4편 빈칸에 걸림, 101쪽 두 줄 제목 띠, 새로고침 뒤 내 빈칸 보존.
- r05_test.py: 5편 추가 시험. /home/claude/test/test_r05rec.zip(교재_r05.zip + backup.json: 기기에 없는 1편 쪽 내 빈칸과 5편 쪽 내 빈칸·핵심 빈칸). 기록 그대로, 6회차 1~5번 빈칸·답 범위, 목차(263쪽 제6편 편 제목), 학자 탭, 새로고침 뒤 새 내 빈칸 보존.
- two_device_test.py: 태블릿·PC 번갈아 쓰기. 두 브라우저가 가짜 드라이브(파이썬 dict)를 같이 쓴다. A) PC 빈칸이 태블릿 앱으로 돌아오면(focus) 자동으로 받아짐 B) 양쪽에 안 올라간 작업이 있을 때 덮어쓰지 않고 받아 온 뒤 내 빈칸이 합쳐지고, 충돌보관 파일이 남음. 드라이브 최신본에 양쪽 빈칸이 모두 있어야 함.
- two_device_memo_test.py: 두 기기 메모·펜 합치기. 양쪽에서 쓴 메모는 둘 다 남고, PC에서 지운 메모(mdel 묘비)는 지워진 채, 태블릿에서 그은 펜 선(sT가 더 나중)은 남는지.
