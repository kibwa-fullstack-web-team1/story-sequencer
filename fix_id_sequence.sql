-- ID 시퀀스 재설정 스크립트
-- stories 테이블의 id 시퀀스를 현재 최대값 다음부터 시작하도록 설정

-- 1. 현재 stories 테이블의 최대 id 확인
SELECT MAX(id) FROM stories;

-- 2. 시퀀스 재설정 (최대 id + 1부터 시작)
-- PostgreSQL에서 시퀀스 이름은 보통 'stories_id_seq'입니다
SELECT setval('stories_id_seq', (SELECT MAX(id) FROM stories));

-- 3. 시퀀스가 제대로 설정되었는지 확인
SELECT currval('stories_id_seq');
SELECT nextval('stories_id_seq');
