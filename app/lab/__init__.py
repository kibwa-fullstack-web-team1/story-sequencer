from app.lab.mock_base import DynamicMock

class MockStoryService(DynamicMock):
    def __init__(self):
        super().__init__("MockStoryService")
        self._method_responses = {
            'create_story': {
                'id': 1,
                'title': 'Mock Story',
                'content': 'This is a mock story content.',
                'image_url': None,
                'created_at': '2025-01-01T00:00:00',
                'updated_at': '2025-01-01T00:00:00',
                'segments': [
                    {'id': 1, 'story_id': 1, 'order': 1, 'segment_text': 'This is a mock story content.'}
                ]
            },
            'get_story': {
                'id': 1,
                'title': 'Mock Story',
                'content': 'This is a mock story content.',
                'image_url': None,
                'created_at': '2025-01-01T00:00:00',
                'updated_at': '2025-01-01T00:00:00',
                'segments': [
                    {'id': 1, 'story_id': 1, 'order': 1, 'segment_text': 'This is a mock story content.'}
                ]
            },
            'get_stories': [
                {
                    'id': 1,
                    'title': 'Mock Story 1',
                    'content': 'This is a mock story content.',
                    'image_url': None,
                    'created_at': '2025-01-01T00:00:00',
                    'updated_at': '2025-01-01T00:00:00',
                    'segments': []
                }
            ]
        }

class MockOpenAIService(DynamicMock):
    def __init__(self):
        super().__init__("MockOpenAIService")
        self._method_responses = {
            'split_story': ['This is a mock story content.']
        } 