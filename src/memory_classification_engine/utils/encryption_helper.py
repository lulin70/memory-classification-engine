"""Encryption helper for memory storage operations."""

import json
import base64
from typing import Dict, Any, Optional
from memory_classification_engine.privacy.encryption import encryption_manager
from memory_classification_engine.utils.logger import logger


class MemoryEncryptionHelper:
    """Helper class for encrypting and decrypting memory content."""
    
    @staticmethod
    def encrypt_memory_content(memory: Dict[str, Any], 
                                default_password: str = 'default_password') -> bool:
        """Encrypt memory content if it contains sensitive data.
        
        Args:
            memory: The memory dictionary to encrypt (modified in-place).
            default_password: Default password for key generation.
            
        Returns:
            True if encryption was performed, False otherwise.
        """
        try:
            content = memory.get('content', '')
            if not content or not encryption_manager.is_sensitive_data(content):
                return False
            
            # Get or create encryption key
            key_id = memory.get('encryption_key_id')
            if not key_id:
                key_id = encryption_manager.create_key(default_password)
            
            # Encrypt the content
            ciphertext, nonce, tag = encryption_manager.encrypt(content, key_id)
            
            # Store encrypted data
            encrypted_data = {
                'ciphertext': base64.b64encode(ciphertext).decode(),
                'nonce': base64.b64encode(nonce).decode(),
                'tag': base64.b64encode(tag).decode()
            }
            
            # Update memory with encrypted content
            memory['content'] = json.dumps(encrypted_data)
            memory['is_encrypted'] = True
            memory['encryption_key_id'] = key_id
            memory['privacy_level'] = 1
            
            return True
        except Exception as e:
            logger.error(f"Error encrypting memory content: {e}")
            return False
    
    @staticmethod
    def decrypt_memory_content(memory: Dict[str, Any]) -> bool:
        """Decrypt memory content if it is encrypted.
        
        Args:
            memory: The memory dictionary to decrypt (modified in-place).
            
        Returns:
            True if decryption was performed, False otherwise.
        """
        if not memory.get('is_encrypted'):
            return False
        
        try:
            content = memory.get('content', '')
            if not content or not isinstance(content, str):
                return False
            
            # Parse encrypted data
            try:
                encrypted_data = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing encrypted JSON content: {e}")
                return False
            
            # Validate encrypted data structure
            if not isinstance(encrypted_data, dict):
                logger.error("Encrypted data is not a dictionary")
                return False
            
            required_keys = ['ciphertext', 'nonce', 'tag']
            if not all(key in encrypted_data for key in required_keys):
                logger.error(f"Encrypted data missing required keys: {required_keys}")
                return False
            
            # Decode base64 data
            try:
                ciphertext = base64.b64decode(encrypted_data['ciphertext'])
                nonce = base64.b64decode(encrypted_data['nonce'])
                tag = base64.b64decode(encrypted_data['tag'])
            except Exception as e:
                logger.error(f"Error decoding base64 encrypted data: {e}")
                return False
            
            # Get encryption key
            key_id = memory.get('encryption_key_id')
            if not key_id:
                logger.error("No encryption key ID found in memory")
                return False
            
            # Decrypt content
            try:
                decrypted_content = encryption_manager.decrypt(ciphertext, nonce, tag, key_id)
                memory['content'] = str(decrypted_content)
                return True
            except Exception as e:
                logger.error(f"Error decrypting memory content: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Unexpected error decrypting memory: {e}")
            return False
    
    @staticmethod
    def decrypt_memory_list(memories: list) -> int:
        """Decrypt a list of memories in-place.
        
        Args:
            memories: List of memory dictionaries to decrypt.
            
        Returns:
            Number of memories successfully decrypted.
        """
        decrypted_count = 0
        for memory in memories:
            if MemoryEncryptionHelper.decrypt_memory_content(memory):
                decrypted_count += 1
        return decrypted_count