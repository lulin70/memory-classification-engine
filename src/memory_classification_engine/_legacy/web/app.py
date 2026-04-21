from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, g
from memory_classification_engine import MemoryClassificationEngine
from memory_classification_engine.utils.logger import logger
from memory_classification_engine.utils.security import security_manager, authorization_manager
import time
import json
import threading
from typing import Dict, List, Optional

app = Flask(__name__)

# Comment in Chinese removed
engine = MemoryClassificationEngine()

# Comment in Chinese removedly)
VALID_API_KEYS = {
    'test-api-key': 'user',
    'admin-api-key': 'admin'
}

# Comment in Chinese removed limiting
rate_limit = {
    'window': 60,  # Comment in Chinese removedconds
    'limit': 100,  # Comment in Chinese removedr window
    'requests': {}
}

# Comment in Chinese removed limiting
rate_limit_lock = threading.RLock()

# Comment in Chinese removedck
def check_auth():
    """Check authentication."""
    # Comment in Chinese removedy
    api_key = request.headers.get('X-API-Key')
    if api_key and api_key in VALID_API_KEYS:
        g.role = VALID_API_KEYS[api_key]
        return True
    
    # Comment in Chinese removedn
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        payload = security_manager.verify_token(token)
        if payload:
            g.role = payload.get('role', 'user')
            return True
    
    # Comment in Chinese removedtion
    public_endpoints = [
        '/api/health',
        '/api/version'
    ]
    
    if request.path in public_endpoints:
        g.role = 'guest'
        return True
    
    return False

# Comment in Chinese removedpport
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

# Comment in Chinese removedtor
def rate_limit_check():
    """Check rate limit for the current request."""
    client_ip = request.remote_addr
    current_time = time.time()
    
    with rate_limit_lock:
        # Comment in Chinese removedsts
        if client_ip in rate_limit['requests']:
            rate_limit['requests'][client_ip] = [t for t in rate_limit['requests'][client_ip] if current_time - t < rate_limit['window']]
        else:
            rate_limit['requests'][client_ip] = []
        
        # Comment in Chinese removedd
        if len(rate_limit['requests'][client_ip]) >= rate_limit['limit']:
            return make_response(jsonify({'error': 'Rate limit exceeded'}), 429)
        
        # Comment in Chinese removedst
        rate_limit['requests'][client_ip].append(current_time)
    
    return None

# Comment in Chinese removed limiting
@app.before_request
def before_request():
    """Before request handler for rate limiting and authentication."""
    # Comment in Chinese removeds
    if not request.path.startswith('/api/'):
        return
    
    # Comment in Chinese removedsts
    if request.method == 'OPTIONS':
        return
    
    # Comment in Chinese removed limit
    rate_limit_response = rate_limit_check()
    if rate_limit_response:
        return rate_limit_response
    
    # Comment in Chinese removeds)
    public_endpoints = [
        '/api/health',
        '/api/version'
    ]
    
    if request.path not in public_endpoints:
        if not check_auth():
            return make_response(jsonify({'error': 'Unauthorized'}), 401)

@app.route('/')
def index():
    """Home page."""
    stats = engine.get_stats()
    return render_template('index.html', stats=stats)

@app.route('/memories')
def memories():
    """List all memories."""
    query = request.args.get('query', '')
    limit = int(request.args.get('limit', 20))
    memories = engine.retrieve_memories(query, limit)
    return render_template('memories.html', memories=memories, query=query, limit=limit)

@app.route('/memory/<memory_id>')
def memory_detail(memory_id):
    """Memory detail page."""
    result = engine.manage_memory('view', memory_id)
    if not result['success']:
        return redirect(url_for('memories'))
    memory = result['memory']
    return render_template('memory_detail.html', memory=memory)

@app.route('/memory/<memory_id>/edit', methods=['GET', 'POST'])
def edit_memory(memory_id):
    """Edit memory page."""
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            result = engine.manage_memory('edit', memory_id, {'content': content})
            if result['success']:
                return redirect(url_for('memory_detail', memory_id=memory_id))
    
    result = engine.manage_memory('view', memory_id)
    if not result['success']:
        return redirect(url_for('memories'))
    memory = result['memory']
    return render_template('edit_memory.html', memory=memory)

@app.route('/memory/<memory_id>/delete')
def delete_memory(memory_id):
    """Delete memory."""
    engine.manage_memory('delete', memory_id)
    return redirect(url_for('memories'))

@app.route('/process', methods=['POST'])
def process_message():
    """Process a message."""
    message = request.form.get('message')
    if message:
        result = engine.process_message(message)
        return redirect(url_for('memories'))
    return redirect(url_for('index'))

@app.route('/api/memories')
def api_memories():
    """API endpoint for memories."""
    query = request.args.get('query', '')
    limit = int(request.args.get('limit', 20))
    memories = engine.retrieve_memories(query, limit)
    return jsonify({
        'success': True,
        'data': memories,
        'total': len(memories),
        'query': query,
        'limit': limit
    })

@app.route('/api/memories/<memory_id>')
def api_memory_detail(memory_id):
    """API endpoint for memory detail."""
    result = engine.manage_memory('view', memory_id)
    if result['success']:
        return jsonify({
            'success': True,
            'data': result['memory']
        })
    return jsonify({
        'success': False,
        'error': result.get('error', 'Memory not found')
    }), 404

@app.route('/api/process', methods=['POST'])
def api_process():
    """API endpoint for processing messages."""
    data = request.get_json()
    message = data.get('message')
    context = data.get('context')
    
    if message:
        result = engine.process_message(message, context)
        return jsonify({
            'success': True,
            'data': result
        })
    return jsonify({
        'success': False,
        'error': 'No message provided'
    }), 400

@app.route('/api/memories/<memory_id>', methods=['PUT'])
def api_update_memory(memory_id):
    """API endpoint for updating memory."""
    data = request.get_json()
    content = data.get('content')
    
    if content:
        result = engine.manage_memory('edit', memory_id, {'content': content})
        if result['success']:
            return jsonify({
                'success': True,
                'data': result['memory']
            })
        return jsonify({
            'success': False,
            'error': result.get('error', 'Failed to update memory')
        }), 400
    return jsonify({
        'success': False,
        'error': 'No content provided'
    }), 400

@app.route('/api/memories/<memory_id>', methods=['DELETE'])
def api_delete_memory(memory_id):
    """API endpoint for deleting memory."""
    result = engine.manage_memory('delete', memory_id)
    if result['success']:
        return jsonify({
            'success': True,
            'message': 'Memory deleted successfully'
        })
    return jsonify({
        'success': False,
        'error': result.get('error', 'Failed to delete memory')
    }), 400

@app.route('/api/stats')
def api_stats():
    """API endpoint for system statistics."""
    stats = engine.get_stats()
    return jsonify({
        'success': True,
        'data': stats
    })

@app.route('/api/plugins')
def api_plugins():
    """API endpoint for plugin information."""
    if hasattr(engine, 'plugin_manager'):
        plugins = engine.plugin_manager.get_all_plugin_info()
        return jsonify({
            'success': True,
            'data': plugins
        })
    return jsonify({
        'success': False,
        'error': 'Plugin system not available'
    }), 404

@app.route('/api/health')
def api_health():
    """API endpoint for health check."""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': time.time()
    })

@app.route('/api/version')
def api_version():
    """API endpoint for version information."""
    return jsonify({
        'success': True,
        'version': '1.0.0',
        'name': 'Memory Classification Engine API'
    })

if __name__ == '__main__':
    app.run(debug=True)
