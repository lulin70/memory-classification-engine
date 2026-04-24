"""Semantic recall engine for CarryMem v0.4.0.

Provides zero-dependency semantic expansion for memory recall:
- Synonym graph (同义词图谱)
- Spell correction (拼写纠错)
- Cross-language mapping (跨语言映射)
- Result fusion (结果融合)

Architecture:
    query → FTS5 (exact) → SemanticExpander → expanded queries → FTS5 → ResultMerger → final results
"""

from .expander import SemanticExpander
from .merger import ResultMerger

__all__ = ["SemanticExpander", "ResultMerger"]
