#!/usr/bin/env python3
"""
下载 HuggingFace 模型的脚本，支持多种镜像站点
"""

import os
import sys

# 设置镜像站点（按优先级排序）
MIRROR_ENDPOINTS = [
    "https://hf-mirror.com",  # 国内镜像
    "https://huggingface.co",  # 官方站点
]

def download_with_mirror(model_id="sentence-transformers/all-MiniLM-L6-v2", local_dir="./models/all-MiniLM-L6-v2"):
    """尝试使用多个镜像站点下载模型"""
    
    # 确保目录存在
    os.makedirs(local_dir, exist_ok=True)
    
    # 尝试每个镜像站点
    for endpoint in MIRROR_ENDPOINTS:
        print(f"\n尝试使用镜像站点: {endpoint}")
        os.environ["HF_ENDPOINT"] = endpoint
        
        try:
            from huggingface_hub import snapshot_download
            
            print(f"开始下载模型: {model_id}")
            print(f"保存到: {local_dir}")
            
            snapshot_download(
                repo_id=model_id,
                local_dir=local_dir,
                local_dir_use_symlinks=False,
                resume_download=True,
                timeout=300  # 5分钟超时
            )
            
            print(f"✅ 模型下载成功！")
            print(f"📁 保存位置: {os.path.abspath(local_dir)}")
            return True
            
        except Exception as e:
            print(f"❌ 使用 {endpoint} 下载失败: {e}")
            continue
    
    print("\n❌ 所有镜像站点都下载失败")
    return False


def download_with_transformers(model_id="sentence-transformers/all-MiniLM-L6-v2"):
    """使用 transformers 库下载模型"""
    
    print(f"\n尝试使用 transformers 下载: {model_id}")
    
    try:
        from transformers import AutoTokenizer, AutoModel
        
        print("下载 tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir="./models")
        
        print("下载 model...")
        model = AutoModel.from_pretrained(model_id, cache_dir="./models")
        
        print("✅ 模型下载成功！")
        return True
        
    except Exception as e:
        print(f"❌ transformers 下载失败: {e}")
        return False


def download_with_sentence_transformers(model_id="sentence-transformers/all-MiniLM-L6-v2"):
    """使用 sentence-transformers 库下载模型"""
    
    print(f"\n尝试使用 sentence-transformers 下载: {model_id}")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        print("下载模型...")
        model = SentenceTransformer(model_id, cache_folder="./models")
        
        print("✅ 模型下载成功！")
        print(f"📁 模型保存位置: {model.cache_folder}")
        return True
        
    except Exception as e:
        print(f"❌ sentence-transformers 下载失败: {e}")
        return False


def main():
    """主函数"""
    model_id = "sentence-transformers/all-MiniLM-L6-v2"
    local_dir = "./models/all-MiniLM-L6-v2"
    
    print("=" * 60)
    print("HuggingFace 模型下载工具")
    print("=" * 60)
    print(f"模型: {model_id}")
    print(f"保存位置: {local_dir}")
    print("=" * 60)
    
    # 方法1: 使用 huggingface_hub + 镜像
    if download_with_mirror(model_id, local_dir):
        return 0
    
    # 方法2: 使用 transformers
    if download_with_transformers(model_id):
        return 0
    
    # 方法3: 使用 sentence-transformers
    if download_with_sentence_transformers(model_id):
        return 0
    
    print("\n" + "=" * 60)
    print("所有方法都失败了。建议:")
    print("1. 检查网络连接")
    print("2. 使用代理/VPN")
    print("3. 手动下载模型文件")
    print("=" * 60)
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
