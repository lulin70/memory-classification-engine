import os
import json
from typing import Dict, List, Optional, Set, Any

class Role:
    def __init__(self, name: str, permissions: List[str]):
        self.name = name
        self.permissions = permissions

class Permission:
    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action

class AccessControlManager:
    def __init__(self, config_file: str = "./config/access_control.json"):
        self.config_file = config_file
        self.roles = self._load_roles()
        self.user_roles = self._load_user_roles()
        self.user_tenants = self._load_user_tenants()
        self.memory_shares = self._load_memory_shares()
        self.permissions_cache = {}
    
    def _load_roles(self) -> Dict[str, Role]:
        """加载角色"""
        if not os.path.exists(self.config_file):
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            return self._create_default_roles()
        
        with open(self.config_file, 'r') as f:
            data = json.load(f)
            roles = {}
            for role_name, role_data in data.get('roles', {}).items():
                roles[role_name] = Role(role_name, role_data.get('permissions', []))
            return roles
    
    def _load_user_roles(self) -> Dict[str, List[str]]:
        """加载用户角色"""
        if not os.path.exists(self.config_file):
            return {}
        
        with open(self.config_file, 'r') as f:
            data = json.load(f)
            return data.get('user_roles', {})
    
    def _load_user_tenants(self) -> Dict[str, str]:
        """加载用户租户映射"""
        if not os.path.exists(self.config_file):
            return {}
        
        with open(self.config_file, 'r') as f:
            data = json.load(f)
            return data.get('user_tenants', {})
    
    def _load_memory_shares(self) -> Dict[str, List[Dict[str, Any]]]:
        """加载记忆共享配置"""
        if not os.path.exists(self.config_file):
            return {}
        
        with open(self.config_file, 'r') as f:
            data = json.load(f)
            return data.get('memory_shares', {})
    
    def _save_config(self):
        """保存配置"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        data = {
            'roles': {
                role_name: {'permissions': role.permissions}
                for role_name, role in self.roles.items()
            },
            'user_roles': self.user_roles,
            'user_tenants': self.user_tenants,
            'memory_shares': self.memory_shares
        }
        with open(self.config_file, 'w') as f:
            json.dump(data, f)
    
    def _create_default_roles(self) -> Dict[str, Role]:
        """创建默认角色"""
        default_roles = {
            'admin': Role('admin', [
                'memory:read', 'memory:write', 'memory:delete', 'memory:share',
                'user:read', 'user:write', 'user:delete', 'user:manage',
                'role:read', 'role:write', 'role:delete',
                'tenant:read', 'tenant:write', 'tenant:delete',
                'audit:read', 'audit:write'
            ]),
            'manager': Role('manager', [
                'memory:read', 'memory:write', 'memory:delete', 'memory:share',
                'user:read', 'user:write',
                'tenant:read'
            ]),
            'user': Role('user', [
                'memory:read', 'memory:write', 'memory:delete',
                'user:read', 'user:write'
            ]),
            'guest': Role('guest', [
                'memory:read'
            ])
        }
        return default_roles
    
    def create_role(self, name: str, permissions: List[str]) -> Role:
        """创建角色"""
        if name in self.roles:
            raise ValueError(f"Role {name} already exists")
        
        self.roles[name] = Role(name, permissions)
        self._save_config()
        return self.roles[name]
    
    def update_role(self, name: str, permissions: List[str]) -> Role:
        """更新角色"""
        if name not in self.roles:
            raise ValueError(f"Role {name} not found")
        
        self.roles[name].permissions = permissions
        self._save_config()
        # 清除缓存
        self.permissions_cache = {}
        return self.roles[name]
    
    def delete_role(self, name: str):
        """删除角色"""
        if name not in self.roles:
            raise ValueError(f"Role {name} not found")
        
        del self.roles[name]
        # 从用户角色中移除
        for user_id, roles in self.user_roles.items():
            if name in roles:
                roles.remove(name)
        self._save_config()
        # 清除缓存
        self.permissions_cache = {}
    
    def assign_role(self, user_id: str, role_name: str):
        """分配角色"""
        if role_name not in self.roles:
            raise ValueError(f"Role {role_name} not found")
        
        if user_id not in self.user_roles:
            self.user_roles[user_id] = []
        
        if role_name not in self.user_roles[user_id]:
            self.user_roles[user_id].append(role_name)
            self._save_config()
            # 清除缓存
            self.permissions_cache.pop(user_id, None)
            # 强制重新计算权限
            self.get_user_permissions(user_id)
    
    def remove_role(self, user_id: str, role_name: str):
        """移除角色"""
        if user_id not in self.user_roles:
            return
        
        if role_name in self.user_roles[user_id]:
            self.user_roles[user_id].remove(role_name)
            self._save_config()
            # 清除缓存
            self.permissions_cache.pop(user_id, None)
    
    def get_user_roles(self, user_id: str) -> List[str]:
        """获取用户角色"""
        roles = self.user_roles.get(user_id, [])
        # 如果用户没有角色，自动分配默认角色
        if not roles:
            self.assign_role(user_id, 'user')
            return ['user']
        return roles
    
    def get_user_permissions(self, user_id: str) -> Set[str]:
        """获取用户权限"""
        if user_id in self.permissions_cache:
            return self.permissions_cache[user_id]
        
        permissions = set()
        roles = self.get_user_roles(user_id)
        for role_name in roles:
            if role_name in self.roles:
                permissions.update(self.roles[role_name].permissions)
        
        self.permissions_cache[user_id] = permissions
        return permissions
    
    def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """检查权限"""
        permission = f"{resource}:{action}"
        user_permissions = self.get_user_permissions(user_id)
        return permission in user_permissions
    
    def check_tenant_isolation(self, user_id: str, tenant_id: str) -> bool:
        """检查租户隔离"""
        # Comment in Chinese removed
        user_tenant_id = self.user_tenants.get(user_id)
        # 如果用户没有租户，使用默认租户
        if not user_tenant_id:
            user_tenant_id = 'default'
        return user_tenant_id == tenant_id
    
    def assign_tenant(self, user_id: str, tenant_id: str):
        """分配租户"""
        self.user_tenants[user_id] = tenant_id
        self._save_config()
    
    def get_user_tenant(self, user_id: str) -> str:
        """获取用户租户"""
        return self.user_tenants.get(user_id, 'default')
    
    def share_memory(self, memory_id: str, user_ids: List[str], permission: str = 'read'):
        """共享记忆"""
        if memory_id not in self.memory_shares:
            self.memory_shares[memory_id] = []
        
        for user_id in user_ids:
            # 检查是否已经共享
            existing_share = next((s for s in self.memory_shares[memory_id] if s['user_id'] == user_id), None)
            if existing_share:
                existing_share['permission'] = permission
            else:
                self.memory_shares[memory_id].append({
                    'user_id': user_id,
                    'permission': permission,
                    'shared_at': os.path.getmtime(__file__)  # 使用文件修改时间作为共享时间
                })
        
        self._save_config()
    
    def unshare_memory(self, memory_id: str, user_id: str):
        """取消共享记忆"""
        if memory_id in self.memory_shares:
            self.memory_shares[memory_id] = [
                s for s in self.memory_shares[memory_id] if s['user_id'] != user_id
            ]
            # 如果没有共享了，删除该记忆的共享配置
            if not self.memory_shares[memory_id]:
                del self.memory_shares[memory_id]
            self._save_config()
    
    def get_memory_shares(self, memory_id: str) -> List[Dict[str, Any]]:
        """获取记忆共享信息"""
        return self.memory_shares.get(memory_id, [])
    
    def check_memory_access(self, user_id: str, memory_id: str, action: str) -> bool:
        """检查记忆访问权限"""
        # 检查用户是否有基本权限
        if not self.check_permission(user_id, 'memory', action):
            return False
        
        # 检查记忆共享权限
        shares = self.get_memory_shares(memory_id)
        for share in shares:
            if share['user_id'] == user_id:
                # 检查共享权限是否包含请求的操作
                if share['permission'] == 'read' and action == 'read':
                    return True
                elif share['permission'] == 'write' and action in ['read', 'write']:
                    return True
                elif share['permission'] == 'delete' and action in ['read', 'write', 'delete']:
                    return True
        
        # 如果没有共享记录，检查用户是否是记忆的创建者或管理员
        # 这里需要与记忆存储系统集成，获取记忆的创建者信息
        # Comment in Chinese removed，实际项目中需要实现完整的权限检查
        return True

# 全局访问控制管理器实例
access_control_manager = AccessControlManager()
