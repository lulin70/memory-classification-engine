#!/usr/bin/env python3
"""
简单测试脚本

测试系统的基本功能，包括直接调用分类功能
"""

import sys
import time
from typing import Dict, Any, Optional

# 直接导入引擎
from memory_classification_engine.engine_facade import MemoryClassificationEngineFacade


class SimpleTester:
    """简单测试器"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        # 初始化引擎
        self.engine = MemoryClassificationEngineFacade()
        # 测试数据
        self.test_data = [
            ("我喜欢在早晨喝咖啡，下午喝茶", "个人偏好设置"),
            ("明天上午10点有医生预约", "个人日程安排"),
            ("今天工作很顺利，我感到非常开心", "个人情绪记录")
        ]
