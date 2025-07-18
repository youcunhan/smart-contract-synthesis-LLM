"""
文件处理工具函数

提供文件读写和处理的工具函数。
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional


class FileUtils:
    """文件处理工具类"""
    
    @staticmethod
    def read_text_file(file_path: str, encoding: str = 'utf-8') -> str:
        """读取文本文件"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    
    @staticmethod
    def write_text_file(file_path: str, content: str, encoding: str = 'utf-8'):
        """写入文本文件"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
    
    @staticmethod
    def read_json_file(file_path: str) -> Dict[str, Any]:
        """读取JSON文件"""
        content = FileUtils.read_text_file(file_path)
        return json.loads(content)
    
    @staticmethod
    def write_json_file(file_path: str, data: Dict[str, Any], indent: int = 2):
        """写入JSON文件"""
        content = json.dumps(data, indent=indent, ensure_ascii=False)
        FileUtils.write_text_file(file_path, content)
    
    @staticmethod
    def read_yaml_file(file_path: str) -> Dict[str, Any]:
        """读取YAML文件"""
        content = FileUtils.read_text_file(file_path)
        return yaml.safe_load(content)
    
    @staticmethod
    def write_yaml_file(file_path: str, data: Dict[str, Any]):
        """写入YAML文件"""
        content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
        FileUtils.write_text_file(file_path, content)
    
    @staticmethod
    def list_files(directory: str, pattern: str = "*", recursive: bool = False) -> List[str]:
        """列出目录中的文件"""
        path = Path(directory)
        if not path.exists():
            return []
        
        if recursive:
            files = path.rglob(pattern)
        else:
            files = path.glob(pattern)
        
        return [str(f) for f in files if f.is_file()]
    
    @staticmethod
    def list_directories(directory: str) -> List[str]:
        """列出目录中的子目录"""
        path = Path(directory)
        if not path.exists():
            return []
        
        return [str(d) for d in path.iterdir() if d.is_dir()]
    
    @staticmethod
    def create_directory(directory: str):
        """创建目录"""
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """检查文件是否存在"""
        return Path(file_path).exists()
    
    @staticmethod
    def directory_exists(directory: str) -> bool:
        """检查目录是否存在"""
        return Path(directory).exists()
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """获取文件扩展名"""
        return Path(file_path).suffix
    
    @staticmethod
    def get_file_name(file_path: str) -> str:
        """获取文件名（不含扩展名）"""
        return Path(file_path).stem
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """获取文件大小（字节）"""
        return Path(file_path).stat().st_size
    
    @staticmethod
    def copy_file(source: str, destination: str):
        """复制文件"""
        import shutil
        shutil.copy2(source, destination)
    
    @staticmethod
    def move_file(source: str, destination: str):
        """移动文件"""
        import shutil
        shutil.move(source, destination)
    
    @staticmethod
    def delete_file(file_path: str):
        """删除文件"""
        Path(file_path).unlink()
    
    @staticmethod
    def backup_file(file_path: str, backup_suffix: str = ".backup") -> str:
        """备份文件"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        backup_path = str(path) + backup_suffix
        FileUtils.copy_file(file_path, backup_path)
        return backup_path
    
    @staticmethod
    def find_files_by_content(directory: str, search_text: str, file_pattern: str = "*.sol") -> List[str]:
        """根据内容查找文件"""
        matching_files = []
        
        for file_path in FileUtils.list_files(directory, file_pattern, recursive=True):
            try:
                content = FileUtils.read_text_file(file_path)
                if search_text in content:
                    matching_files.append(file_path)
            except Exception:
                continue
        
        return matching_files
    
    @staticmethod
    def save_contract_with_metadata(
        contract_code: str, 
        output_path: str, 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """保存合约代码和元数据"""
        # 保存合约代码
        FileUtils.write_text_file(output_path, contract_code)
        
        # 保存元数据
        if metadata:
            metadata_path = output_path + ".meta.json"
            FileUtils.write_json_file(metadata_path, metadata)
    
    @staticmethod
    def load_contract_with_metadata(contract_path: str) -> tuple[str, Optional[Dict[str, Any]]]:
        """加载合约代码和元数据"""
        # 加载合约代码
        contract_code = FileUtils.read_text_file(contract_path)
        
        # 加载元数据
        metadata_path = contract_path + ".meta.json"
        metadata = None
        if FileUtils.file_exists(metadata_path):
            metadata = FileUtils.read_json_file(metadata_path)
        
        return contract_code, metadata
    
    @staticmethod
    def create_project_structure(base_path: str, structure: Dict[str, Any]):
        """创建项目目录结构"""
        def create_structure_recursive(path: Path, struct: Dict[str, Any]):
            for name, content in struct.items():
                item_path = path / name
                
                if isinstance(content, dict):
                    # 创建目录
                    item_path.mkdir(parents=True, exist_ok=True)
                    create_structure_recursive(item_path, content)
                elif isinstance(content, str):
                    # 创建文件
                    item_path.parent.mkdir(parents=True, exist_ok=True)
                    FileUtils.write_text_file(str(item_path), content)
                else:
                    # 创建空目录
                    item_path.mkdir(parents=True, exist_ok=True)
        
        base_path_obj = Path(base_path)
        base_path_obj.mkdir(parents=True, exist_ok=True)
        create_structure_recursive(base_path_obj, structure)
    
    @staticmethod
    def get_file_hash(file_path: str, algorithm: str = "md5") -> str:
        """计算文件哈希值"""
        import hashlib
        
        hash_obj = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    @staticmethod
    def compare_files(file1: str, file2: str) -> bool:
        """比较两个文件是否相同"""
        if not FileUtils.file_exists(file1) or not FileUtils.file_exists(file2):
            return False
        
        return FileUtils.get_file_hash(file1) == FileUtils.get_file_hash(file2) 