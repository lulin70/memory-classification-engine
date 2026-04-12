import os
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from typing import Optional, Dict, Tuple

class EncryptionManager:
    def __init__(self, key_file: str = "./config/encryption_keys.json"):
        self.key_file = key_file
        self.keys = self._load_keys()
        self.backend = default_backend()
    
    def _load_keys(self) -> Dict[str, str]:
        """加载密钥"""
        if not os.path.exists(self.key_file):
            os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
            return {}
        
        with open(self.key_file, 'r') as f:
            return json.load(f)
    
    def _save_keys(self):
        """保存密钥"""
        os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
        with open(self.key_file, 'w') as f:
            json.dump(self.keys, f)
    
    def _generate_key(self, password: str, salt: bytes) -> bytes:
        """生成密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        return kdf.derive(password.encode())
    
    def generate_key_id(self) -> str:
        """生成密钥ID"""
        return os.urandom(16).hex()
    
    def create_key(self, password: str) -> str:
        """创建新密钥"""
        salt = os.urandom(16)
        key = self._generate_key(password, salt)
        key_id = self.generate_key_id()
        
        self.keys[key_id] = {
            "key": key.hex(),
            "salt": salt.hex()
        }
        self._save_keys()
        return key_id
    
    def get_key(self, key_id: str) -> Optional[bytes]:
        """获取密钥"""
        if key_id not in self.keys:
            return None
        
        key_data = self.keys[key_id]
        return bytes.fromhex(key_data["key"])
    
    def rotate_key(self, old_key_id: str, new_password: str) -> str:
        """轮换密钥"""
        if old_key_id not in self.keys:
            raise ValueError("Old key not found")
        
        new_key_id = self.create_key(new_password)
        del self.keys[old_key_id]
        self._save_keys()
        return new_key_id
    
    def backup_keys(self, backup_file: str):
        """备份密钥"""
        with open(backup_file, 'w') as f:
            json.dump(self.keys, f)
    
    def restore_keys(self, backup_file: str):
        """恢复密钥"""
        with open(backup_file, 'r') as f:
            self.keys = json.load(f)
        self._save_keys()
    
    def encrypt(self, data: str, key_id: str) -> Tuple[bytes, bytes, bytes]:
        """加密数据"""
        key = self.get_key(key_id)
        if key is None:
            raise ValueError("Key not found")
        
        nonce = os.urandom(12)
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data.encode()) + encryptor.finalize()
        
        return ciphertext, nonce, encryptor.tag
    
    def decrypt(self, ciphertext: bytes, nonce: bytes, tag: bytes, key_id: str) -> str:
        """解密数据"""
        key = self.get_key(key_id)
        if key is None:
            raise ValueError("Key not found")
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce, tag),
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext.decode()
    
    def is_sensitive_data(self, data: str) -> bool:
        """判断是否为敏感数据"""
        sensitive_patterns = [
            r'\b\d{16,}\b',  # 信用卡号
            r'\b\d{9,12}\b',  # 身份证号
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # 邮箱
            r'\b\d{3}-\d{3}-\d{4}\b',  # 电话号码
            r'\b\d{5}(-\d{4})?\b',  # 邮编
            r'\bhttps?://\S+\b',  # Comment in Chinese removed
        ]
        
        import re
        for pattern in sensitive_patterns:
            if re.search(pattern, data):
                return True
        
        return False

# 全局加密管理器实例
encryption_manager = EncryptionManager()
