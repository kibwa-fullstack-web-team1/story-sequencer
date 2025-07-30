from typing import List, Dict, Any

def validate_story_content(content: str) -> bool:
    """
    이야기 내용의 유효성을 검사합니다.
    
    Args:
        content: 검사할 이야기 내용
        
    Returns:
        bool: 유효성 여부
    """
    if not content or not content.strip():
        return False
    
    if len(content.strip()) < 10:
        return False
    
    return True

def validate_story_title(title: str) -> bool:
    """
    이야기 제목의 유효성을 검사합니다.
    
    Args:
        title: 검사할 이야기 제목
        
    Returns:
        bool: 유효성 여부
    """
    if not title or not title.strip():
        return False
    
    if len(title.strip()) < 2:
        return False
    
    if len(title.strip()) > 255:
        return False
    
    return True 