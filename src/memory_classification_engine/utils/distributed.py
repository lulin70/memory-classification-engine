"""Distributed deployment support utilities."""

import os
import json
import socket
import threading
import time
import queue
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from memory_classification_engine.utils.logger import logger


class DistributedManager:
    """Distributed deployment manager for Memory Classification Engine."""
    
    def __init__(self, node_id: str = None, port: int = 5000, discovery_interval: int = 30):
        """Initialize the distributed manager.
        
        Args:
            node_id: Unique identifier for this node.
            port: Port to use for communication.
            discovery_interval: Interval for node discovery in seconds.
        """
        self.node_id = node_id or f"node_{socket.gethostname()}_{os.getpid()}"
        self.port = port
        self.discovery_interval = discovery_interval
        
        # Nodes information
        self.nodes = {
            self.node_id: {
                'ip': self._get_local_ip(),
                'port': port,
                'last_seen': datetime.now().isoformat(),
                'status': 'active'
            }
        }
        
        # Data synchronization
        self.sync_queue = queue.Queue()
        self.sync_interval = 60  # seconds
        
        # Lock for thread safety
        self.lock = threading.RLock()
        
        # Threads
        self.discovery_thread = None
        self.sync_thread = None
        self.server_thread = None
        
        # Running flag
        self.running = False
        
        logger.info(f"DistributedManager initialized with node ID: {self.node_id}")
    
    def _get_local_ip(self) -> str:
        """Get local IP address.
        
        Returns:
            Local IP address.
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '127.0.0.1'
    
    def start(self):
        """Start distributed services."""
        if self.running:
            return
        
        self.running = True
        
        # Start discovery thread
        self.discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
        self.discovery_thread.start()
        
        # Start sync thread
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        
        # Start server thread
        self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
        self.server_thread.start()
        
        logger.info("Distributed services started")
    
    def stop(self):
        """Stop distributed services."""
        if not self.running:
            return
        
        self.running = False
        
        # Wait for threads to finish
        if self.discovery_thread:
            self.discovery_thread.join(timeout=5)
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        if self.server_thread:
            self.server_thread.join(timeout=5)
        
        logger.info("Distributed services stopped")
    
    def _discovery_loop(self):
        """Node discovery loop."""
        while self.running:
            try:
                # Send discovery message
                self._send_discovery()
                
                # Clean up stale nodes
                self._cleanup_stale_nodes()
                
                time.sleep(self.discovery_interval)
            except Exception as e:
                logger.error(f"Error in discovery loop: {e}")
                time.sleep(5)
    
    def _send_discovery(self):
        """Send discovery message."""
        try:
            # Broadcast discovery message
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            discovery_msg = {
                'type': 'discovery',
                'node_id': self.node_id,
                'ip': self.nodes[self.node_id]['ip'],
                'port': self.port,
                'timestamp': datetime.now().isoformat()
            }
            
            sock.sendto(json.dumps(discovery_msg).encode(), ('255.255.255.255', self.port))
            sock.close()
        except Exception as e:
            logger.error(f"Error sending discovery: {e}")
    
    def _cleanup_stale_nodes(self):
        """Clean up stale nodes."""
        with self.lock:
            current_time = datetime.now()
            stale_nodes = []
            
            for node_id, info in self.nodes.items():
                if node_id != self.node_id:
                    last_seen = datetime.fromisoformat(info['last_seen'])
                    if (current_time - last_seen).total_seconds() > self.discovery_interval * 3:
                        stale_nodes.append(node_id)
            
            for node_id in stale_nodes:
                del self.nodes[node_id]
                logger.info(f"Removed stale node: {node_id}")
    
    def _sync_loop(self):
        """Data synchronization loop."""
        while self.running:
            try:
                # Process sync queue
                self._process_sync_queue()
                
                # Sync with other nodes
                self._sync_with_nodes()
                
                time.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
                time.sleep(5)
    
    def _process_sync_queue(self):
        """Process synchronization queue."""
        while not self.sync_queue.empty():
            try:
                item = self.sync_queue.get()
                # Process sync item
                logger.debug(f"Processing sync item: {item}")
            except Exception as e:
                logger.error(f"Error processing sync queue: {e}")
            finally:
                self.sync_queue.task_done()
    
    def _sync_with_nodes(self):
        """Sync data with other nodes."""
        with self.lock:
            for node_id, info in self.nodes.items():
                if node_id != self.node_id:
                    try:
                        # Sync with this node
                        self._sync_with_node(node_id, info)
                    except Exception as e:
                        logger.error(f"Error syncing with node {node_id}: {e}")
    
    def _sync_with_node(self, node_id: str, node_info: Dict[str, Any]):
        """Sync with a specific node.
        
        Args:
            node_id: Node ID.
            node_info: Node information.
        """
        # In a real implementation, this would:
        # 1. Establish a connection to the node
        # 2. Exchange data hashes
        # 3. Transfer missing or updated data
        # 4. Verify synchronization
        
        logger.debug(f"Syncing with node {node_id} at {node_info['ip']}:{node_info['port']}")
    
    def _server_loop(self):
        """Server loop for handling incoming connections."""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('0.0.0.0', self.port))
            server_socket.listen(5)
            
            while self.running:
                try:
                    client_socket, address = server_socket.accept()
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if not self.running:
                        break
                    logger.error(f"Error in server loop: {e}")
                    time.sleep(1)
        finally:
            server_socket.close()
    
    def _handle_client(self, client_socket: socket.socket, address: Tuple[str, int]):
        """Handle incoming client connection.
        
        Args:
            client_socket: Client socket.
            address: Client address.
        """
        try:
            data = client_socket.recv(1024)
            if data:
                message = json.loads(data.decode())
                self._handle_message(message, address)
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            client_socket.close()
    
    def _handle_message(self, message: Dict[str, Any], address: Tuple[str, int]):
        """Handle incoming message.
        
        Args:
            message: Message data.
            address: Sender address.
        """
        message_type = message.get('type')
        
        if message_type == 'discovery':
            self._handle_discovery(message, address)
        elif message_type == 'sync':
            self._handle_sync(message, address)
        elif message_type == 'heartbeat':
            self._handle_heartbeat(message, address)
    
    def _handle_discovery(self, message: Dict[str, Any], address: Tuple[str, int]):
        """Handle discovery message.
        
        Args:
            message: Discovery message.
            address: Sender address.
        """
        node_id = message.get('node_id')
        if node_id and node_id != self.node_id:
            with self.lock:
                self.nodes[node_id] = {
                    'ip': message.get('ip', address[0]),
                    'port': message.get('port', self.port),
                    'last_seen': datetime.now().isoformat(),
                    'status': 'active'
                }
            logger.info(f"Discovered node: {node_id} at {self.nodes[node_id]['ip']}:{self.nodes[node_id]['port']}")
    
    def _handle_sync(self, message: Dict[str, Any], address: Tuple[str, int]):
        """Handle sync message.
        
        Args:
            message: Sync message.
            address: Sender address.
        """
        # Handle sync request/response
        logger.debug(f"Received sync message: {message}")
    
    def _handle_heartbeat(self, message: Dict[str, Any], address: Tuple[str, int]):
        """Handle heartbeat message.
        
        Args:
            message: Heartbeat message.
            address: Sender address.
        """
        node_id = message.get('node_id')
        if node_id and node_id != self.node_id:
            with self.lock:
                if node_id in self.nodes:
                    self.nodes[node_id]['last_seen'] = datetime.now().isoformat()
                    self.nodes[node_id]['status'] = 'active'
    
    def add_sync_item(self, item: Dict[str, Any]):
        """Add an item to the sync queue.
        
        Args:
            item: Sync item.
        """
        self.sync_queue.put(item)
    
    def get_nodes(self) -> Dict[str, Dict[str, Any]]:
        """Get all known nodes.
        
        Returns:
            Dictionary of nodes.
        """
        with self.lock:
            return self.nodes.copy()
    
    def get_node_count(self) -> int:
        """Get number of nodes in the cluster.
        
        Returns:
            Number of nodes.
        """
        with self.lock:
            return len(self.nodes)
    
    def is_leader(self) -> bool:
        """Check if this node is the leader.
        
        Returns:
            True if this node is the leader, False otherwise.
        """
        # Simple leader election: node with lex smallest ID is leader
        with self.lock:
            node_ids = sorted(self.nodes.keys())
            return node_ids[0] == self.node_id
    
    def get_leader(self) -> Optional[str]:
        """Get the current leader node ID.
        
        Returns:
            Leader node ID or None.
        """
        with self.lock:
            if not self.nodes:
                return None
            node_ids = sorted(self.nodes.keys())
            return node_ids[0]


class DataSynchronizer:
    """Data synchronization utility."""
    
    @staticmethod
    def sync_data(source: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronize data between source and target.
        
        Args:
            source: Source data.
            target: Target data.
            
        Returns:
            Merged data.
        """
        # Recursively merge data
        return DataSynchronizer._merge_data(source, target)
    
    @staticmethod
    def _merge_data(source: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, Any]:
        """Merge data recursively.
        
        Args:
            source: Source data.
            target: Target data.
            
        Returns:
            Merged data.
        """
        result = target.copy()
        
        for key, value in source.items():
            if key in result:
                if isinstance(value, dict) and isinstance(result[key], dict):
                    # Recursive merge for dictionaries
                    result[key] = DataSynchronizer._merge_data(value, result[key])
                elif isinstance(value, list) and isinstance(result[key], list):
                    # Merge lists (keep unique items)
                    merged_list = result[key].copy()
                    for item in value:
                        if item not in merged_list:
                            merged_list.append(item)
                    result[key] = merged_list
                else:
                    # Override with source value
                    result[key] = value
            else:
                # Add new key
                result[key] = value
        
        return result
    
    @staticmethod
    def calculate_hash(data: Any) -> str:
        """Calculate hash for data.
        
        Args:
            data: Data to hash.
            
        Returns:
            Hash string.
        """
        import hashlib
        
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    @staticmethod
    def detect_changes(old_data: Dict[str, Any], new_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect changes between old and new data.
        
        Args:
            old_data: Old data.
            new_data: New data.
            
        Returns:
            List of changes.
        """
        changes = []
        DataSynchronizer._detect_changes_recursive(old_data, new_data, '', changes)
        return changes
    
    @staticmethod
    def _detect_changes_recursive(old: Any, new: Any, path: str, changes: List[Dict[str, Any]]):
        """Detect changes recursively.
        
        Args:
            old: Old value.
            new: New value.
            path: Current path.
            changes: List to collect changes.
        """
        if isinstance(old, dict) and isinstance(new, dict):
            # Check for added keys
            for key in new:
                new_path = f"{path}.{key}" if path else key
                if key not in old:
                    changes.append({
                        'type': 'add',
                        'path': new_path,
                        'value': new[key]
                    })
                else:
                    DataSynchronizer._detect_changes_recursive(
                        old[key], new[key], new_path, changes
                    )
            
            # Check for removed keys
            for key in old:
                new_path = f"{path}.{key}" if path else key
                if key not in new:
                    changes.append({
                        'type': 'remove',
                        'path': new_path,
                        'value': old[key]
                    })
        
        elif isinstance(old, list) and isinstance(new, list):
            # Check for list changes
            if len(old) != len(new):
                changes.append({
                    'type': 'modify',
                    'path': path,
                    'old_value': old,
                    'new_value': new
                })
            else:
                for i, (old_item, new_item) in enumerate(zip(old, new)):
                    new_path = f"{path}[{i}]"
                    DataSynchronizer._detect_changes_recursive(
                        old_item, new_item, new_path, changes
                    )
        
        else:
            # Check for value changes
            if old != new:
                changes.append({
                    'type': 'modify',
                    'path': path,
                    'old_value': old,
                    'new_value': new
                })
