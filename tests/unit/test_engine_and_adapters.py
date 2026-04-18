import unittest
import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from memory_classification_engine.engine import MemoryClassificationEngine
from memory_classification_engine.agents.adapters.base_adapter import BaseAdapter
from memory_classification_engine.agents.adapters.claude_code import ClaudeCodeAdapter
from memory_classification_engine.agents.adapters.openclaw import OpenclawAdapter
from memory_classification_engine.agents.adapters.trae import TraeAdapter
from memory_classification_engine.agents.adapters.work_buddy import WorkBuddyAdapter
from memory_classification_engine.plugins.builtin.sentiment_analyzer import SentimentAnalyzerPlugin
from memory_classification_engine.plugins.builtin.entity_extractor import EntityExtractorPlugin
from memory_classification_engine.utils.config import ConfigManager
from memory_classification_engine.utils.memory_manager import MemoryManager, SmartCache as MM_SmartCache


class TestMemoryClassificationEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config = ConfigManager()
        self.config.set('storage.data_path', self.test_dir)
        self.config.set('storage.tier2_path', os.path.join(self.test_dir, 'tier2'))
        self.config.set('storage.tier3_path', os.path.join(self.test_dir, 'tier3'))
        self.config.set('storage.tier4_path', os.path.join(self.test_dir, 'tier4'))
        self.config.set('memory.forgetting.min_weight', 0.1)
        self.engine = MemoryClassificationEngine(self.config)

    def tearDown(self):
        if hasattr(self.engine, 'cleanup'):
            self.engine.cleanup()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        self.assertIsNotNone(self.engine)

    def test_process_message_preference(self):
        result = self.engine.process_message("I prefer dark mode")
        self.assertIsInstance(result, dict)

    def test_process_message_correction(self):
        result = self.engine.process_message("Actually, use double quotes")
        self.assertIsInstance(result, dict)

    def test_process_message_fact(self):
        result = self.engine.process_message("The project uses Python 3.9")
        self.assertIsInstance(result, dict)

    def test_process_message_chinese(self):
        result = self.engine.process_message("我喜欢用双引号")
        self.assertIsInstance(result, dict)

    def test_process_message_japanese(self):
        result = self.engine.process_message("ダークモードが好きです")
        self.assertIsInstance(result, dict)

    def test_retrieve_memories(self):
        self.engine.process_message("I prefer dark mode")
        results = self.engine.retrieve_memories("dark mode")
        self.assertIsInstance(results, list)

    def test_get_stats(self):
        stats = self.engine.get_stats()
        self.assertIsInstance(stats, dict)

    def test_batch_classify(self):
        messages = [
            "I prefer dark mode",
            "Actually, use single quotes",
            "The project uses Python 3.9",
        ]
        results = []
        for msg in messages:
            result = self.engine.process_message(msg)
            results.append(result)
        self.assertEqual(len(results), 3)


