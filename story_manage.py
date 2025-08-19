import uvicorn
from app import create_app
import os
from dotenv import load_dotenv

load_dotenv()

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