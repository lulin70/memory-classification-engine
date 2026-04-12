"""API server for Memory Classification Engine."""

import json
import asyncio
import logging
from typing import Dict, Any, Optional
from aiohttp import web
import socketio

from memory_classification_engine import MemoryClassificationEngine
from memory_classification_engine.utils.logger import logger
from memory_classification_engine.utils.security import SecurityManager
from memory_classification_engine.community.feedback_manager import feedback_manager


class APIServer:
    """API server for Memory Classification Engine."""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8000, config_path: str = None):
        """Initialize the API server.
        
        Args:
            host: Host to bind to.
            port: Port to bind to.
            config_path: Path to configuration file.
        """
        self.host = host
        self.port = port
        self.config_path = config_path
        
        # Comment in Chinese removed
        self.engine = MemoryClassificationEngine(config_path)
        
        # Comment in Chinese removedr
        self.security_manager = SecurityManager()
        
        # Comment in Chinese removedtion
        self.app = web.Application()
        self.setup_routes()
        
        # Comment in Chinese removedr
        self.sio = socketio.AsyncServer(cors_allowed_origins='*')
        self.sio_app = socketio.ASGIApp(self.sio, self.app)
        self.setup_socketio_events()
    
    def setup_routes(self):
        """Set up API routes."""
        # Comment in Chinese removedck
        self.app.add_routes([web.get('/health', self.health_check)])
        
        # Comment in Chinese removedndpoints
        self.app.add_routes([
            web.post('/api/memory/process', self.process_message),
            web.get('/api/memory/retrieve', self.retrieve_memories),
            web.post('/api/memory/manage', self.manage_memory),
            web.get('/api/memory/export', self.export_memories),
            web.post('/api/memory/import', self.import_memories),
            web.get('/api/memory/stats', self.get_stats)
        ])
        
        # Comment in Chinese removedndpoints
        self.app.add_routes([
            web.post('/api/tenant/create', self.create_tenant),
            web.get('/api/tenant/{tenant_id}', self.get_tenant),
            web.get('/api/tenant', self.list_tenants),
            web.delete('/api/tenant/{tenant_id}', self.delete_tenant),
            web.put('/api/tenant/{tenant_id}', self.update_tenant),
            web.post('/api/tenant/{tenant_id}/role', self.add_tenant_role),
            web.get('/api/tenant/{tenant_id}/permission', self.check_tenant_permission),
            web.get('/api/tenant/{tenant_id}/memories', self.get_tenant_memories)
        ])
        
        # Comment in Chinese removedndpoints
        self.app.add_routes([
            web.post('/api/auth/token', self.generate_token),
            web.post('/api/auth/verify', self.verify_token),
            web.post('/api/auth/key', self.generate_api_key)
        ])
        
        # Comment in Chinese removedndpoints
        self.app.add_routes([
            web.post('/api/community/feedback', self.submit_feedback),
            web.get('/api/community/feedback/{feedback_id}', self.get_feedback),
            web.get('/api/community/feedback', self.list_feedback),
            web.put('/api/community/feedback/{feedback_id}/status', self.update_feedback_status),
            web.post('/api/community/feedback/{feedback_id}/reply', self.reply_to_feedback),
            web.get('/api/community/feedback/stats', self.get_feedback_stats),
            web.get('/api/community/feedback/export', self.export_feedback)
        ])
    
    def setup_socketio_events(self):
        """Set up Socket.IO events."""
        @self.sio.event
        async def connect(sid, environ):
            logger.info(f"Client connected: {sid}")
        
        @self.sio.event
        async def disconnect(sid):
            logger.info(f"Client disconnected: {sid}")
        
        @self.sio.event
        async def process_message(sid, data):
            try:
                message = data.get('message')
                context = data.get('context', {})
                result = self.engine.process_message(message, context)
                await self.sio.emit('process_message_response', result, to=sid)
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
                await self.sio.emit('error', {'error': str(e)}, to=sid)
        
        @self.sio.event
        async def retrieve_memories(sid, data):
            try:
                query = data.get('query')
                limit = data.get('limit', 5)
                tenant_id = data.get('tenant_id')
                result = self.engine.retrieve_memories(query, limit, tenant_id)
                await self.sio.emit('retrieve_memories_response', result, to=sid)
            except Exception as e:
                logger.error(f"Error retrieving memories: {e}", exc_info=True)
                await self.sio.emit('error', {'error': str(e)}, to=sid)
    
    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        return web.json_response({'status': 'healthy', 'version': '1.0.0'})
    
    async def process_message(self, request: web.Request) -> web.Response:
        """Process message endpoint."""
        try:
            data = await request.json()
            message = data.get('message')
            context = data.get('context', {})
            
            if not message:
                return web.json_response({'error': 'Message is required'}, status=400)
            
            result = self.engine.process_message(message, context)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def retrieve_memories(self, request: web.Request) -> web.Response:
        """Retrieve memories endpoint."""
        try:
            query = request.query.get('query')
            limit = int(request.query.get('limit', 5))
            tenant_id = request.query.get('tenant_id')
            
            result = self.engine.retrieve_memories(query, limit, tenant_id)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def manage_memory(self, request: web.Request) -> web.Response:
        """Manage memory endpoint."""
        try:
            data = await request.json()
            action = data.get('action')
            memory_id = data.get('memory_id')
            memory_data = data.get('data')
            
            if not action or not memory_id:
                return web.json_response({'error': 'Action and memory_id are required'}, status=400)
            
            result = self.engine.manage_memory(action, memory_id, memory_data)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error managing memory: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def export_memories(self, request: web.Request) -> web.Response:
        """Export memories endpoint."""
        try:
            format = request.query.get('format', 'json')
            result = self.engine.export_memories(format)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error exporting memories: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def import_memories(self, request: web.Request) -> web.Response:
        """Import memories endpoint."""
        try:
            data = await request.json()
            format = data.get('format', 'json')
            memories = data.get('data')
            
            if not memories:
                return web.json_response({'error': 'Memories data is required'}, status=400)
            
            result = self.engine.import_memories(memories, format)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error importing memories: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_stats(self, request: web.Request) -> web.Response:
        """Get stats endpoint."""
        try:
            result = self.engine.get_stats()
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error getting stats: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def create_tenant(self, request: web.Request) -> web.Response:
        """Create tenant endpoint."""
        try:
            data = await request.json()
            tenant_id = data.get('tenant_id')
            name = data.get('name')
            tenant_type = data.get('type')
            kwargs = data.get('kwargs', {})
            
            if not tenant_id or not name or not tenant_type:
                return web.json_response({'error': 'tenant_id, name, and type are required'}, status=400)
            
            result = self.engine.create_tenant(tenant_id, name, tenant_type, **kwargs)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error creating tenant: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_tenant(self, request: web.Request) -> web.Response:
        """Get tenant endpoint."""
        try:
            tenant_id = request.match_info.get('tenant_id')
            result = self.engine.get_tenant(tenant_id)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error getting tenant: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def list_tenants(self, request: web.Request) -> web.Response:
        """List tenants endpoint."""
        try:
            result = self.engine.list_tenants()
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error listing tenants: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def delete_tenant(self, request: web.Request) -> web.Response:
        """Delete tenant endpoint."""
        try:
            tenant_id = request.match_info.get('tenant_id')
            result = self.engine.delete_tenant(tenant_id)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error deleting tenant: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def update_tenant(self, request: web.Request) -> web.Response:
        """Update tenant endpoint."""
        try:
            tenant_id = request.match_info.get('tenant_id')
            data = await request.json()
            result = self.engine.update_tenant(tenant_id, data)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error updating tenant: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def add_tenant_role(self, request: web.Request) -> web.Response:
        """Add tenant role endpoint."""
        try:
            tenant_id = request.match_info.get('tenant_id')
            data = await request.json()
            role_name = data.get('role_name')
            permissions = data.get('permissions', [])
            
            if not role_name:
                return web.json_response({'error': 'role_name is required'}, status=400)
            
            result = self.engine.add_tenant_role(tenant_id, role_name, permissions)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error adding tenant role: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def check_tenant_permission(self, request: web.Request) -> web.Response:
        """Check tenant permission endpoint."""
        try:
            tenant_id = request.match_info.get('tenant_id')
            role_name = request.query.get('role_name')
            permission = request.query.get('permission')
            
            if not role_name or not permission:
                return web.json_response({'error': 'role_name and permission are required'}, status=400)
            
            result = self.engine.check_tenant_permission(tenant_id, role_name, permission)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error checking tenant permission: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_tenant_memories(self, request: web.Request) -> web.Response:
        """Get tenant memories endpoint."""
        try:
            tenant_id = request.match_info.get('tenant_id')
            limit = int(request.query.get('limit', 10))
            result = self.engine.get_tenant_memories(tenant_id, limit)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error getting tenant memories: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def generate_token(self, request: web.Request) -> web.Response:
        """Generate token endpoint."""
        try:
            data = await request.json()
            user_id = data.get('user_id')
            
            if not user_id:
                return web.json_response({'error': 'user_id is required'}, status=400)
            
            token = self.security_manager.generate_token(user_id)
            return web.json_response({'token': token})
        except Exception as e:
            logger.error(f"Error generating token: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def verify_token(self, request: web.Request) -> web.Response:
        """Verify token endpoint."""
        try:
            data = await request.json()
            token = data.get('token')
            
            if not token:
                return web.json_response({'error': 'token is required'}, status=400)
            
            valid, user_id = self.security_manager.verify_token(token)
            return web.json_response({'valid': valid, 'user_id': user_id})
        except Exception as e:
            logger.error(f"Error verifying token: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def generate_api_key(self, request: web.Request) -> web.Response:
        """Generate API key endpoint."""
        try:
            data = await request.json()
            user_id = data.get('user_id')
            
            if not user_id:
                return web.json_response({'error': 'user_id is required'}, status=400)
            
            api_key = self.security_manager.generate_api_key(user_id)
            return web.json_response({'api_key': api_key})
        except Exception as e:
            logger.error(f"Error generating API key: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def submit_feedback(self, request: web.Request) -> web.Response:
        """Submit feedback endpoint."""
        try:
            data = await request.json()
            user_id = data.get('user_id')
            feedback_type = data.get('feedback_type')
            content = data.get('content')
            severity = data.get('severity', 'medium')
            metadata = data.get('metadata', {})
            
            if not user_id or not feedback_type or not content:
                return web.json_response({'error': 'user_id, feedback_type, and content are required'}, status=400)
            
            result = feedback_manager.submit_feedback(user_id, feedback_type, content, severity, metadata)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_feedback(self, request: web.Request) -> web.Response:
        """Get feedback endpoint."""
        try:
            feedback_id = request.match_info.get('feedback_id')
            feedback = feedback_manager.get_feedback(feedback_id)
            
            if not feedback:
                return web.json_response({'error': 'Feedback not found'}, status=404)
            
            return web.json_response(feedback)
        except Exception as e:
            logger.error(f"Error getting feedback: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def list_feedback(self, request: web.Request) -> web.Response:
        """List feedback endpoint."""
        try:
            status = request.query.get('status')
            feedback_type = request.query.get('feedback_type')
            user_id = request.query.get('user_id')
            limit = int(request.query.get('limit', 100))
            
            feedback = feedback_manager.list_feedback(status, feedback_type, user_id, limit)
            return web.json_response(feedback)
        except Exception as e:
            logger.error(f"Error listing feedback: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def update_feedback_status(self, request: web.Request) -> web.Response:
        """Update feedback status endpoint."""
        try:
            feedback_id = request.match_info.get('feedback_id')
            data = await request.json()
            status = data.get('status')
            user_id = data.get('user_id')
            comment = data.get('comment')
            
            if not status or not user_id:
                return web.json_response({'error': 'status and user_id are required'}, status=400)
            
            result = feedback_manager.update_feedback_status(feedback_id, status, user_id, comment)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error updating feedback status: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def reply_to_feedback(self, request: web.Request) -> web.Response:
        """Reply to feedback endpoint."""
        try:
            feedback_id = request.match_info.get('feedback_id')
            data = await request.json()
            user_id = data.get('user_id')
            content = data.get('content')
            
            if not user_id or not content:
                return web.json_response({'error': 'user_id and content are required'}, status=400)
            
            result = feedback_manager.reply_to_feedback(feedback_id, user_id, content)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error replying to feedback: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_feedback_stats(self, request: web.Request) -> web.Response:
        """Get feedback stats endpoint."""
        try:
            stats = feedback_manager.get_feedback_stats()
            return web.json_response(stats)
        except Exception as e:
            logger.error(f"Error getting feedback stats: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def export_feedback(self, request: web.Request) -> web.Response:
        """Export feedback endpoint."""
        try:
            filename = request.query.get('filename', 'feedback_export.json')
            result = feedback_manager.export_feedback(filename)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error exporting feedback: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def start(self):
        """Start the API server."""
        runner = web.AppRunner(self.sio_app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        logger.info(f"API server started on http://{self.host}:{self.port}")
    
    async def stop(self):
        """Stop the API server."""
        # Comment in Chinese removedp
        logger.info("API server stopped")


def main():
    """Main function to start the API server."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Classification Engine API Server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--config', type=str, default=None, help='Path to configuration file')
    
    args = parser.parse_args()
    
    server = APIServer(args.host, args.port, args.config)
    
    async def run_server():
        await server.start()
        # Comment in Chinese removednning
        while True:
            await asyncio.sleep(3600)
    
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Shutting down API server...")


if __name__ == '__main__':
    main()
