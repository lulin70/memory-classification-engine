import re
import time
import json
from typing import Dict, Any, Optional

# Comment in Chinese removedinitions
MEMORY_TYPES = {
    "user_preference": "用户偏好",
    "correction": "纠正信号",
    "fact_declaration": "事实声明",
    "decision": "决策记录",
    "relationship": "关系信息",
    "task_pattern": "任务模式",
    "sentiment_marker": "情感标记"
}

# Comment in Chinese removedinitions
MEMORY_TIERS = {
    1: "工作记忆",
    2: "程序性记忆",
    3: "情节记忆",
    4: "语义记忆"
}

def generate_memory_id() -> str:
    """Generate a unique memory ID.
    
    Returns:
        A unique memory ID.
    """
    import random
    timestamp = int(time.time() * 1000)
    random_suffix = random.randint(1000, 9999)
    return f"mem_{timestamp}_{random_suffix}"

def get_current_time() -> str:
    """Get the current time in ISO format.
    
    Returns:
        The current time as an ISO string.
    """
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def extract_content(text: str, pattern: str, action: str) -> Optional[str]:
    """Extract content from text based on pattern and action.
    
    Args:
        text: The text to extract from.
        pattern: The regex pattern to match.
        action: The action to perform.
        
    Returns:
        The extracted content or None.
    """
    match = re.search(pattern, text)
    if not match:
        return None
    
    if action == "extract_following_content":
        # Comment in Chinese removedrn
        start = match.end()
        content = text[start:].strip()
        # Comment in Chinese removedtion
        content = re.sub(r'[.!?]+$', '', content)
        return content
    
    elif action == "extract_surrounding_context":
        # Comment in Chinese removedrn
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 100)
        content = text[start:end].strip()
        return content
    
    elif action == "extract_entity_and_relation":
        # Comment in Chinese removedtion
        content = text.strip()
        return content
    
    elif action == "extract_preceding_proposal":
        # Comment in Chinese removedrn
        end = match.start()
        content = text[:end].strip()
        # Comment in Chinese removedtion
        content = re.sub(r'[.!?]+$', '', content)
        return content
    
    elif action == "extract":
        # Comment in Chinese removednt
        content = match.group(0)
        return content
    
    return None

def calculate_memory_weight(confidence: float, days_since_last_access: int, access_count: int) -> float:
    """Calculate memory weight based on confidence, recency, and frequency.
    
    Args:
        confidence: Confidence score (0.0-1.0).
        days_since_last_access: Days since last access.
        access_count: Number of times the memory has been accessed.
        
    Returns:
        The calculated memory weight.
    """
    # Comment in Chinese removedncy
    recency_score = 2 ** (-0.1 * days_since_last_access)
    
    # Comment in Chinese removedncy (边际递减)
    frequency_score = 1 + 0.5 * (access_count ** 0.5)
    
    # Comment in Chinese removedight
    weight = confidence * recency_score * frequency_score
    
    return weight

def format_memory(memory: Dict[str, Any]) -> str:
    """Format memory as a string for display.
    
    Args:
        memory: The memory dictionary.
        
    Returns:
        The formatted memory string.
    """
    memory_type = MEMORY_TYPES.get(memory.get('type', 'unknown'), 'unknown')
    tier = MEMORY_TIERS.get(memory.get('tier', 1), 'unknown')
    
    return f"[{tier}] {memory_type}: {memory.get('content', '')} (confidence: {memory.get('confidence', 0.0):.2f})"

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON data from file.
    
    Args:
        file_path: Path to the JSON file.
        
    Returns:
        The loaded JSON data as a dictionary.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return {}

def save_json_file(file_path: str, data: Dict[str, Any]):
    """Save JSON data to file.
    
    Args:
        file_path: Path to the JSON file.
        data: The data to save.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving JSON file: {e}")
