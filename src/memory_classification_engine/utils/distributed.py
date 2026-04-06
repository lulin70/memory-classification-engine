"""Distributed deployment support utilities."""

import os
import json
import socket
import threading
import time
import queue
import gzip
import io
from typing import Dict, List, Optional, Any, Tuple, Set
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
        self.heartbeat_thread = None
        
        # Running flag
        self.running = False
        
        # Raft algorithm related
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0
        self.last_applied = 0
        # For single node cluster, start as leader
        self.state = 'leader'  # follower, candidate, leader
        self.election_timeout = 30  # seconds
        self.heartbeat_interval = 1  # seconds
        self.last_heartbeat = time.time()
        self.votes = set()
        
        # Load balancing related
        self.node_metrics = {
            self.node_id: {
                'cpu_usage': 0.0,
                'memory_usage': 0.0,
                'disk_usage': 0.0,
                'request_count': 0,
                'last_updated': datetime.now().isoformat()
            }
        }
        self.task_queue = queue.Queue()
        self.task_assignments = {}
        
        # Fault detection and recovery
        self.fault_detection_interval = 5  # seconds
        self.failed_nodes = set()
        self.recovery_queue = queue.Queue()
        
        # Network optimization
        self.use_compression = True
        self.connection_pool = {}
        self.batch_messages = {}
        self.batch_interval = 0.5  # seconds
        self.batch_timer = None
        
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
        
        # Start heartbeat thread
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
        
        # Start fault detection thread
        self.fault_detection_thread = threading.Thread(target=self._fault_detection_loop, daemon=True)
        self.fault_detection_thread.start()
        
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
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)
        if self.fault_detection_thread:
            self.fault_detection_thread.join(timeout=5)
        
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
                self.failed_nodes.add(node_id)
                logger.info(f"Removed stale node: {node_id}")
    
    def _fault_detection_loop(self):
        """Fault detection loop."""
        while self.running:
            try:
                self._detect_faults()
                self._recover_from_faults()
                time.sleep(self.fault_detection_interval)
            except Exception as e:
                logger.error(f"Error in fault detection loop: {e}")
                time.sleep(5)
    
    def _detect_faults(self):
        """Detect node faults."""
        with self.lock:
            current_time = datetime.now()
            for node_id, info in self.nodes.items():
                if node_id != self.node_id:
                    last_seen = datetime.fromisoformat(info['last_seen'])
                    if (current_time - last_seen).total_seconds() > self.discovery_interval * 2:
                        # Mark node as suspected
                        self.nodes[node_id]['status'] = 'suspected'
                        logger.warning(f"Node {node_id} is suspected to be faulty")
                    elif (current_time - last_seen).total_seconds() > self.discovery_interval * 3:
                        # Mark node as failed
                        self.nodes[node_id]['status'] = 'failed'
                        self.failed_nodes.add(node_id)
                        logger.error(f"Node {node_id} is marked as failed")
                        # Trigger fault recovery
                        self._handle_node_failure(node_id)
    
    def _handle_node_failure(self, node_id: str):
        """Handle node failure."""
        if not self.is_leader():
            return
        
        logger.info(f"Handling failure of node {node_id}")
        
        # Reassign tasks from failed node
        with self.lock:
            if node_id in self.task_assignments:
                tasks = self.task_assignments[node_id]
                for task in tasks:
                    self.task_queue.put(task)
                del self.task_assignments[node_id]
                logger.info(f"Reassigned {len(tasks)} tasks from failed node {node_id}")
        
        # Trigger task reallocation
        self.assign_tasks()
    
    def _recover_from_faults(self):
        """Recover from node faults."""
        with self.lock:
            # Check if any failed nodes have recovered
            recovered_nodes = []
            for node_id in list(self.failed_nodes):
                if node_id in self.nodes and self.nodes[node_id]['status'] == 'active':
                    recovered_nodes.append(node_id)
                    self.failed_nodes.remove(node_id)
                    logger.info(f"Node {node_id} has recovered")
            
            # Add recovered nodes to recovery queue
            for node_id in recovered_nodes:
                self.recovery_queue.put(node_id)
    
    def recover_node(self, node_id: str):
        """Recover a failed node.
        
        Args:
            node_id: Node ID to recover.
        """
        if node_id in self.failed_nodes:
            self.failed_nodes.remove(node_id)
            if node_id in self.nodes:
                self.nodes[node_id]['status'] = 'active'
            logger.info(f"Node {node_id} has been recovered")
    
    def get_failed_nodes(self) -> Set[str]:
        """Get list of failed nodes.
        
        Returns:
            Set of failed node IDs.
        """
        with self.lock:
            return self.failed_nodes.copy()
    
    def is_node_failed(self, node_id: str) -> bool:
        """Check if a node is failed.
        
        Args:
            node_id: Node ID to check.
            
        Returns:
            True if node is failed, False otherwise.
        """
        return node_id in self.failed_nodes
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get comprehensive cluster status.
        
        Returns:
            Cluster status information.
        """
        with self.lock:
            status = {
                'cluster_size': len(self.nodes),
                'leader': self.get_leader(),
                'nodes': {},
                'failed_nodes': list(self.failed_nodes),
                'total_tasks': self.task_queue.qsize(),
                'task_assignments': {node: len(tasks) for node, tasks in self.task_assignments.items()},
                'timestamp': datetime.now().isoformat()
            }
            
            # Add node details
            for node_id, node_info in self.nodes.items():
                status['nodes'][node_id] = {
                    'ip': node_info['ip'],
                    'port': node_info['port'],
                    'status': node_info['status'],
                    'last_seen': node_info['last_seen'],
                    'health': self.get_node_health(node_id),
                    'metrics': self.node_metrics.get(node_id, {})
                }
            
            return status
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the cluster.
        
        Returns:
            Performance metrics.
        """
        with self.lock:
            metrics = {
                'node_count': len(self.nodes),
                'failed_node_count': len(self.failed_nodes),
                'average_cpu_usage': 0.0,
                'average_memory_usage': 0.0,
                'total_requests': 0,
                'timestamp': datetime.now().isoformat()
            }
            
            # Calculate average metrics
            if self.node_metrics:
                cpu_usages = [m.get('cpu_usage', 0) for m in self.node_metrics.values()]
                memory_usages = [m.get('memory_usage', 0) for m in self.node_metrics.values()]
                request_counts = [m.get('request_count', 0) for m in self.node_metrics.values()]
                
                metrics['average_cpu_usage'] = sum(cpu_usages) / len(cpu_usages) if cpu_usages else 0
                metrics['average_memory_usage'] = sum(memory_usages) / len(memory_usages) if memory_usages else 0
                metrics['total_requests'] = sum(request_counts)
            
            return metrics
    
    def get_raft_status(self) -> Dict[str, Any]:
        """Get Raft algorithm status.
        
        Returns:
            Raft status information.
        """
        return {
            'current_term': self.current_term,
            'state': self.state,
            'voted_for': self.voted_for,
            'log_length': len(self.log),
            'commit_index': self.commit_index,
            'last_applied': self.last_applied
        }
    
    def generate_cluster_report(self) -> str:
        """Generate a comprehensive cluster report.
        
        Returns:
            Cluster report as a string.
        """
        status = self.get_cluster_status()
        performance = self.get_performance_metrics()
        raft_status = self.get_raft_status()
        
        report = f"Cluster Report - {status['timestamp']}\n"
        report += "=" * 80 + "\n"
        report += f"Cluster Size: {status['cluster_size']}\n"
        report += f"Leader: {status['leader']}\n"
        report += f"Failed Nodes: {len(status['failed_nodes'])} - {', '.join(status['failed_nodes']) if status['failed_nodes'] else 'None'}\n"
        report += f"Total Tasks: {status['total_tasks']}\n"
        report += "\nNode Details:\n"
        report += "-" * 80 + "\n"
        
        for node_id, node_info in status['nodes'].items():
            report += f"Node: {node_id}\n"
            report += f"  IP: {node_info['ip']}:{node_info['port']}\n"
            report += f"  Status: {node_info['status']}\n"
            report += f"  Health: {node_info['health']}\n"
            report += f"  Last Seen: {node_info['last_seen']}\n"
            report += f"  CPU Usage: {node_info['metrics'].get('cpu_usage', 0):.2f}%\n"
            report += f"  Memory Usage: {node_info['metrics'].get('memory_usage', 0):.2f}%\n"
            report += f"  Requests: {node_info['metrics'].get('request_count', 0)}\n"
            report += "-" * 80 + "\n"
        
        report += "\nPerformance Metrics:\n"
        report += "-" * 80 + "\n"
        report += f"Average CPU Usage: {performance['average_cpu_usage']:.2f}%\n"
        report += f"Average Memory Usage: {performance['average_memory_usage']:.2f}%\n"
        report += f"Total Requests: {performance['total_requests']}\n"
        
        report += "\nRaft Status:\n"
        report += "-" * 80 + "\n"
        report += f"Current Term: {raft_status['current_term']}\n"
        report += f"State: {raft_status['state']}\n"
        report += f"Voted For: {raft_status['voted_for']}\n"
        report += f"Log Length: {raft_status['log_length']}\n"
        report += f"Commit Index: {raft_status['commit_index']}\n"
        report += f"Last Applied: {raft_status['last_applied']}\n"
        
        return report
    
    def _compress_message(self, message: Dict[str, Any]) -> bytes:
        """Compress a message to reduce bandwidth usage.
        
        Args:
            message: Message to compress.
            
        Returns:
            Compressed message bytes.
        """
        if not self.use_compression:
            return json.dumps(message).encode()
        
        json_str = json.dumps(message)
        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode='w') as f:
            f.write(json_str.encode())
        return buffer.getvalue()
    
    def _decompress_message(self, data: bytes) -> Dict[str, Any]:
        """Decompress a message.
        
        Args:
            data: Compressed message bytes.
            
        Returns:
            Decompressed message.
        """
        try:
            # Try to decompress
            buffer = io.BytesIO(data)
            with gzip.GzipFile(fileobj=buffer, mode='r') as f:
                json_str = f.read().decode()
            return json.loads(json_str)
        except:
            # If decompression fails, try to parse as uncompressed JSON
            return json.loads(data.decode())
    
    def _get_connection(self, node_id: str, node_info: Dict[str, Any]) -> Optional[socket.socket]:
        """Get a connection from the pool or create a new one.
        
        Args:
            node_id: Node ID.
            node_info: Node information.
            
        Returns:
            Socket connection or None if failed.
        """
        # Check if we have a valid connection in the pool
        if node_id in self.connection_pool:
            sock = self.connection_pool[node_id]
            try:
                # Test if connection is still alive
                sock.sendall(b'')
                return sock
            except:
                # Connection is dead, remove it
                del self.connection_pool[node_id]
        
        # Create a new connection
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((node_info['ip'], node_info['port']))
            self.connection_pool[node_id] = sock
            return sock
        except Exception as e:
            logger.error(f"Error creating connection to node {node_id}: {e}")
            return None
    
    def _close_connection(self, node_id: str):
        """Close a connection and remove it from the pool.
        
        Args:
            node_id: Node ID.
        """
        if node_id in self.connection_pool:
            try:
                self.connection_pool[node_id].close()
            except:
                pass
            del self.connection_pool[node_id]
    
    def _batch_message(self, node_id: str, message: Dict[str, Any]):
        """Add a message to the batch for a node.
        
        Args:
            node_id: Node ID.
            message: Message to batch.
        """
        if node_id not in self.batch_messages:
            self.batch_messages[node_id] = []
        self.batch_messages[node_id].append(message)
        
        # Start batch timer if not running
        if not self.batch_timer:
            self.batch_timer = threading.Timer(self.batch_interval, self._send_batched_messages)
            self.batch_timer.daemon = True
            self.batch_timer.start()
    
    def _send_batched_messages(self):
        """Send batched messages to all nodes."""
        with self.lock:
            for node_id, messages in list(self.batch_messages.items()):
                if messages:
                    # Create a batch message
                    batch_message = {
                        'type': 'batch',
                        'messages': messages
                    }
                    
                    # Send the batch
                    if node_id in self.nodes:
                        try:
                            sock = self._get_connection(node_id, self.nodes[node_id])
                            if sock:
                                compressed = self._compress_message(batch_message)
                                sock.sendall(compressed)
                        except Exception as e:
                            logger.error(f"Error sending batch to node {node_id}: {e}")
                            self._close_connection(node_id)
                    
                    # Clear the batch
                    del self.batch_messages[node_id]
        
        # Reset batch timer
        self.batch_timer = None
    
    def _heartbeat_loop(self):
        """Heartbeat and election loop."""
        while self.running:
            try:
                if self.state == 'leader':
                    # Send heartbeats to all followers
                    self._send_heartbeats()
                    time.sleep(self.heartbeat_interval)
                else:
                    # Check if election timeout has occurred
                    if time.time() - self.last_heartbeat > self.election_timeout:
                        self._start_election()
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                time.sleep(5)
    
    def _send_heartbeats(self):
        """Send heartbeat messages to all followers."""
        with self.lock:
            for node_id, info in self.nodes.items():
                if node_id != self.node_id:
                    try:
                        self._send_append_entries(node_id, info)
                    except Exception as e:
                        logger.error(f"Error sending heartbeat to node {node_id}: {e}")
    
    def _start_election(self):
        """Start a new election."""
        with self.lock:
            self.state = 'candidate'
            self.current_term += 1
            self.voted_for = self.node_id
            self.votes = {self.node_id}
            
            logger.info(f"Starting election for term {self.current_term}")
            
            # Request votes from all other nodes
            for node_id, info in self.nodes.items():
                if node_id != self.node_id:
                    try:
                        self._request_vote(node_id, info)
                    except Exception as e:
                        logger.error(f"Error requesting vote from node {node_id}: {e}")
            
            # Wait for votes
            time.sleep(2)
            
            # Check if we got majority
            majority = (len(self.nodes) // 2) + 1
            if len(self.votes) >= majority:
                self.state = 'leader'
                logger.info(f"Elected as leader for term {self.current_term}")
            else:
                self.state = 'follower'
                logger.info(f"Election failed, remaining as follower")
    
    def _request_vote(self, node_id: str, node_info: Dict[str, Any]):
        """Request vote from a node."""
        vote_request = {
            'type': 'request_vote',
            'term': self.current_term,
            'candidate_id': self.node_id,
            'last_log_index': len(self.log) - 1,
            'last_log_term': self.log[-1]['term'] if self.log else 0
        }
        
        # Send vote request
        try:
            sock = self._get_connection(node_id, node_info)
            if sock:
                compressed = self._compress_message(vote_request)
                sock.sendall(compressed)
                response = sock.recv(1024)
                if response:
                    vote_response = self._decompress_message(response)
                    if vote_response.get('vote_granted'):
                        self.votes.add(node_id)
        except Exception as e:
            logger.error(f"Error requesting vote: {e}")
            self._close_connection(node_id)
    
    def _send_append_entries(self, node_id: str, node_info: Dict[str, Any]):
        """Send append entries (heartbeat or log replication)."""
        append_entries = {
            'type': 'append_entries',
            'term': self.current_term,
            'leader_id': self.node_id,
            'prev_log_index': len(self.log) - 1,
            'prev_log_term': self.log[-1]['term'] if self.log else 0,
            'entries': [],  # Empty for heartbeat
            'leader_commit': self.commit_index
        }
        
        try:
            sock = self._get_connection(node_id, node_info)
            if sock:
                compressed = self._compress_message(append_entries)
                sock.sendall(compressed)
        except Exception as e:
            logger.error(f"Error sending append entries: {e}")
            self._close_connection(node_id)
    
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
    
    def replicate_log(self, entry: Dict[str, Any]):
        """Replicate log entry to all followers.
        
        Args:
            entry: Log entry to replicate.
        """
        if not self.is_leader():
            return False
        
        # Add entry to local log
        log_entry = {
            'term': self.current_term,
            'index': len(self.log),
            'data': entry
        }
        self.log.append(log_entry)
        
        # Replicate to followers
        success_count = 1  # Count self
        with self.lock:
            for node_id, info in self.nodes.items():
                if node_id != self.node_id:
                    try:
                        if self._replicate_to_node(node_id, info, log_entry):
                            success_count += 1
                    except Exception as e:
                        logger.error(f"Error replicating to node {node_id}: {e}")
        
        # Check if majority has replicated
        majority = (len(self.nodes) // 2) + 1
        if success_count >= majority:
            # Commit the entry
            self.commit_index = len(self.log) - 1
            logger.info(f"Committed log entry at index {self.commit_index}")
            return True
        
        return False
    
    def _replicate_to_node(self, node_id: str, node_info: Dict[str, Any], log_entry: Dict[str, Any]) -> bool:
        """Replicate log entry to a specific node.
        
        Args:
            node_id: Node ID.
            node_info: Node information.
            log_entry: Log entry to replicate.
            
        Returns:
            True if replication successful, False otherwise.
        """
        append_entries = {
            'type': 'append_entries',
            'term': self.current_term,
            'leader_id': self.node_id,
            'prev_log_index': log_entry['index'] - 1,
            'prev_log_term': self.log[log_entry['index'] - 1]['term'] if log_entry['index'] > 0 else 0,
            'entries': [log_entry],
            'leader_commit': self.commit_index
        }
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((node_info['ip'], node_info['port']))
            sock.sendall(json.dumps(append_entries).encode())
            response = sock.recv(1024)
            sock.close()
            
            if response:
                response_data = json.loads(response.decode())
                return response_data.get('success', False)
        except Exception as e:
            logger.error(f"Error replicating to node: {e}")
        
        return False
    
    def check_data_consistency(self) -> bool:
        """Check data consistency across the cluster.
        
        Returns:
            True if data is consistent, False otherwise.
        """
        if not self.is_leader():
            return False
        
        # Get data hashes from all nodes
        node_hashes = {}
        with self.lock:
            for node_id, info in self.nodes.items():
                if node_id != self.node_id:
                    try:
                        node_hash = self._get_node_data_hash(node_id, info)
                        if node_hash:
                            node_hashes[node_id] = node_hash
                    except Exception as e:
                        logger.error(f"Error getting data hash from node {node_id}: {e}")
        
        # Check if all hashes match
        if not node_hashes:
            return True  # No other nodes, so consistent
        
        reference_hash = list(node_hashes.values())[0]
        for node_id, node_hash in node_hashes.items():
            if node_hash != reference_hash:
                logger.error(f"Data inconsistency detected: node {node_id} has different hash")
                return False
        
        logger.info("Data consistency check passed")
        return True
    
    def _get_node_data_hash(self, node_id: str, node_info: Dict[str, Any]) -> str:
        """Get data hash from a node.
        
        Args:
            node_id: Node ID.
            node_info: Node information.
            
        Returns:
            Data hash or None if failed.
        """
        # In a real implementation, this would request the data hash from the node
        # For now, return a dummy hash
        return "dummy_hash"
    
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
                message = self._decompress_message(data)
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
        
        if message_type == 'batch':
            # Handle batched messages
            messages = message.get('messages', [])
            for msg in messages:
                self._handle_message(msg, address)
        elif message_type == 'discovery':
            self._handle_discovery(message, address)
        elif message_type == 'sync':
            self._handle_sync(message, address)
        elif message_type == 'heartbeat':
            self._handle_heartbeat(message, address)
        elif message_type == 'request_vote':
            self._handle_request_vote(message, address)
        elif message_type == 'append_entries':
            self._handle_append_entries(message, address)
    
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
    
    def _handle_request_vote(self, message: Dict[str, Any], address: Tuple[str, int]):
        """Handle vote request message.
        
        Args:
            message: Vote request message.
            address: Sender address.
        """
        term = message.get('term')
        candidate_id = message.get('candidate_id')
        last_log_index = message.get('last_log_index')
        last_log_term = message.get('last_log_term')
        
        # Update term if needed
        if term > self.current_term:
            self.current_term = term
            self.state = 'follower'
            self.voted_for = None
        
        # Determine if we should grant the vote
        vote_granted = False
        if term == self.current_term and (self.voted_for is None or self.voted_for == candidate_id):
            # Check log completeness
            last_log_entry = self.log[-1] if self.log else None
            local_last_term = last_log_entry['term'] if last_log_entry else 0
            local_last_index = len(self.log) - 1
            
            if last_log_term > local_last_term or (last_log_term == local_last_term and last_log_index <= local_last_index):
                vote_granted = True
                self.voted_for = candidate_id
        
        # Send vote response
        response = {
            'term': self.current_term,
            'vote_granted': vote_granted
        }
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(address)
            sock.sendall(json.dumps(response).encode())
            sock.close()
        except Exception as e:
            logger.error(f"Error sending vote response: {e}")
    
    def _handle_append_entries(self, message: Dict[str, Any], address: Tuple[str, int]):
        """Handle append entries message (heartbeat or log replication).
        
        Args:
            message: Append entries message.
            address: Sender address.
        """
        term = message.get('term')
        leader_id = message.get('leader_id')
        prev_log_index = message.get('prev_log_index')
        prev_log_term = message.get('prev_log_term')
        entries = message.get('entries', [])
        leader_commit = message.get('leader_commit')
        
        # Update term if needed
        if term > self.current_term:
            self.current_term = term
            self.state = 'follower'
            self.voted_for = None
        
        # Update last heartbeat time
        self.last_heartbeat = time.time()
        
        # Check if we should become follower
        if self.state != 'follower':
            self.state = 'follower'
        
        # Send response
        success = True
        # In a real implementation, we would check log consistency here
        
        response = {
            'term': self.current_term,
            'success': success
        }
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(address)
            sock.sendall(json.dumps(response).encode())
            sock.close()
        except Exception as e:
            logger.error(f"Error sending append entries response: {e}")
        
        # Apply entries if needed
        if entries:
            for entry in entries:
                self.log.append(entry)
        
        # Update commit index
        if leader_commit > self.commit_index:
            self.commit_index = min(leader_commit, len(self.log) - 1)
            # Apply committed entries
            while self.last_applied < self.commit_index:
                self.last_applied += 1
                # Apply the log entry
                entry = self.log[self.last_applied]
                # In a real implementation, we would apply the entry to the state machine
    
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
        return self.state == 'leader'
    
    def get_leader(self) -> Optional[str]:
        """Get the current leader node ID.
        
        Returns:
            Leader node ID or None.
        """
        if self.state == 'leader':
            return self.node_id
        # In a real implementation, we would track the leader ID
        # For now, return None if this node is not the leader
        return None
    
    def update_node_metrics(self, metrics: Dict[str, Any]):
        """Update node metrics for load balancing.
        
        Args:
            metrics: Node metrics including cpu_usage, memory_usage, etc.
        """
        with self.lock:
            self.node_metrics[self.node_id].update(metrics)
            self.node_metrics[self.node_id]['last_updated'] = datetime.now().isoformat()
    
    def get_node_metrics(self, node_id: str = None) -> Dict[str, Any]:
        """Get node metrics.
        
        Args:
            node_id: Node ID to get metrics for. If None, get all metrics.
            
        Returns:
            Node metrics.
        """
        with self.lock:
            if node_id:
                return self.node_metrics.get(node_id, {})
            return self.node_metrics.copy()
    
    def add_task(self, task: Dict[str, Any]):
        """Add a task to the task queue.
        
        Args:
            task: Task to add.
        """
        self.task_queue.put(task)
    
    def assign_tasks(self):
        """Assign tasks to nodes based on load balancing strategy."""
        if not self.is_leader():
            return
        
        with self.lock:
            # Get available nodes
            available_nodes = [node_id for node_id in self.nodes if self.nodes[node_id]['status'] == 'active']
            if not available_nodes:
                return
            
            # Calculate node scores based on metrics
            node_scores = {}
            for node_id in available_nodes:
                metrics = self.node_metrics.get(node_id, {})
                # Simple scoring: lower resource usage = higher score
                score = 100 - (metrics.get('cpu_usage', 0) + metrics.get('memory_usage', 0)) / 2
                node_scores[node_id] = score
            
            # Sort nodes by score (highest first)
            sorted_nodes = sorted(node_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Assign tasks to nodes
            while not self.task_queue.empty() and sorted_nodes:
                task = self.task_queue.get()
                best_node = sorted_nodes[0][0]
                
                # Assign task
                if best_node not in self.task_assignments:
                    self.task_assignments[best_node] = []
                self.task_assignments[best_node].append(task)
                
                # Update request count for the node
                if best_node in self.node_metrics:
                    self.node_metrics[best_node]['request_count'] += 1
                
                logger.info(f"Assigned task to node {best_node}")
    
    def get_task_assignments(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get task assignments.
        
        Returns:
            Task assignments by node ID.
        """
        with self.lock:
            return self.task_assignments.copy()
    
    def get_node_health(self, node_id: str) -> str:
        """Get node health status.
        
        Args:
            node_id: Node ID.
            
        Returns:
            Health status ('healthy', 'warning', 'critical').
        """
        metrics = self.node_metrics.get(node_id, {})
        cpu_usage = metrics.get('cpu_usage', 0)
        memory_usage = metrics.get('memory_usage', 0)
        
        if cpu_usage > 80 or memory_usage > 80:
            return 'critical'
        elif cpu_usage > 60 or memory_usage > 60:
            return 'warning'
        else:
            return 'healthy'
    
    def get_cluster_health(self) -> Dict[str, str]:
        """Get cluster health status.
        
        Returns:
            Health status for each node.
        """
        health_status = {}
        with self.lock:
            for node_id in self.nodes:
                health_status[node_id] = self.get_node_health(node_id)
        return health_status


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
    
    @staticmethod
    def incremental_sync(source: Dict[str, Any], target: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Perform incremental synchronization.
        
        Args:
            source: Source data.
            target: Target data.
            
        Returns:
            Tuple of (merged data, list of changes made)
        """
        changes = DataSynchronizer.detect_changes(target, source)
        merged_data = DataSynchronizer.sync_data(source, target)
        return merged_data, changes
    
    @staticmethod
    def resolve_conflicts(conflicts: List[Dict[str, Any]], resolution_strategy: str = 'latest') -> Dict[str, Any]:
        """Resolve conflicts between different versions of data.
        
        Args:
            conflicts: List of conflicted changes.
            resolution_strategy: Resolution strategy ('latest', 'earliest', 'custom').
            
        Returns:
            Resolved changes.
        """
        resolved_changes = {}
        
        for conflict in conflicts:
            path = conflict['path']
            if resolution_strategy == 'latest':
                # Keep the latest change
                resolved_changes[path] = conflict.get('new_value', conflict.get('value'))
            elif resolution_strategy == 'earliest':
                # Keep the earliest change
                resolved_changes[path] = conflict.get('old_value', conflict.get('value'))
            # For 'custom' strategy, we would need more context
        
        return resolved_changes
    
    @staticmethod
    def calculate_merkle_tree(data: Dict[str, Any]) -> Dict[str, str]:
        """Calculate Merkle tree for efficient change detection.
        
        Args:
            data: Data to calculate Merkle tree for.
            
        Returns:
            Merkle tree structure with hashes for each node.
        """
        merkle_tree = {}
        DataSynchronizer._calculate_merkle_tree_recursive(data, '', merkle_tree)
        return merkle_tree
    
    @staticmethod
    def _calculate_merkle_tree_recursive(data: Any, path: str, merkle_tree: Dict[str, str]):
        """Calculate Merkle tree recursively.
        
        Args:
            data: Current data node.
            path: Current path in the tree.
            merkle_tree: Dictionary to store Merkle tree hashes.
        """
        if isinstance(data, dict):
            # Calculate hashes for all children
            child_hashes = []
            for key, value in sorted(data.items()):
                child_path = f"{path}.{key}" if path else key
                DataSynchronizer._calculate_merkle_tree_recursive(value, child_path, merkle_tree)
                child_hashes.append(merkle_tree[child_path])
            # Calculate hash for current node
            node_hash = DataSynchronizer.calculate_hash(''.join(child_hashes))
            merkle_tree[path] = node_hash
        elif isinstance(data, list):
            # Calculate hashes for all items
            item_hashes = []
            for i, item in enumerate(data):
                item_path = f"{path}[{i}]"
                DataSynchronizer._calculate_merkle_tree_recursive(item, item_path, merkle_tree)
                item_hashes.append(merkle_tree[item_path])
            # Calculate hash for current node
            node_hash = DataSynchronizer.calculate_hash(''.join(item_hashes))
            merkle_tree[path] = node_hash
        else:
            # Calculate hash for leaf node
            merkle_tree[path] = DataSynchronizer.calculate_hash(data)
    
    @staticmethod
    def find_differences(merkle_tree1: Dict[str, str], merkle_tree2: Dict[str, str]) -> List[str]:
        """Find differences between two Merkle trees.
        
        Args:
            merkle_tree1: First Merkle tree.
            merkle_tree2: Second Merkle tree.
            
        Returns:
            List of paths with differences.
        """
        differences = []
        all_paths = set(merkle_tree1.keys()) | set(merkle_tree2.keys())
        
        for path in all_paths:
            if merkle_tree1.get(path) != merkle_tree2.get(path):
                differences.append(path)
        
        return differences
