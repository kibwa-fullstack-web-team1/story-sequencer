#!/bin/bash

# Story API 서비스 랩 환경 시작 스크립트

set -e  # 에러 발생 시 스크립트 중단

echo "Starting Story API Service in LAB mode..."

# 랩 환경 설정
export PHASE=development
export SERVICE_LAB_MODE=true
export CORE_MODULES_AVAILABLE=false

# 환경변수 설정
export OPENAI_API_KEY=${OPENAI_API_KEY:-mock_key}
export STORY_DATABASE_URL=${STORY_DATABASE_URL:-sqlite:///test.db}
export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-mock_key}
export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-mock_secret}
export S3_BUCKET_NAME=${S3_BUCKET_NAME:-mock-bucket}
export AWS_REGION=${AWS_REGION:-us-east-1}

echo "Lab mode enabled: SERVICE_LAB_MODE=$SERVICE_LAB_MODE"
echo "Core modules disabled: CORE_MODULES_AVAILABLE=$CORE_MODULES_AVAILABLE"

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
echo "Starting service in LAB mode on port 8011..."
uvicorn story_manage:app --host 0.0.0.0 --port 8011 --reload 