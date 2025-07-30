# Story API Service

기억의 정원 프로젝트의 이야기 관리 API 서비스입니다.

## 프로젝트 구조

```
story-api/
├── app/
│   ├── __init__.py                 # FastAPI 앱 팩토리
│   ├── api/                        # API 엔드포인트 정의
│   │   ├── __init__.py            # 라우터 등록
│   │   └── story.py               # Story API
│   ├── common/                     # 공통 모듈
│   │   └── response.py            # 응답 처리
│   ├── config/                     # 설정 관리
│   │   └── config.py              # 기본 설정
│   ├── core/                       # 핵심 서비스
│   │   └── story_service.py       # Story 서비스
│   ├── helper/                     # 비즈니스 로직
│   │   └── story_helper.py        # Story 헬퍼
│   ├── models/                     # 데이터 모델
│   │   └── story.py               # Story 모델
│   ├── schemas/                    # 데이터 스키마
│   │   └── story.py               # Story 스키마
│   ├── utils/                      # 유틸리티
│   │   ├── functions.py           # 공통 함수
│   │   └── logger.py              # 로깅
│   ├── lab/                        # 테스트 환경
│   │   ├── __init__.py            # Mock 서비스
│   │   └── mock_base.py           # Mock 기본 클래스
│   └── database.py                 # 데이터베이스 설정
├── story_manage.py                 # 앱 실행 파일
├── requirements.txt                # 의존성
├── start.sh                        # 시작 스크립트
├── start_lab.sh                    # 랩 환경 시작 스크립트
└── README.md                       # 프로젝트 문서
```

## 환경 설정

### 환경변수

- `PHASE`: 실행 환경 (development, production, lab_development)
- `OPENAI_API_KEY`: OpenAI API 키
- `STORY_DATABASE_URL`: 데이터베이스 연결 URL
- `SERVICE_LAB_MODE`: 랩 환경 모드 (true/false)
- `AWS_ACCESS_KEY_ID`: AWS 액세스 키 ID
- `AWS_SECRET_ACCESS_KEY`: AWS 시크릿 액세스 키
- `AWS_REGION`: AWS 리전 (기본값: ap-northeast-2)
- `S3_BUCKET_NAME`: S3 버킷 이름 (기본값: memory-garden-images)

### 환경별 설정

#### Development
```bash
export PHASE=development
export OPENAI_API_KEY=your_openai_key
export STORY_DATABASE_URL=your_database_url
export AWS_ACCESS_KEY_ID=your_aws_access_key_id
export AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
export AWS_REGION=ap-northeast-2
export S3_BUCKET_NAME=memory-garden-images
```

#### Lab Environment
```bash
export SERVICE_LAB_MODE=true
export PHASE=lab_development
```

## 실행 방법

### 일반 실행
```bash
chmod +x start.sh
./start.sh
```

### 랩 환경 실행
```bash
chmod +x start_lab.sh
./start_lab.sh
```

### 직접 실행
```bash
uvicorn story_manage:app --host 0.0.0.0 --port 8011 --reload
```

## API 엔드포인트

### Story API

- `GET /api/v0/stories/` - 이야기 목록 조회
- `POST /api/v0/stories/` - 이야기 생성
- `GET /api/v0/stories/{story_id}` - 이야기 상세 조회
- `PUT /api/v0/stories/{story_id}` - 이야기 수정
- `DELETE /api/v0/stories/{story_id}` - 이야기 삭제

### Upload API

- `POST /api/v0/upload/image` - 이미지 업로드
- `DELETE /api/v0/upload/image` - 이미지 삭제

### Admin Panel

- `GET /api/v0/admin/` - 관리자 패널

### API 문서

- `/docs` - Swagger UI 문서
- `/redoc` - ReDoc 문서

## 주요 기능

1. **이야기 관리**: CRUD 작업
2. **AI 문장 분리**: OpenAI를 사용한 자동 문장 분리
3. **이미지 업로드**: S3를 통한 이미지 저장 및 관리
4. **관리자 패널**: 웹 기반 이야기 관리 인터페이스
5. **환경별 서비스 분리**: Production/Development/Lab 환경 지원
6. **Mock 서비스**: 랩 환경에서 외부 서비스 Mock 처리
7. **표준화된 응답**: 일관된 API 응답 형식
8. **에러 처리**: 계층화된 예외 처리

## S3 설정 가이드

### 1. AWS S3 버킷 생성
1. AWS 콘솔에서 S3 서비스로 이동
2. "버킷 만들기" 클릭
3. 버킷 이름 설정 (예: memory-garden-images)
4. 리전 선택 (ap-northeast-2 권장)
5. 퍼블릭 액세스 차단 해제 (이미지 공개 접근을 위해)

### 2. CORS 설정
버킷의 권한 탭에서 CORS 설정 추가:
```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "POST", "PUT", "DELETE"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```

### 3. 버킷 정책 설정
버킷의 권한 탭에서 버킷 정책 추가:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        }
    ]
}
```

### 4. IAM 사용자 생성
1. IAM 서비스에서 새 사용자 생성
2. S3FullAccess 정책 연결
3. 액세스 키 ID와 시크릿 액세스 키 생성
4. 환경 변수에 설정

## 개발 가이드

### 새로운 API 추가

1. `app/api/` 디렉토리에 새로운 API 파일 생성
2. `app/helper/` 디렉토리에 비즈니스 로직 구현
3. `app/core/` 디렉토리에 서비스 로직 구현
4. `app/api/__init__.py`에 라우터 등록

### Mock 서비스 추가

1. `app/lab/mock_base.py`의 `DynamicMock` 클래스 상속
2. `app/lab/__init__.py`에 Mock 서비스 등록
3. `app/__init__.py`에서 환경별 서비스 분기 처리

## 배포

### Docker (예시)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8011

CMD ["uvicorn", "story_manage:app", "--host", "0.0.0.0", "--port", "8011"]
```

### 시스템 서비스
```bash
# story-api.service 파일 생성 후
sudo systemctl enable story-api
sudo systemctl start story-api
``` 