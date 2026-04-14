#!/usr/bin/env python3
"""
Memory Classification Engine MCP Server

MCP (Model Context Protocol) server for Memory Classification Engine
Provides three core tools: classify_message, retrieve_memories, manage_forgetting
"""

import json
import yaml
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from memory_classification_engine import MemoryClassificationEngine

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mce-mcp-server')

# 全局引擎实例
engine = MemoryClassificationEngine()

class MCPRequestHandler(BaseHTTPRequestHandler):
    """MCP 请求处理器"""
    
    def do_POST(self):
        """处理 POST 请求"""
        try:
            # 读取请求体
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # 解析 JSON 请求
            request_data = json.loads(post_data.decode('utf-8'))
            
            # 处理工具调用
            if 'toolcall' in request_data:
                response = self.handle_tool_call(request_data['toolcall'])
            else:
                response = {
                    'error': 'Invalid request format: missing toolcall'
                }
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {
                'error': str(e)
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def handle_tool_call(self, toolcall):
        """处理工具调用"""
        tool_name = toolcall.get('name')
        params = toolcall.get('params', {})
        
        logger.info(f"Tool call: {tool_name} with params: {params}")
        
        if tool_name == 'classify_message':
            return self.handle_classify_message(params)
        elif tool_name == 'retrieve_memories':
            return self.handle_retrieve_memories(params)
        elif tool_name == 'search_memories':
            return self.handle_search_memories(params)
        elif tool_name == 'get_memory_timeline':
            return self.handle_get_memory_timeline(params)
        elif tool_name == 'get_memory_details':
            return self.handle_get_memory_details(params)
        elif tool_name == 'manage_forgetting':
            return self.handle_manage_forgetting(params)
        else:
            return {
                'error': f'Unknown tool: {tool_name}'
            }
    
    def handle_classify_message(self, params):
        """处理消息分类"""
        message = params.get('message')
        context = params.get('context')
        execution_context = params.get('execution_context')
        
        if not message:
            return {'error': 'Missing required parameter: message'}
        
        try:
            result = engine.process_message(
                message,
                context=context,
                execution_context=execution_context
            )
            
            return {
                'result': {
                    'matches': result.get('matches', []),
                    'summary': result.get('summary', ''),
                    'confidence': result.get('confidence', 0.0)
                }
            }
        except Exception as e:
            return {'error': f'Classification failed: {str(e)}'}
    
    def handle_retrieve_memories(self, params):
        """处理记忆检索"""
        query = params.get('query')
        memory_type = params.get('memory_type')
        limit = params.get('limit', 10)
        
        if not query:
            return {'error': 'Missing required parameter: query'}
        
        try:
            memories = engine.retrieve_memories(
                query=query,
                memory_type=memory_type,
                limit=limit
            )
            
            return {
                'result': {
                    'memories': memories,
                    'total': len(memories),
                    'query': query
                }
            }
        except Exception as e:
            return {'error': f'Retrieval failed: {str(e)}'}
    
    def handle_manage_forgetting(self, params):
        """处理遗忘管理"""
        memory_id = params.get('memory_id')
        action = params.get('action', 'decrease_weight')
        weight_adjustment = params.get('weight_adjustment', 0.1)
        
        if not memory_id:
            return {'error': 'Missing required parameter: memory_id'}
        
        try:
            result = engine.manage_forgetting(
                memory_id=memory_id,
                action=action,
                weight_adjustment=weight_adjustment
            )
            
            return {
                'result': {
                    'success': result.get('success', False),
                    'message': result.get('message', ''),
                    'memory_id': memory_id
                }
            }
        except Exception as e:
            return {'error': f'Forgetting management failed: {str(e)}'}
    
    def handle_search_memories(self, params):
        """处理记忆搜索（紧凑索引）"""
        query = params.get('query')
        memory_type = params.get('memory_type')
        limit = params.get('limit', 20)
        
        if not query:
            return {'error': 'Missing required parameter: query'}
        
        try:
            memories = engine.retrieve_memories(
                query=query,
                memory_type=memory_type,
                limit=limit
            )
            
            # 生成紧凑索引（~50 token/条）
            compact_index = []
            for memory in memories:
                index_entry = {
                    'id': memory.get('id'),
                    'memory_type': memory.get('memory_type'),
                    'summary': memory.get('content', '')[:100] + ('...' if len(memory.get('content', '')) > 100 else ''),
                    'created_at': memory.get('created_at'),
                    'confidence': memory.get('confidence', 0.0)
                }
                compact_index.append(index_entry)
            
            return {
                'result': {
                    'compact_index': compact_index,
                    'total': len(compact_index),
                    'query': query
                }
            }
        except Exception as e:
            return {'error': f'Search failed: {str(e)}'}
    
    def handle_get_memory_timeline(self, params):
        """处理记忆时间线（时间线上下文）"""
        memory_ids = params.get('memory_ids', [])
        
        if not memory_ids:
            return {'error': 'Missing required parameter: memory_ids'}
        
        try:
            timeline = []
            for memory_id in memory_ids:
                # 获取完整记忆
                memory = None
                for tier in [2, 3, 4]:
                    tier_memories = engine.storage_coordinator.retrieve_memories('', limit=100, tier=tier)
                    for mem in tier_memories:
                        if mem.get('id') == memory_id:
                            memory = mem
                            break
                    if memory:
                        break
                
                if memory:
                    # 生成时间线上下文（~200 token/条）
                    timeline_entry = {
                        'id': memory.get('id'),
                        'memory_type': memory.get('memory_type'),
                        'content': memory.get('content', ''),
                        'created_at': memory.get('created_at'),
                        'last_accessed': memory.get('last_accessed'),
                        'confidence': memory.get('confidence', 0.0),
                        'context': memory.get('context', '')
                    }
                    timeline.append(timeline_entry)
            
            return {
                'result': {
                    'timeline': timeline,
                    'total': len(timeline)
                }
            }
        except Exception as e:
            return {'error': f'Timeline retrieval failed: {str(e)}'}
    
    def handle_get_memory_details(self, params):
        """处理记忆详情（完整详情）"""
        memory_id = params.get('memory_id')
        
        if not memory_id:
            return {'error': 'Missing required parameter: memory_id'}
        
        try:
            # 获取完整记忆
            memory = None
            for tier in [2, 3, 4]:
                tier_memories = engine.storage_coordinator.retrieve_memories('', limit=100, tier=tier)
                for mem in tier_memories:
                    if mem.get('id') == memory_id:
                        memory = mem
                        break
                if memory:
                    break
            
            if memory:
                # 生成完整详情（~500 token/条）
                details = {
                    'id': memory.get('id'),
                    'memory_type': memory.get('memory_type'),
                    'content': memory.get('content', ''),
                    'created_at': memory.get('created_at'),
                    'updated_at': memory.get('updated_at'),
                    'last_accessed': memory.get('last_accessed'),
                    'access_count': memory.get('access_count', 0),
                    'confidence': memory.get('confidence', 0.0),
                    'source': memory.get('source', 'unknown'),
                    'context': memory.get('context', ''),
                    'status': memory.get('status', 'active'),
                    'weight': memory.get('weight', 1.0),
                    'tenant_id': memory.get('tenant_id'),
                    'language': memory.get('language', 'unknown'),
                    'sensitivity_level': memory.get('sensitivity_level', 0)
                }
                
                return {
                    'result': {
                        'details': details
                    }
                }
            else:
                return {'error': f'Memory {memory_id} not found'}
        except Exception as e:
            return {'error': f'Details retrieval failed: {str(e)}'}
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        logger.info(format % args)

def load_config(config_path='config.yaml'):
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, using default config")
        return {
            'server': {
                'host': '0.0.0.0',
                'port': 8080
            },
            'logging': {
                'level': 'INFO'
            }
        }

def main():
    """主函数"""
    # 加载配置
    config = load_config()
    
    # 配置服务器
    host = config['server'].get('host', '0.0.0.0')
    port = config['server'].get('port', 8080)
    
    # 创建服务器
    server = HTTPServer((host, port), MCPRequestHandler)
    logger.info(f"MCP Server started on http://{host}:{port}")
    logger.info("Available tools:")
    logger.info("  - classify_message: Classify a message into memory types")
    logger.info("  - retrieve_memories: Retrieve relevant memories")
    logger.info("  - search_memories: Search memories with compact index")
    logger.info("  - get_memory_timeline: Get memory timeline context")
    logger.info("  - get_memory_details: Get full memory details")
    logger.info("  - manage_forgetting: Manage memory forgetting process")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
