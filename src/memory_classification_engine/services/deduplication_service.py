"""Deduplication service for handling memory deduplication and conflict resolution."""

from typing import Dict, List, Any
from memory_classification_engine.utils.logger import logger


class DeduplicationService:
    """Service for deduplicating and resolving conflicts in memories."""
    
    def __init__(self, config: Any):
        """Initialize deduplication service.
        
        Args:
            config: Configuration manager instance.
        """
        self.config = config
        self.enabled = config.get('memory.deduplication.enabled', True)
        self.similarity_threshold = config.get('memory.deduplication.similarity_threshold', 0.8)
        self.conflict_resolution_strategy = config.get('memory.conflict_resolution.strategy', 'latest')
        
        # Comment in Chinese removedzily
        from memory_classification_engine.utils.semantic import semantic_utility
        self.semantic_utility = semantic_utility
    
    def deduplicate(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate matches.
        
        Args:
            matches: List of matches to deduplicate.
            
        Returns:
            List of unique matches.
        """
        if not self.enabled:
            return matches
        
        unique_matches = []
        
        for match in matches:
            content = match.get('content', '').strip()
            memory_type = match.get('memory_type', '')
            is_duplicate = False
            
            for existing_match in unique_matches:
                existing_content = existing_match.get('content', '').strip()
                existing_memory_type = existing_match.get('memory_type', '')
                
                # Comment in Chinese removed
                if memory_type == existing_memory_type:
                    similarity = self._calculate_semantic_similarity(content, existing_content)
                    
                    if similarity > self.similarity_threshold:
                        is_duplicate = True
                        # Comment in Chinese removedlict
                        if self._detect_conflict(match, existing_match):
                            # Comment in Chinese removedlict
                            resolved_match = self._resolve_conflict(match, existing_match)
                            unique_matches.remove(existing_match)
                            unique_matches.append(resolved_match)
                        else:
                            # Comment in Chinese removed
                            if self._is_better_match(match, existing_match):
                                unique_matches.remove(existing_match)
                                unique_matches.append(match)
                        break
            
            if not is_duplicate:
                unique_matches.append(match)
        
        return unique_matches
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts.
        
        Args:
            text1: First text.
            text2: Second text.
            
        Returns:
            Similarity score between 0 and 1.
        """
        return self.semantic_utility.calculate_similarity(text1, text2)
    
    def _is_better_match(self, match1: Dict[str, Any], match2: Dict[str, Any]) -> bool:
        """Determine if match1 is better than match2.
        
        Args:
            match1: First match.
            match2: Second match.
            
        Returns:
            True if match1 is better, False otherwise.
        """
        # Comment in Chinese removeds
        confidence1 = match1.get('confidence', 0)
        confidence2 = match2.get('confidence', 0)
        
        if confidence1 != confidence2:
            return confidence1 > confidence2
        
        # Comment in Chinese removed priority
        source_priority = {
            'rule': 4,      # Comment in Chinese removed
            'pattern': 3,    # Comment in Chinese removedxt
            'semantic': 2,   # Comment in Chinese removed
            'default': 1     # Comment in Chinese removed
        }
        
        def get_source_priority(source):
            for key, priority in source_priority.items():
                if key in source:
                    return priority
            return 0
        
        priority1 = get_source_priority(match1.get('source', ''))
        priority2 = get_source_priority(match2.get('source', ''))
        
        if priority1 != priority2:
            return priority1 > priority2
        
        # Comment in Chinese removedr)
        time1 = match1.get('created_at', '')
        time2 = match2.get('created_at', '')
        
        return time1 > time2
    
    def _detect_conflict(self, memory1: Dict[str, Any], memory2: Dict[str, Any]) -> bool:
        """Detect if two memories conflict.
        
        Args:
            memory1: First memory.
            memory2: Second memory.
            
        Returns:
            True if memories conflict, False otherwise.
        """
        # Comment in Chinese removedtion
        content1 = memory1.get('content', '').lower()
        content2 = memory2.get('content', '').lower()
        
        # Comment in Chinese removed
        chinese_negation_words = ['不', '没', '没有', '不是', '不要', '不喜欢', '不想要', '反对', '拒绝', '否定']
        # Comment in Chinese removednglish
        english_negation_words = ['not', 'no', 'don\'t', 'doesn\'t', 'didn\'t', 'won\'t', 'can\'t', 'never', 'against', 'reject', 'deny']
        
        # Comment in Chinese removedtion
        for word in chinese_negation_words:
            if word in content1 and word not in content2:
                # Comment in Chinese removedr
                content1_without_negation = content1.replace(word, '').strip()
                similarity = self._calculate_semantic_similarity(content1_without_negation, content2)
                if similarity > self.similarity_threshold:
                    return True
            elif word in content2 and word not in content1:
                # Comment in Chinese removedr
                content2_without_negation = content2.replace(word, '').strip()
                similarity = self._calculate_semantic_similarity(content1, content2_without_negation)
                if similarity > self.similarity_threshold:
                    return True
        
        # Comment in Chinese removedtion
        for word in english_negation_words:
            if word in content1 and word not in content2:
                # Comment in Chinese removedr
                content1_without_negation = content1.replace(word, '').strip()
                similarity = self._calculate_semantic_similarity(content1_without_negation, content2)
                if similarity > self.similarity_threshold:
                    return True
            elif word in content2 and word not in content1:
                # Comment in Chinese removedr
                content2_without_negation = content2.replace(word, '').strip()
                similarity = self._calculate_semantic_similarity(content1, content2_without_negation)
                if similarity > self.similarity_threshold:
                    return True
        
        # Comment in Chinese removednt
        if 'sentiment_marker' in memory1.get('memory_type', '') and 'sentiment_marker' in memory2.get('memory_type', ''):
            if '正面' in content1 and '负面' in content2:
                return True
            if '负面' in content1 and '正面' in content2:
                return True
            if 'positive' in content1 and 'negative' in content2:
                return True
            if 'negative' in content1 and 'positive' in content2:
                return True
        
        return False
    
    def _resolve_conflict(self, memory1: Dict[str, Any], memory2: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflict between two memories.
        
        Args:
            memory1: First memory.
            memory2: Second memory.
            
        Returns:
            Resolved memory.
        """
        strategy = self.conflict_resolution_strategy
        
        if strategy == 'latest':
            # Comment in Chinese removedmory
            time1 = memory1.get('created_at', '')
            time2 = memory2.get('created_at', '')
            return memory1 if time1 > time2 else memory2
        elif strategy == 'highest_confidence':
            # Comment in Chinese removed
            confidence1 = memory1.get('confidence', 0)
            confidence2 = memory2.get('confidence', 0)
            return memory1 if confidence1 > confidence2 else memory2
        elif strategy == 'best_source':
            # Comment in Chinese removed
            if self._is_better_match(memory1, memory2):
                return memory1
            else:
                return memory2
        elif strategy == 'merge':
            # Comment in Chinese removedxt
            merged_content = f"{memory1.get('content', '')} (conflict resolved: {memory2.get('content', '')})"
            merged_confidence = (memory1.get('confidence', 0) + memory2.get('confidence', 0)) / 2
            return {
                'memory_type': memory1.get('memory_type', memory2.get('memory_type')),
                'tier': max(memory1.get('tier', 3), memory2.get('tier', 3)),
                'content': merged_content,
                'confidence': merged_confidence,
                'source': f"conflict_resolved:{memory1.get('source', '')}:{memory2.get('source', '')}",
                'description': 'Conflict resolved by merging'
            }
        else:
            # Comment in Chinese removedst
            time1 = memory1.get('created_at', '')
            time2 = memory2.get('created_at', '')
            return memory1 if time1 > time2 else memory2
