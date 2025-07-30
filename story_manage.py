import uvicorn
from app import create_app
import os
from dotenv import load_dotenv

load_dotenv()

# Environment variables setup (실제 프로덕션 키 사용)
os.environ['SECRET_KEY'] = os.getenv('SECRET_KEY')
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL')
os.environ['PHASE'] = os.getenv('PHASE')

SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

# Lab environment detection - explicit opt-in required
if os.getenv('SERVICE_LAB_MODE', '').lower() == 'true':
    config_name = 'lab_development'
else:
    config_name = os.getenv('PHASE') or 'development'

app = create_app(config_name)

if __name__ == '__main__':
    uvicorn.run(
        "story_manage:app",
        host='0.0.0.0',
        port=8011,
        reload=True
    ) 