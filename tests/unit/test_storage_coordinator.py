import unittest
from unittest.mock import Mock, patch
from memory_classification_engine.coordinators.storage_coordinator import StorageCoordinator


class TestStorageCoordinator(unittest.TestCase):
    """测试StorageCoordinator类的单元测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建配置模拟
        self.config = Mock()
        self.config.get.side_effect = lambda key, default=None: {
            'storage.data_path': './data',
            'storage.tier2_path': './data/tier2',
            'storage.tier3_path': './data/tier3',
            'storage.tier4_path': './data/tier4',
            'memory.forgetting.min_weight': 0.1
        }.get(key, default)
        
        # 创建存储层模拟
        self.tier2_mock = Mock()
        self.tier3_mock = Mock()
        self.tier4_mock = Mock()
    
    @patch('memory_classification_engine.coordinators.storage_coordinator.Tier2Storage')
    @patch('memory_classification_engine.coordinators.storage_coordinator.Tier3Storage')
    @patch('memory_classification_engine.coordinators.storage_coordinator.Tier4Storage')
    def test_get_stats_with_valid_data(self, mock_tier4, mock_tier3, mock_tier2):
        """测试get_stats方法处理有效数据"""
        # 配置模拟返回值
        mock_tier2.return_value.get_stats.return_value = {'total_memories': 10, 'total_preferences': 5, 'total_corrections': 5}
        mock_tier3.return_value.get_stats.return_value = {'total_memories': 20, 'active_memories': 15}
        mock_tier4.return_value.get_stats.return_value = {'total_memories': 30, 'active_memories': 25}
        
        # 创建存储协调器实例
        coordinator = StorageCoordinator(self.config)
        
        # 调用get_stats方法
        stats = coordinator.get_stats()
        
        # 验证结果
        self.assertEqual(stats['total_memories'], 60)
    
    @patch('memory_classification_engine.coordinators.storage_coordinator.Tier2Storage')
    @patch('memory_classification_engine.coordinators.storage_coordinator.Tier3Storage')
    @patch('memory_classification_engine.coordinators.storage_coordinator.Tier4Storage')
    def test_get_stats_with_invalid_data(self, mock_tier4, mock_tier3, mock_tier2):
        """测试get_stats方法处理无效数据"""
        # 配置模拟返回值（包含无效类型）
        mock_tier2.return_value.get_stats.return_value = {'total_memories': '10'}  # 字符串类型
        mock_tier3.return_value.get_stats.return_value = {'total_memories': None}  # None类型
        mock_tier4.return_value.get_stats.return_value = {}  # 缺少total_memories键
        
        # 创建存储协调器实例
        coordinator = StorageCoordinator(self.config)
        
        # 调用get_stats方法
        stats = coordinator.get_stats()
        
        # 验证结果（应该安全处理这些情况）
        self.assertEqual(stats['total_memories'], 0)  # 所有无效值都应该被视为0
    
    @patch('memory_classification_engine.coordinators.storage_coordinator.Tier2Storage')
    @patch('memory_classification_engine.coordinators.storage_coordinator.Tier3Storage')
    @patch('memory_classification_engine.coordinators.storage_coordinator.Tier4Storage')
    def test_get_stats_with_non_dict_return(self, mock_tier4, mock_tier3, mock_tier2):
        """测试get_stats方法处理非字典返回值"""
        # 配置模拟返回非字典值
        mock_tier2.return_value.get_stats.return_value = None  # None
        mock_tier3.return_value.get_stats.return_value = []  # 列表
        mock_tier4.return_value.get_stats.return_value = 123  # 数字
        
        # 创建存储协调器实例
        coordinator = StorageCoordinator(self.config)
        
        # 调用get_stats方法
        stats = coordinator.get_stats()
        
        # 验证结果（应该安全处理这些情况）
        self.assertEqual(stats['total_memories'], 0)  # 所有非字典值都应该被视为0


if __name__ == '__main__':
    unittest.main()