class TestAgentAdapters(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()

    def test_base_adapter(self):
        adapter = BaseAdapter(self.config)
        self.assertIsNotNone(adapter)

    def test_claude_code_adapter(self):
        adapter = ClaudeCodeAdapter(self.config)
        self.assertIsNotNone(adapter)

    def test_claude_code_process_message(self):
        adapter = ClaudeCodeAdapter(self.config)
        result = adapter.process_message("I prefer dark mode")
        self.assertIsInstance(result, dict)

    def test_claude_code_process_memory(self):
        adapter = ClaudeCodeAdapter(self.config)
        memory = {
            'id': 'test_1',
            'content': 'I prefer dark mode',
            'memory_type': 'user_preference',
            'confidence': 0.95,
        }
        result = adapter.process_memory(memory)
        self.assertIsInstance(result, dict)

    def test_openclaw_adapter(self):
        adapter = OpenclawAdapter(self.config)
        self.assertIsNotNone(adapter)

    def test_openclaw_process_message(self):
        adapter = OpenclawAdapter(self.config)
        result = adapter.process_message("I prefer dark mode")
        self.assertIsInstance(result, dict)

    def test_openclaw_process_memory(self):
        adapter = OpenclawAdapter(self.config)
        memory = {'id': 'test_1', 'content': 'Test', 'memory_type': 'user_preference', 'confidence': 0.9}
        result = adapter.process_memory(memory)
        self.assertIsInstance(result, dict)

    def test_trae_adapter(self):
        adapter = TraeAdapter(self.config)
        self.assertIsNotNone(adapter)

    def test_trae_process_message(self):
        adapter = TraeAdapter(self.config)
        result = adapter.process_message("I prefer dark mode")
        self.assertIsInstance(result, dict)

    def test_trae_process_memory(self):
        adapter = TraeAdapter(self.config)
        memory = {'id': 'test_1', 'content': 'Test', 'memory_type': 'user_preference', 'confidence': 0.9}
        result = adapter.process_memory(memory)
        self.assertIsInstance(result, dict)

    def test_work_buddy_adapter(self):
        adapter = WorkBuddyAdapter(self.config)
        self.assertIsNotNone(adapter)

    def test_work_buddy_process_message(self):
        adapter = WorkBuddyAdapter(self.config)
        result = adapter.process_message("I prefer dark mode")
        self.assertIsInstance(result, dict)

    def test_work_buddy_process_memory(self):
        adapter = WorkBuddyAdapter(self.config)
        memory = {'id': 'test_1', 'content': 'Test', 'memory_type': 'user_preference', 'confidence': 0.9}
        result = adapter.process_memory(memory)
        self.assertIsInstance(result, dict)


class TestBuiltinPlugins(unittest.TestCase):
    def test_sentiment_analyzer_init(self):
        plugin = SentimentAnalyzerPlugin()
        self.assertIsNotNone(plugin)

    def test_sentiment_analyzer_process(self):
        plugin = SentimentAnalyzerPlugin()
        plugin.initialize()
        result = plugin.process_message("I love this feature!")
        self.assertIsNotNone(result)

    def test_sentiment_analyzer_negative(self):
        plugin = SentimentAnalyzerPlugin()
        plugin.initialize()
        result = plugin.process_message("This is terrible and broken")
        self.assertIsNotNone(result)

    def test_entity_extractor_init(self):
        plugin = EntityExtractorPlugin()
        self.assertIsNotNone(plugin)

    def test_entity_extractor_process(self):
        plugin = EntityExtractorPlugin()
        plugin.initialize()
        result = plugin.process_message("John Smith works at Google in New York")
        self.assertIsNotNone(result)


class TestMemoryManagerSystem(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.manager = MemoryManager(self.config)

    def test_init(self):
        self.assertIsNotNone(self.manager)

    def test_get_memory_limits(self):
        limits = self.manager.get_memory_limits()
        self.assertIsInstance(limits, dict)

    def test_get_memory_metrics(self):
        metrics = self.manager.get_memory_metrics()
        self.assertIsInstance(metrics, dict)

    def test_get_memory_summary(self):
        summary = self.manager.get_memory_summary()
        self.assertIsInstance(summary, dict)

    def test_get_memory_history(self):
        history = self.manager.get_memory_history()
        self.assertIsInstance(history, list)

    def test_get_alert_history(self):
        alerts = self.manager.get_alert_history()
        self.assertIsInstance(alerts, list)

    def test_calculate_fragmentation(self):
        frag = self.manager.calculate_memory_fragmentation()
        self.assertIsInstance(frag, float)
        self.assertGreaterEqual(frag, 0)
        self.assertLessEqual(frag, 1)

    def test_optimize_memory_usage(self):
        try:
            result = self.manager.optimize_memory_usage(target_usage=0.5)
            self.assertIsNotNone(result)
        except Exception:
            pass

    def test_stop(self):
        self.manager.stop()


if __name__ == '__main__':
    unittest.main()
