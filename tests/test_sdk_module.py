#!/usr/bin/env python3
"""SDK module tests for Memory Classification Engine."""

import pytest
import requests
from unittest.mock import Mock, patch
from memory_classification_engine.sdk.client import MemoryClassificationSDK


class TestSDKClient:
    """SDK客户端测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.sdk = MemoryClassificationSDK(api_key="test-api-key")
    
    @patch('requests.get')
    def test_retrieve_memories(self, mock_get):
        """测试记忆检索"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "memories": [
                {"id": "1", "content": "Test memory", "memory_type": "fact_declaration"}
            ],
            "total": 1
        }
        mock_get.return_value = mock_response
        
        # 测试基本检索
        result = self.sdk.retrieve_memories(query="test", limit=5)
        assert "memories" in result
        assert len(result["memories"]) == 1
        
        # 测试带过滤条件的检索
        result = self.sdk.retrieve_memories(
            query="test",
            limit=10,
            tenant_id="tenant1",
            memory_type="fact_declaration",
            tier=2
        )
        assert "memories" in result
    
    @patch('requests.post')
    def test_process_message(self, mock_post):
        """测试消息处理"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "matches": [
                {"memory_type": "fact_declaration", "content": "Test content"}
            ]
        }
        mock_post.return_value = mock_response
        
        # 测试消息处理
        result = self.sdk.process_message("This is a test message")
        assert "matches" in result
        assert len(result["matches"]) == 1
        
        # 测试带上下文的消息处理
        context = {"user_id": "user1", "tenant_id": "tenant1"}
        result = self.sdk.process_message("This is a test message", context=context)
        assert "matches" in result
    
    @patch('requests.get')
    def test_get_memory(self, mock_get):
        """测试获取单个记忆"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "id": "1",
            "content": "Test memory",
            "memory_type": "fact_declaration",
            "created_at": "2026-04-13T12:00:00Z"
        }
        mock_get.return_value = mock_response
        
        # 测试获取记忆
        result = self.sdk.get_memory("1")
        assert result["id"] == "1"
        assert result["content"] == "Test memory"
    
    @patch('requests.put')
    def test_update_memory(self, mock_put):
        """测试更新记忆"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "id": "1",
            "content": "Updated memory",
            "memory_type": "fact_declaration"
        }
        mock_put.return_value = mock_response
        
        # 测试更新记忆
        update_data = {"content": "Updated memory"}
        result = self.sdk.update_memory("1", update_data)
        assert result["content"] == "Updated memory"
    
    @patch('requests.delete')
    def test_delete_memory(self, mock_delete):
        """测试删除记忆"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {"success": True, "message": "Memory deleted"}
        mock_delete.return_value = mock_response
        
        # 测试删除记忆
        result = self.sdk.delete_memory("1")
        assert result["success"] is True
    
    @patch('requests.get')
    def test_get_stats(self, mock_get):
        """测试获取系统统计"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "total_memories": 100,
            "memory_types": {"fact_declaration": 50, "event": 30, "task_pattern": 20},
            "tier_distribution": {"tier1": 20, "tier2": 30, "tier3": 40, "tier4": 10}
        }
        mock_get.return_value = mock_response
        
        # 测试获取统计
        result = self.sdk.get_stats()
        assert "total_memories" in result
        assert result["total_memories"] == 100
    
    @patch('requests.get')
    def test_export_memories(self, mock_get):
        """测试导出记忆"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.content = b'{"memories": []}'
        mock_get.return_value = mock_response
        
        # 测试导出记忆
        result = self.sdk.export_memories(format="json")
        assert isinstance(result, bytes)
    
    @patch('requests.post')
    def test_process_with_agent(self, mock_post):
        """测试代理处理"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "agent": "test_agent",
            "result": "Agent processing result"
        }
        mock_post.return_value = mock_response
        
        # 测试代理处理
        result = self.sdk.process_with_agent("test_agent", "Test message")
        assert result["agent"] == "test_agent"


class TestSDKTenantManagement:
    """SDK租户管理测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.sdk = MemoryClassificationSDK(api_key="test-api-key")
    
    @patch('requests.post')
    def test_create_tenant(self, mock_post):
        """测试创建租户"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "tenant_id": "tenant1",
            "name": "Test Tenant",
            "tenant_type": "business"
        }
        mock_post.return_value = mock_response
        
        # 测试创建租户
        result = self.sdk.create_tenant(
            tenant_id="tenant1",
            name="Test Tenant",
            tenant_type="business",
            user_id="user1"
        )
        assert result["tenant_id"] == "tenant1"
    
    @patch('requests.get')
    def test_get_tenant(self, mock_get):
        """测试获取租户"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "tenant_id": "tenant1",
            "name": "Test Tenant",
            "tenant_type": "business"
        }
        mock_get.return_value = mock_response
        
        # 测试获取租户
        result = self.sdk.get_tenant("tenant1")
        assert result["tenant_id"] == "tenant1"
    
    @patch('requests.get')
    def test_list_tenants(self, mock_get):
        """测试列出租户"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "tenants": [
                {"tenant_id": "tenant1", "name": "Test Tenant 1"},
                {"tenant_id": "tenant2", "name": "Test Tenant 2"}
            ],
            "total": 2
        }
        mock_get.return_value = mock_response
        
        # 测试列出租户
        result = self.sdk.list_tenants()
        assert "tenants" in result
        assert len(result["tenants"]) == 2
    
    @patch('requests.put')
    def test_update_tenant(self, mock_put):
        """测试更新租户"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "tenant_id": "tenant1",
            "name": "Updated Tenant",
            "tenant_type": "business"
        }
        mock_put.return_value = mock_response
        
        # 测试更新租户
        update_data = {"name": "Updated Tenant"}
        result = self.sdk.update_tenant("tenant1", update_data)
        assert result["name"] == "Updated Tenant"
    
    @patch('requests.delete')
    def test_delete_tenant(self, mock_delete):
        """测试删除租户"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {"success": True, "message": "Tenant deleted"}
        mock_delete.return_value = mock_response
        
        # 测试删除租户
        result = self.sdk.delete_tenant("tenant1")
        assert result["success"] is True


class TestSDKFeedbackManagement:
    """SDK反馈管理测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.sdk = MemoryClassificationSDK(api_key="test-api-key")
    
    @patch('requests.post')
    def test_submit_feedback(self, mock_post):
        """测试提交反馈"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "feedback_id": "f1",
            "user_id": "user1",
            "feedback_type": "bug",
            "status": "open"
        }
        mock_post.return_value = mock_response
        
        # 测试提交反馈
        result = self.sdk.submit_feedback(
            user_id="user1",
            feedback_type="bug",
            content="Test bug report",
            severity="high"
        )
        assert result["feedback_id"] == "f1"
    
    @patch('requests.get')
    def test_get_feedback(self, mock_get):
        """测试获取反馈"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "feedback_id": "f1",
            "user_id": "user1",
            "feedback_type": "bug",
            "content": "Test bug report",
            "status": "open"
        }
        mock_get.return_value = mock_response
        
        # 测试获取反馈
        result = self.sdk.get_feedback("f1")
        assert result["feedback_id"] == "f1"
    
    @patch('requests.get')
    def test_list_feedback(self, mock_get):
        """测试列出反馈"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = [
            {"feedback_id": "f1", "user_id": "user1", "status": "open"},
            {"feedback_id": "f2", "user_id": "user2", "status": "resolved"}
        ]
        mock_get.return_value = mock_response
        
        # 测试列出反馈
        result = self.sdk.list_feedback(status="open", limit=10)
        assert isinstance(result, list)
        assert len(result) == 2
    
    @patch('requests.put')
    def test_update_feedback_status(self, mock_put):
        """测试更新反馈状态"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "feedback_id": "f1",
            "status": "in_progress",
            "updated_by": "user2"
        }
        mock_put.return_value = mock_response
        
        # 测试更新反馈状态
        result = self.sdk.update_feedback_status(
            feedback_id="f1",
            status="in_progress",
            user_id="user2",
            comment="Working on it"
        )
        assert result["status"] == "in_progress"
    
    @patch('requests.post')
    def test_reply_to_feedback(self, mock_post):
        """测试回复反馈"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "feedback_id": "f1",
            "reply_id": "r1",
            "user_id": "user2",
            "content": "Test reply"
        }
        mock_post.return_value = mock_response
        
        # 测试回复反馈
        result = self.sdk.reply_to_feedback(
            feedback_id="f1",
            user_id="user2",
            content="Test reply"
        )
        assert result["reply_id"] == "r1"


class TestSDKErrorHandling:
    """SDK错误处理测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.sdk = MemoryClassificationSDK(api_key="test-api-key")
    
    @patch('requests.get')
    def test_network_timeout(self, mock_get):
        """测试网络超时异常"""
        # 模拟网络超时
        mock_get.side_effect = requests.exceptions.RequestException("Connection timed out")
        
        # 测试异常处理
        with pytest.raises(Exception, match="API request failed"):
            self.sdk.get_stats()
    
    @patch('requests.post')
    def test_authentication_failure(self, mock_post):
        """测试认证失败异常"""
        # 模拟认证失败
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("401 Client Error: Unauthorized")
        mock_post.return_value = mock_response
        
        # 测试异常处理
        with pytest.raises(Exception, match="API request failed"):
            self.sdk.process_message("Test message")
    
    @patch('requests.get')
    def test_rate_limiting(self, mock_get):
        """测试速率限制异常"""
        # 模拟速率限制
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("429 Client Error: Too Many Requests")
        mock_get.return_value = mock_response
        
        # 测试异常处理
        with pytest.raises(Exception, match="API request failed"):
            self.sdk.get_stats()


class TestSDKQuickStart:
    """SDK快速开始示例测试"""
    
    def test_quick_start_example(self):
        """测试快速开始示例可运行"""
        # 测试 SDK 初始化
        sdk = MemoryClassificationSDK(api_key="test-api-key")
        assert sdk is not None
        assert sdk.api_key == "test-api-key"
        assert sdk.base_url == "http://localhost:8000/api/v1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])