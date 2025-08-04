import os
import re

def create_chapter_index_directories(content, root_path):
    """
    按章节在同级目录中的序号（index）创建文件夹，支持任意层级嵌套
    
    参数:
        content: 包含层级目录的字符串（缩进表示层级）
        root_path: 根目录路径
    """
    # 确保根目录存在
    if not os.path.exists(root_path):
        os.makedirs(root_path)
        print(f"创建根目录: {root_path}")
    
    # 解析每一行，获取层级、标题和页码（页码仅用于原始信息保留，不参与命名）
    items = []
    for line in content.split('\n'):
        line = line.strip('\n').rstrip()
        if not line:
            continue
        
        # 计算层级（2个空格=1级）
        indent_count = len(line) - len(line.lstrip(' '))
        level = indent_count // 2
        text = line.lstrip(' ')
        
        # 分离标题和页码（页码不影响命名，仅作为原始信息）
        if '@' in text:
            title = text.split('@', 1)[0].strip()
        else:
            title = text.strip()
        
        # 处理标题中的特殊字符
        safe_title = re.sub(r'[\/:*?"<>|]', '-', title)
        items.append((level, safe_title))
    
    # 递归创建目录，同时跟踪同级目录的序号（index）
    def build_hierarchy(items, index=0, current_level=0, parent_path=root_path, sibling_count=None):
        """
        递归构建目录结构，sibling_count用于跟踪当前层级的兄弟节点数量（序号）
        """
        # 初始化当前层级的兄弟节点计数器（从1开始）
        if sibling_count is None:
            sibling_count = 1
        
        while index < len(items):
            item_level, item_title = items[index]
            
            if item_level == current_level:
                # 当前层级的节点：用同级序号命名
                dir_name = f"[{sibling_count}] {item_title}"
                current_path = os.path.join(parent_path, dir_name)
                
                if not os.path.exists(current_path):
                    os.makedirs('\\?\\' +current_path)
                    print(f"创建目录: {current_path}")
                else:
                    print(f"目录已存在: {current_path}")
                
                # 序号+1，处理下一个同级节点
                sibling_count += 1
                index += 1
            
            elif item_level > current_level:
                # 子层级节点：递归创建，重置子层级的序号为1
                index = build_hierarchy(
                    items,
                    index=index,
                    current_level=item_level,
                    parent_path=current_path,
                    sibling_count=1  # 子层级从1开始计数
                )
            
            else:
                # 回到上一级：返回当前index，让父级继续处理
                return index
        
        return index  # 所有节点处理完毕
    
    # 开始构建目录
    build_hierarchy(items)
    print("\n所有层级目录创建完成!")

# 调用函数（使用原问题中的内容，也可替换为上面的测试内容）
content = open('bookmarks.txt', 'r', encoding='utf-8').read()  # 从文件读取内容
# 执行创建（支持任意层级）
create_chapter_index_directories(content, root_path='../../note')