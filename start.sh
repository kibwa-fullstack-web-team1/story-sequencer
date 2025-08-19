#!/bin/bash

# Story API 서비스 시작 스크립트

set -e  # 에러 발생 시 스크립트 중단

echo "Starting Story API Service..."

# 환경변수 설정
export PHASE=${PHASE:-development}
export OPENAI_API_KEY=${OPENAI_API_KEY}
export STORY_DATABASE_URL=${STORY_DATABASE_URL}
export SERVICE_LAB_MODE=${SERVICE_LAB_MODE:-false}
export CORE_MODULES_AVAILABLE=${CORE_MODULES_AVAILABLE:-true}

# 필수 환경변수 검증
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY is not set"
fi

if [ -z "$STORY_DATABASE_URL" ]; then
    echo "Warning: STORY_DATABASE_URL is not set"
fi

# 로그 디렉토리 생성
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"
echo "Log directory: $LOG_DIR"

# Python 가상환경 활성화 (필요시)
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# 의존성 설치
echo "Installing dependencies..."
pip install -r requirements.txt

# 서비스 시작
echo "Starting service on port 8011..."
uvicorn story_manage:app --host 0.0.0.0 --port 8011 --reload 