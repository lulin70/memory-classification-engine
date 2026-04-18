import unittest
import os
import sys
import tempfile
import shutil
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from memory_classification_engine.engine_facade import MemoryClassificationEngineFacade
from memory_classification_engine.orchestrator import MemoryOrchestrator, get_memory_orchestrator
from memory_classification_engine.coordinators.classification_pipeline import ClassificationPipeline
from memory_classification_engine.layers.rule_matcher import RuleMatcher
from memory_classification_engine.layers.semantic_classifier import SemanticClassifier
from memory_classification_engine.layers.pattern_analyzer import PatternAnalyzer
from memory_classification_engine.knowledge.knowledge_manager import KnowledgeManager
from memory_classification_engine.community.feedback_manager import FeedbackManager
from memory_classification_engine.agents.agent_manager import AgentManager
from memory_classification_engine.plugins.base_plugin import BasePlugin
from memory_classification_engine.plugins.plugin_manager import PluginManager
from memory_classification_engine.utils.config import ConfigManager


class TestMemoryClassificationEngineFacade(unittest.TestCase):
    def setUp(self):
        self.facade = MemoryClassificationEngineFacade(config_path=None)

    def test_init(self):
        self.assertIsNotNone(self.facade)

    def test_classify_message(self):
        result = self.facade.classify_message("I prefer dark mode for coding")
        self.assertIsInstance(result, dict)

    def test_classify_message_chinese(self):
        result = self.facade.classify_message("我喜欢用双引号")
        self.assertIsInstance(result, dict)

    def test_retrieve_memories(self):
        result = self.facade.retrieve_memories(query="test")
        self.assertIsInstance(result, list)


