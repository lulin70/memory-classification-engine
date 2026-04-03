import json
from typing import Dict, List, Optional, Any

class SemanticClassifier:
    """Semantic memory classifier using LLM."""
    
    def __init__(self, llm_enabled: bool = False, api_key: str = None):
        """Initialize the semantic classifier.
        
        Args:
            llm_enabled: Whether to enable LLM-based classification.
            api_key: API key for the LLM service.
        """
        self.llm_enabled = llm_enabled
        self.api_key = api_key
    
    def classify(self, message: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Classify a message using semantic analysis.
        
        Args:
            message: The message to classify.
            context: Optional context for the message.
            
        Returns:
            A list of classified memories.
        """
        if not self.llm_enabled:
            # Return empty list if LLM is not enabled
            return []
        
        try:
            # In a real implementation, we would call an LLM API here
            # For now, we'll use a mock implementation
            return self._mock_classify(message, context)
        except Exception as e:
            print(f"Error in semantic classification: {e}")
            return []
    
    def _mock_classify(self, message: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Mock semantic classification for testing.
        
        Args:
            message: The message to classify.
            context: Optional context for the message.
            
        Returns:
            A list of classified memories.
        """
        classified_memories = []
        
        # Mock classification logic
        # In a real implementation, this would be done by an LLM
        
        # Check for fact declarations
        if any(keyword in message for keyword in ['是', '有', '在', '位于', '属于', '成立于', '创建于']):
            classified_memories.append({
                'memory_type': 'fact_declaration',
                'tier': 4,
                'content': message,
                'confidence': 0.8,
                'source': 'semantic:fact',
                'description': '事实声明'
            })
        
        # Check for relationship information
        if any(keyword in message for keyword in ['负责', '管理', '领导', '汇报', '属于', '合作', '关系']):
            classified_memories.append({
                'memory_type': 'relationship',
                'tier': 4,
                'content': message,
                'confidence': 0.7,
                'source': 'semantic:relationship',
                'description': '关系信息'
            })
        
        # Check for user preferences
        if any(keyword in message for keyword in ['喜欢', '偏好', '希望', '想要', '不要', '别', '避免']):
            classified_memories.append({
                'memory_type': 'user_preference',
                'tier': 2,
                'content': message,
                'confidence': 0.75,
                'source': 'semantic:preference',
                'description': '用户偏好'
            })
        
        # Check for corrections
        if any(keyword in message for keyword in ['不对', '错了', '不是', '你搞错了', '应该是', '实际上是']):
            classified_memories.append({
                'memory_type': 'correction',
                'tier': 3,
                'content': message,
                'confidence': 0.85,
                'source': 'semantic:correction',
                'description': '纠正信号'
            })
        
        return classified_memories
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM API.
        
        Args:
            prompt: The prompt to send to the LLM.
            
        Returns:
            The LLM's response.
        """
        # In a real implementation, this would call an LLM API like OpenAI's GPT
        # For now, we'll return a mock response
        return "{\"has_memory\": true, \"memory_type\": \"user_preference\", \"tier\": 2, \"content\": \"Test content\", \"confidence\": 0.9, \"reasoning\": \"Test reasoning\"}"
    
    def _generate_prompt(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a prompt for the LLM.
        
        Args:
            message: The message to classify.
            context: Optional context for the message.
            
        Returns:
            The generated prompt.
        """
        prompt = f"""
你是一个记忆分类器。分析以下对话片段，判断是否有值得长期记忆的信息。

记忆类型包括：
- user_preference: 用户表达的偏好或习惯
- fact_declaration: 用户陈述的客观事实
- decision: 达成的明确决定或结论
- relationship: 涉及人物、团队、组织之间的关系
- task_pattern: 反复出现的任务类型
- sentiment_marker: 用户对某话题的情感倾向
- correction: 用户对之前输出的纠正

如果对话中没有值得记忆的信息，返回空。

当前对话：
{message}

已知的用户记忆：
{json.dumps(context.get('existing_memories', []), ensure_ascii=False) if context else '[]'}

请以JSON格式输出，包含以下字段：
- has_memory: boolean
- memory_type: string (枚举值)
- content: string (记忆内容，简洁准确)
- tier: int (2=程序性记忆, 3=情节记忆, 4=语义记忆)
- confidence: float (0.0-1.0)
- reasoning: string (简要判断理由)
"""
        return prompt
