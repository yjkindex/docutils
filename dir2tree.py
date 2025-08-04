import os
from pathlib import Path

def generate_directory_tree(root_dir, max_depth=float('inf'), ignore_hidden=True,
                            ignore_patterns=None, show_files=True):
    """
    生成指定目录的文件树

    参数:
    root_dir (str): 根目录路径
    max_depth (int): 最大显示深度，默认为无限大
    ignore_hidden (bool): 是否忽略隐藏文件，默认为True
    ignore_patterns (list): 要忽略的文件或目录名列表，默认为None
    show_files (bool): 是否显示文件，默认为True
    """
    if ignore_patterns is None:
        ignore_patterns = []

    root_path = Path(root_dir)
    if not root_path.exists():
        print(f"错误: 目录 '{root_dir}' 不存在")
        return

    tree = []

    def _generate_tree(path, prefix='', depth=0):
        if depth > max_depth:
            return

        # 检查是否应该忽略当前路径
        if ignore_hidden and path.name.startswith('.'):
            return
        if any(pattern in path.name for pattern in ignore_patterns):
            return

        # 确定当前项的显示前缀
        is_dir = path.is_dir()
        if not is_dir and not show_files:
            return

        # 生成当前项的显示行
        if depth == 0:
            line = f"{path.name}/"
        else:
            line = f"{prefix}  {path.name}"
            if is_dir:
                line += "/"
        tree.append(line)

        # 如果是目录，递归生成子树
        if is_dir:
            children = list(path.iterdir())
            # 按文件夹优先排序
            children.sort(key=lambda x: (not x.is_dir(), x.name))

            for i, child in enumerate(children):
                # 为子项计算新的前缀
                if i == len(children) - 1:
                    new_prefix = f"{prefix}  "
                else:
                    new_prefix = f"{prefix}  "
                _generate_tree(child, new_prefix, depth + 1)

    _generate_tree(root_path)
    return "\n".join(tree)

if __name__ == "__main__":
    # 示例：生成当前目录的文件树
    current_dir = r"C:\Users\root\Downloads\x"
    tree = generate_directory_tree(
        current_dir,
        max_depth=3,
        ignore_hidden=True,
        ignore_patterns=['__pycache__', '.git'],
        show_files=True
    )
    print(tree)