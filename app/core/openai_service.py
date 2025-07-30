import os
import openai
import json
import re
import logging
from typing import List

class OpenAIService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.api_key:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
                self.logger.info("OpenAI client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None

    def init_app(self, app):
        """앱 초기화"""
        self.logger.info("OpenAIService initialized")
        return self

    def split_story_into_segments(self, content: str) -> List[str]:
        """AI를 사용하여 이야기를 문장 단위로 분리"""
        try:
            if not self.client:
                self.logger.warning("OpenAI client not available, using fallback method")
                return self._fallback_split(content)
            
            prompt = (
                "아래 이야기를 순서대로 문장 단위로 나눠서 JSON 배열로 만들어줘. "
                "각 문장은 따옴표로 감싸고, 배열 형태로만 답변해줘. "
                "예시: [\"첫 번째 문장입니다.\", \"두 번째 문장입니다.\"]\n\n"
                f"{content}"
            )
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "너는 문장 분리기야. 주어진 텍스트를 문장 단위로 나누어 JSON 배열로 반환해줘."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1024,
                temperature=0.2,
            )
            
            text = response.choices[0].message.content
            if text:
                # JSON 배열 패턴 찾기
                match = re.search(r'\[.*\]', text, re.DOTALL)
                if match:
                    try:
                        segments = json.loads(match.group(0))
                        if isinstance(segments, list) and len(segments) > 0:
                            self.logger.info(f"Successfully split story into {len(segments)} segments")
                            return segments
                    except json.JSONDecodeError as e:
                        self.logger.error(f"JSON parsing error: {e}")
                
                # JSON 파싱 실패 시 쉼표로 분리 시도
                self.logger.warning("JSON parsing failed, trying comma-based split")
                return self._extract_sentences_from_text(text)
            else:
                self.logger.warning("Empty response from OpenAI, using fallback")
                return self._fallback_split(content)
                
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return self._fallback_split(content)

    def _extract_sentences_from_text(self, text: str) -> List[str]:
        """텍스트에서 문장들을 추출하는 보조 메서드"""
        try:
            # 따옴표로 감싸진 문장들 찾기
            sentences = re.findall(r'"([^"]*)"', text)
            if sentences:
                return [s.strip() for s in sentences if s.strip()]
            
            # 쉼표나 마침표로 분리
            sentences = re.split(r'[,.]', text)
            return [s.strip() for s in sentences if s.strip()]
        except Exception as e:
            self.logger.error(f"Error extracting sentences: {e}")
            return self._fallback_split(text)

    def _fallback_split(self, content: str) -> List[str]:
        """OpenAI API 실패 시 기본 분리 방법"""
        try:
            # 마침표로 분리하고 빈 문자열 제거
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            self.logger.info(f"Using fallback split method, created {len(sentences)} segments")
            return sentences
        except Exception as e:
            self.logger.error(f"Fallback split error: {e}")
            return [content]  # 최후의 수단으로 전체 내용을 하나의 세그먼트로

    def generate_story_summary(self, content: str) -> str:
        """이야기 요약 생성"""
        try:
            if not self.client:
                return "AI 요약을 사용할 수 없습니다."
            
            prompt = f"다음 이야기를 간단히 요약해주세요:\n\n{content}"
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "너는 이야기 요약 전문가야."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return "요약을 생성할 수 없습니다." 