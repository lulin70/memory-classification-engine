"""agentskills.io format compatibility module."""

import json
import yaml
from typing import Dict, List, Any

class AgentSkillsIO:
    """agentskills.io format compatibility class."""
    
    @staticmethod
    def mce_to_agentskills(mce_rule: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MCE rule to agentskills.io format.
        
        Args:
            mce_rule: MCE rule dictionary
            
        Returns:
            agentskills.io formatted skill
        """
        skill = {
            'name': mce_rule.get('name', 'mce-rule'),
            'description': mce_rule.get('description', 'Memory classification rule'),
            'author': mce_rule.get('author', 'Memory Classification Engine'),
            'version': mce_rule.get('version', '1.0.0'),
            'category': AgentSkillsIO._map_memory_type(mce_rule.get('memory_type', 'general')),
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'description': 'Message to classify'
                    },
                    'context': {
                        'type': 'string',
                        'description': 'Optional context'
                    }
                },
                'required': ['message']
            },
            'outputSchema': {
                'type': 'object',
                'properties': {
                    'memory_type': {
                        'type': 'string',
                        'description': 'Classified memory type'
                    },
                    'confidence': {
                        'type': 'number',
                        'description': 'Classification confidence'
                    },
                    'content': {
                        'type': 'string',
                        'description': 'Extracted memory content'
                    }
                }
            },
            'examples': [
                {
                    'input': {
                        'message': mce_rule.get('example', 'Test message')
                    },
                    'output': {
                        'memory_type': mce_rule.get('memory_type', 'general'),
                        'confidence': 0.9,
                        'content': mce_rule.get('example', 'Test message')
                    }
                }
            ]
        }
        
        return skill
    
    @staticmethod
    def agentskills_to_mce(skill: Dict[str, Any]) -> Dict[str, Any]:
        """Convert agentskills.io format to MCE rule.
        
        Args:
            skill: agentskills.io formatted skill
            
        Returns:
            MCE rule dictionary
        """
        mce_rule = {
            'name': skill.get('name', 'agentskills-rule'),
            'description': skill.get('description', 'Imported from agentskills.io'),
            'pattern': skill.get('pattern', '.*'),
            'memory_type': AgentSkillsIO._map_category(skill.get('category', 'general')),
            'tier': AgentSkillsIO._get_tier(skill.get('category', 'general')),
            'action': skill.get('action', 'extract'),
            'author': skill.get('author', 'agentskills.io'),
            'version': skill.get('version', '1.0.0'),
            'example': skill.get('examples', [{}])[0].get('input', {}).get('message', 'Test message')
        }
        
        return mce_rule
    
    @staticmethod
    def _map_memory_type(memory_type: str) -> str:
        """Map MCE memory type to agentskills.io category."""
        mapping = {
            'user_preference': 'preference',
            'correction': 'correction',
            'fact_declaration': 'fact',
            'decision': 'decision',
            'relationship': 'relationship',
            'task_pattern': 'task',
            'sentiment_marker': 'sentiment',
            'positive_feedback': 'feedback',
            'negative_feedback': 'feedback',
            'tool_error': 'error',
            'retry_needed': 'error',
            'performance_issue': 'performance',
            'correction_followup': 'followup',
            'confirmation_pending': 'followup'
        }
        return mapping.get(memory_type, 'general')
    
    @staticmethod
    def _map_category(category: str) -> str:
        """Map agentskills.io category to MCE memory type."""
        mapping = {
            'preference': 'user_preference',
            'correction': 'correction',
            'fact': 'fact_declaration',
            'decision': 'decision',
            'relationship': 'relationship',
            'task': 'task_pattern',
            'sentiment': 'sentiment_marker',
            'feedback': 'positive_feedback',
            'error': 'tool_error',
            'performance': 'performance_issue',
            'followup': 'correction_followup'
        }
        return mapping.get(category, 'general')
    
    @staticmethod
    def _get_tier(category: str) -> int:
        """Get appropriate tier for agentskills.io category."""
        tier_map = {
            'preference': 2,
            'task': 2,
            'correction': 3,
            'decision': 3,
            'sentiment': 3,
            'feedback': 3,
            'error': 3,
            'performance': 3,
            'followup': 3,
            'fact': 4,
            'relationship': 4
        }
        return tier_map.get(category, 3)
    
    @staticmethod
    def save_skill(skill: Dict[str, Any], output_path: str):
        """Save skill to SKILL.md file.
        
        Args:
            skill: agentskills.io formatted skill
            output_path: Path to save SKILL.md
        """
        # Comment in Chinese removedr
        frontmatter = skill.copy()
        
        # Comment in Chinese removednt
        content = frontmatter.pop('content', '')
        
        # Comment in Chinese removed
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('---\n')
            f.write(yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True))
            f.write('---\n')
            f.write(content)
    
    @staticmethod
    def load_skill(input_path: str) -> Dict[str, Any]:
        """Load skill from SKILL.md file.
        
        Args:
            input_path: Path to SKILL.md file
            
        Returns:
            agentskills.io formatted skill
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Comment in Chinese removedr
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 2:
                frontmatter = yaml.safe_load(parts[1])
                skill_content = parts[2].strip() if len(parts) > 2 else ''
                frontmatter['content'] = skill_content
                return frontmatter
        
        return {'content': content}
