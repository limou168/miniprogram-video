import yaml
import os


def read_yaml(file_path):
    """
    读取yaml文件
    :param file_path: yaml文件路径
    :return: yaml文件内容
    """
    # 1. 获取当前文件 (util.py) 的绝对路径
    current_file_path = os.path.abspath(__file__)
    
    # 2. 获取 common 文件夹的路径
    common_dir = os.path.dirname(current_file_path)
    
    # 3. 获取项目根目录的路径 (向上一级，也就是 auto_test 文件夹)
    root_dir = os.path.dirname(common_dir)
    
    # 4. 拼接完整路径
    full_path = os.path.join(root_dir, file_path)
    
    # 5. (可选) 打印出来看看路径对不对，方便调试
    print(f"正在读取文件: {full_path}")
    
    # 6. 读取文件
    with open(full_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)