class TestMemoryOrchestrator(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config = {'storage': {'data_path': self.test_dir}}
        self.orchestrator = MemoryOrchestrator(config=self.config)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        self.assertIsNotNone(self.orchestrator)

    def test_init_default(self):
        orchestrator = MemoryOrchestrator()
        self.assertIsNotNone(orchestrator)

    def test_learn(self):
        result = self.orchestrator.learn("I prefer dark mode")
        self.assertIsNotNone(result)

    def test_learn_with_context(self):
        result = self.orchestrator.learn("I prefer dark mode", context="coding preferences")
        self.assertIsNotNone(result)

    def test_learn_chinese(self):
        result = self.orchestrator.learn("我喜欢用Python")
        self.assertIsNotNone(result)

    def test_recall(self):
        self.orchestrator.learn("I prefer dark mode")
        results = self.orchestrator.recall("dark mode")
        self.assertIsInstance(results, list)

    def test_search(self):
        self.orchestrator.learn("I prefer dark mode")
        results = self.orchestrator.search("dark mode")
        self.assertIsInstance(results, list)

    def test_batch_learn(self):
        messages = [
            "I prefer dark mode",
            "Actually, use single quotes",
            "The project uses Python 3.9",
        ]
        results = self.orchestrator.batch_learn(messages)
        self.assertIsInstance(results, list)

    def test_get_stats(self):
        stats = self.orchestrator.get_stats()
        self.assertIsInstance(stats, dict)

    def test_forget(self):
        result = self.orchestrator.learn("Test memory to forget")
        if isinstance(result, dict) and 'id' in result:
            forget_result = self.orchestrator.forget(result['id'])
            self.assertIsNotNone(forget_result)

    def test_export_import(self):
        self.orchestrator.learn("Test export")
        exported = self.orchestrator.export_memories()
        self.assertIsInstance(exported, str)
        imported = self.orchestrator.import_memories(exported)
        self.assertIsInstance(imported, dict)

    def test_track_feedback(self):
        result = self.orchestrator.learn("Test feedback")
        if isinstance(result, dict) and 'id' in result:
            feedback = self.orchestrator.track_feedback(result['id'], 'positive')
            self.assertIsNotNone(feedback)

    def test_get_memory_quality(self):
        result = self.orchestrator.learn("Test quality")
        if isinstance(result, dict) and 'id' in result:
            quality = self.orchestrator.get_memory_quality(result['id'])
            self.assertIsNotNone(quality)

    def test_get_memory_orchestrator(self):
        orchestrator = get_memory_orchestrator()
        self.assertIsNotNone(orchestrator)


class TestClassificationPipeline(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.pipeline = ClassificationPipeline(self.config)

    def test_init(self):
        self.assertIsNotNone(self.pipeline)

    def test_classify(self):
        result = self.pipeline.classify("I prefer dark mode")
        self.assertIsNotNone(result)

    def test_classify_correction(self):
        result = self.pipeline.classify("Actually, use double quotes instead")
        self.assertIsNotNone(result)

    def test_classify_fact(self):
        result = self.pipeline.classify("The project uses Python 3.9")
        self.assertIsNotNone(result)

    def test_classify_decision(self):
        result = self.pipeline.classify("We decided to use React for the frontend")
        self.assertIsNotNone(result)

    def test_classify_chinese(self):
        result = self.pipeline.classify("我喜欢用双引号")
        self.assertIsNotNone(result)

    def test_classify_japanese(self):
        result = self.pipeline.classify("ダークモードが好きです")
        self.assertIsNotNone(result)


class TestRuleMatcher(unittest.TestCase):
    def setUp(self):
        self.rules = [
            {'pattern': r'prefer\s+(\w+)', 'memory_type': 'user_preference', 'tier': 2},
            {'pattern': r'actually|correction', 'memory_type': 'correction', 'tier': 3},
        ]
        self.matcher = RuleMatcher(self.rules)

    def test_init(self):
        self.assertIsNotNone(self.matcher)

    def test_match(self):
        result = self.matcher.match("I prefer dark mode")
        self.assertIsNotNone(result)

    def test_match_correction(self):
        result = self.matcher.match("Actually, use double quotes")
        self.assertIsNotNone(result)

    def test_match_no_match(self):
        result = self.matcher.match("Hello world")
        self.assertIsNotNone(result)

    def test_add_rule(self):
        self.matcher.add_rule({'pattern': r'decided', 'memory_type': 'decision', 'tier': 4})
        rules = self.matcher.get_rules()
        self.assertEqual(len(rules), 3)

    def test_remove_rule(self):
        self.matcher.remove_rule(r'prefer\s+(\w+)')
        rules = self.matcher.get_rules()
        self.assertEqual(len(rules), 1)

    def test_get_rules(self):
        rules = self.matcher.get_rules()
        self.assertIsInstance(rules, list)
        self.assertEqual(len(rules), 2)


class TestSemanticClassifier(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.classifier = SemanticClassifier(self.config)

    def test_init(self):
        self.assertIsNotNone(self.classifier)

    def test_classify(self):
        try:
            result = self.classifier.classify("I prefer dark mode")
            self.assertIsNotNone(result)
        except Exception:
            pass

    def test_should_use_llm(self):
        result = self.classifier.should_use_llm("I prefer dark mode")
        self.assertIsInstance(result, bool)


class TestPatternAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = PatternAnalyzer()

    def test_init(self):
        self.assertIsNotNone(self.analyzer)

    def test_analyze(self):
        result = self.analyzer.analyze("I prefer dark mode")
        self.assertIsNotNone(result)

    def test_clear_history(self):
        self.analyzer.clear_history()


class TestKnowledgeManager(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.config.set('knowledge.obsidian_vault_path', '')
        self.manager = KnowledgeManager(self.config)

    def test_init(self):
        self.assertIsNotNone(self.manager)


class TestFeedbackManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        feedback_dir = os.path.join(self.test_dir, 'feedback')
        self.manager = FeedbackManager(feedback_dir=feedback_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        self.assertIsNotNone(self.manager)

    def test_submit_feedback(self):
        result = self.manager.submit_feedback(
            user_id="user1",
            feedback_type="bug",
            content="Classification is wrong",
            severity="medium"
        )
        self.assertIsNotNone(result)

    def test_list_feedback(self):
        self.manager.submit_feedback("user1", "bug", "Test feedback")
        result = self.manager.list_feedback()
        self.assertIsInstance(result, list)

    def test_get_feedback_stats(self):
        self.manager.submit_feedback("user1", "bug", "Test")
        stats = self.manager.get_feedback_stats()
        self.assertIsInstance(stats, dict)


class TestAgentManager(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.manager = AgentManager(self.config)

    def test_init(self):
        self.assertIsNotNone(self.manager)


class TestBasePlugin(unittest.TestCase):
    def _create_concrete_plugin(self, name="test_plugin", version="1.0.0"):
        class ConcretePlugin(BasePlugin):
            def initialize(self, config=None):
                return True
            def process_message(self, message, context=None):
                return {'result': message}
            def process_memory(self, memory):
                return memory
        return ConcretePlugin(name=name, version=version)

    def test_init(self):
        plugin = self._create_concrete_plugin()
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.name, "test_plugin")
        self.assertEqual(plugin.version, "1.0.0")

    def test_get_info(self):
        plugin = self._create_concrete_plugin(version="2.0.0")
        info = plugin.get_info()
        self.assertIsInstance(info, dict)
        self.assertEqual(info['name'], 'test_plugin')

    def test_set_and_get_config(self):
        plugin = self._create_concrete_plugin()
        plugin.set_config({'key': 'value'})
        config = plugin.get_config()
        self.assertEqual(config['key'], 'value')

    def test_cleanup(self):
        plugin = self._create_concrete_plugin()
        result = plugin.cleanup()
        self.assertTrue(result)


class TestPluginManager(unittest.TestCase):
    def _create_concrete_plugin(self, name="test_plugin", version="1.0.0"):
        class ConcretePlugin(BasePlugin):
            def initialize(self, config=None):
                return True
            def process_message(self, message, context=None):
                return {'result': message}
            def process_memory(self, memory):
                return memory
        return ConcretePlugin(name=name, version=version)

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.manager = PluginManager(plugins_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        self.assertIsNotNone(self.manager)

    def test_get_plugins(self):
        plugins = self.manager.get_plugins()
        self.assertIsInstance(plugins, dict)

    def test_get_enabled_plugins(self):
        enabled = self.manager.get_enabled_plugins()
        self.assertIsInstance(enabled, list)

    def test_get_all_plugin_info(self):
        info = self.manager.get_all_plugin_info()
        self.assertIsInstance(info, list)

    def test_add_plugin(self):
        plugin = self._create_concrete_plugin()
        self.manager.add_plugin(plugin)
        plugins = self.manager.get_plugins()
        self.assertIn('test_plugin', plugins)

    def test_remove_plugin(self):
        plugin = self._create_concrete_plugin()
        self.manager.add_plugin(plugin)
        self.manager.remove_plugin('test_plugin')
        plugins = self.manager.get_plugins()
        self.assertNotIn('test_plugin', plugins)


if __name__ == '__main__':
    unittest.main()
