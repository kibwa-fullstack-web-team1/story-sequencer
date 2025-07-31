# story-sequencer/Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY story-sequencer/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY story-sequencer/app ./app
COPY story-sequencer/story_manage.py .

EXPOSE 8011

CMD ["python", "story_manage.py"]
