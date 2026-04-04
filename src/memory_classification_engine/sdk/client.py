"""Memory Classification Engine SDK client."""

import requests
import json
from typing import Dict, List, Optional, Any
from memory_classification_engine.sdk.exceptions import MemoryClassificationError


class MemoryClassificationClient:
    """SDK client for Memory Classification Engine."""
    
    def __init__(self, base_url: str = 'http://localhost:5000', timeout: int = 30):
        """Initialize the SDK client.
        
        Args:
            base_url: Base URL of the Memory Classification Engine API.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a message.
        
        Args:
            message: The message to process.
            context: Optional context information.
            
        Returns:
            Processing result.
        """
        url = f"{self.base_url}/api/process"
        data = {
            'message': message,
            'context': context
        }
        
        try:
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success'):
                raise MemoryClassificationError(result.get('error', 'Unknown error'))
            
            return result['data']
        except requests.RequestException as e:
            raise MemoryClassificationError(f"API request failed: {str(e)}")
        except Exception as e:
            raise MemoryClassificationError(f"Error processing message: {str(e)}")
    
    def retrieve_memories(self, query: str = '', limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve memories.
        
        Args:
            query: Optional search query.
            limit: Maximum number of memories to return.
            
        Returns:
            List of memories.
        """
        url = f"{self.base_url}/api/memories"
        params = {
            'query': query,
            'limit': limit
        }
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success'):
                raise MemoryClassificationError(result.get('error', 'Unknown error'))
            
            return result['data']
        except requests.RequestException as e:
            raise MemoryClassificationError(f"API request failed: {str(e)}")
        except Exception as e:
            raise MemoryClassificationError(f"Error retrieving memories: {str(e)}")
    
    def get_memory(self, memory_id: str) -> Dict[str, Any]:
        """Get a memory by ID.
        
        Args:
            memory_id: Memory ID.
            
        Returns:
            Memory information.
        """
        url = f"{self.base_url}/api/memories/{memory_id}"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success'):
                raise MemoryClassificationError(result.get('error', 'Memory not found'))
            
            return result['data']
        except requests.RequestException as e:
            raise MemoryClassificationError(f"API request failed: {str(e)}")
        except Exception as e:
            raise MemoryClassificationError(f"Error getting memory: {str(e)}")
    
    def update_memory(self, memory_id: str, content: str) -> Dict[str, Any]:
        """Update a memory.
        
        Args:
            memory_id: Memory ID.
            content: New content.
            
        Returns:
            Updated memory information.
        """
        url = f"{self.base_url}/api/memories/{memory_id}"
        data = {
            'content': content
        }
        
        try:
            response = self.session.put(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success'):
                raise MemoryClassificationError(result.get('error', 'Failed to update memory'))
            
            return result['data']
        except requests.RequestException as e:
            raise MemoryClassificationError(f"API request failed: {str(e)}")
        except Exception as e:
            raise MemoryClassificationError(f"Error updating memory: {str(e)}")
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory.
        
        Args:
            memory_id: Memory ID.
            
        Returns:
            True if deletion was successful.
        """
        url = f"{self.base_url}/api/memories/{memory_id}"
        
        try:
            response = self.session.delete(url, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success'):
                raise MemoryClassificationError(result.get('error', 'Failed to delete memory'))
            
            return True
        except requests.RequestException as e:
            raise MemoryClassificationError(f"API request failed: {str(e)}")
        except Exception as e:
            raise MemoryClassificationError(f"Error deleting memory: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics.
        
        Returns:
            System statistics.
        """
        url = f"{self.base_url}/api/stats"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success'):
                raise MemoryClassificationError(result.get('error', 'Unknown error'))
            
            return result['data']
        except requests.RequestException as e:
            raise MemoryClassificationError(f"API request failed: {str(e)}")
        except Exception as e:
            raise MemoryClassificationError(f"Error getting stats: {str(e)}")
    
    def get_plugins(self) -> List[Dict[str, Any]]:
        """Get plugin information.
        
        Returns:
            List of plugins.
        """
        url = f"{self.base_url}/api/plugins"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success'):
                raise MemoryClassificationError(result.get('error', 'Plugin system not available'))
            
            return result['data']
        except requests.RequestException as e:
            raise MemoryClassificationError(f"API request failed: {str(e)}")
        except Exception as e:
            raise MemoryClassificationError(f"Error getting plugins: {str(e)}")
    
    def health_check(self) -> Dict[str, Any]:
        """Health check.
        
        Returns:
            Health check result.
        """
        url = f"{self.base_url}/api/health"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success'):
                raise MemoryClassificationError('Health check failed')
            
            return result
        except requests.RequestException as e:
            raise MemoryClassificationError(f"API request failed: {str(e)}")
        except Exception as e:
            raise MemoryClassificationError(f"Error during health check: {str(e)}")
    
    def get_version(self) -> Dict[str, Any]:
        """Get API version information.
        
        Returns:
            Version information.
        """
        url = f"{self.base_url}/api/version"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success'):
                raise MemoryClassificationError('Failed to get version')
            
            return result
        except requests.RequestException as e:
            raise MemoryClassificationError(f"API request failed: {str(e)}")
        except Exception as e:
            raise MemoryClassificationError(f"Error getting version: {str(e)}")
