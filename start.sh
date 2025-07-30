#!/bin/bash

# Story API 서비스 시작 스크립트

# 환경변수 설정
export PHASE=${PHASE:-development}
export OPENAI_API_KEY=${OPENAI_API_KEY}
export STORY_DATABASE_URL=${STORY_DATABASE_URL}

# 로그 디렉토리 생성
mkdir -p /var/log/story-api

# Python 가상환경 활성화 (필요시)
# source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 서비스 시작
uvicorn story_manage:app --host 0.0.0.0 --port 8011 --reload 