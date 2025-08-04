import os
import re
import fitz  # PyMuPDF库，用于PDF处理
import argparse
from tqdm import tqdm

def extract_bookmarks(pdf_path):
    """提取PDF中的书签信息"""
    try:
        with fitz.open(pdf_path) as doc:
            toc = doc.get_toc()  # 获取目录
            return toc
    except Exception as e:
        print(f"提取书签时出错: {e}")
        return []

def save_bookmarks_to_file(bookmarks, output_file):
    """将书签保存到文本文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in bookmarks:
            level, title, page = item
            indent = '  ' * (level - 1)  # 根据级别缩进
            f.write(f"{indent}{title}@{page}\n")
    print(f"书签已保存到 {output_file}")

def load_bookmarks_from_file(file_path):
    """从文本文件加载书签"""
    bookmarks = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # 计算缩进级别
                indent_match = re.match(r'^(\s*)', line)
                indent = indent_match.group(1) if indent_match else ''
                level = len(indent) // 2 + 1  # 假设两个空格为一个缩进级别
                
                # 提取标题和页码
                content = line.lstrip()
                if '@' in content:
                    title, page = content.rsplit('@', 1)
                    try:
                        page_num = int(page.strip())
                        bookmarks.append([level, title.strip(), page_num])
                    except ValueError:
                        print(f"警告: 无效的页码 '{page}'，跳过这一行: {line}")
                else:
                    print(f"警告: 格式不正确，跳过这一行: {line}")
        return bookmarks
    except Exception as e:
        print(f"加载书签时出错: {e}")
        return []

def update_pdf_bookmarks(pdf_path, new_bookmarks, output_path=None):
    """更新PDF的书签"""
    if not output_path:
        base, ext = os.path.splitext(pdf_path)
        output_path = f"{base}_updated{ext}"
    
    try:
        with fitz.open(pdf_path) as doc:
            # 清除原有书签
            doc.set_toc([])
            
            # 添加新书签
            doc.set_toc(new_bookmarks)
            
            # 保存修改后的PDF
            doc.save(output_path)
        
        print(f"PDF书签已更新并保存到 {output_path}")
        return True
    except Exception as e:
        print(f"更新书签时出错: {e}")
        return False

def generate_sample_bookmarks():
    """生成示例书签用于演示"""
    return [
        [1, "第一章：引言", 1],
        [2, "1.1 背景", 3],
        [2, "1.2 目标", 5],
        [1, "第二章：方法", 10],
        [2, "2.1 材料", 12],
        [2, "2.2 步骤", 15],
        [3, "2.2.1 准备工作", 15],
        [3, "2.2.2 实验过程", 17],
    ]

def main():
    parser = argparse.ArgumentParser(description='PDF目录(书签)编辑工具')
    parser.add_argument('pdf_path', help='PDF文件路径')
    parser.add_argument('-o', '--output', help='输出PDF文件路径，默认为原文件名_updated.pdf')
    parser.add_argument('--extract', help='提取书签并保存到指定文件')
    parser.add_argument('--import', dest='import_file', help='从文件导入书签并更新PDF')
    parser.add_argument('--sample', action='store_true', help='使用示例书签更新PDF')
    parser.add_argument('--delete', action='store_true', help='删除所有书签')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.pdf_path):
        print(f"错误: 文件 {args.pdf_path} 不存在")
        return
    
    # 检查文件是否为PDF
    if not args.pdf_path.lower().endswith('.pdf'):
        print(f"错误: 文件 {args.pdf_path} 不是PDF文件")
        return
    
    # 提取书签
    if args.extract:
        bookmarks = extract_bookmarks(args.pdf_path)
        if bookmarks:
            save_bookmarks_to_file(bookmarks, args.extract)
        else:
            print("未找到书签信息")
        return
    
    # 导入书签
    if args.import_file:
        new_bookmarks = load_bookmarks_from_file(args.import_file)
        if new_bookmarks:
            update_pdf_bookmarks(args.pdf_path, new_bookmarks, args.output)
        else:
            print("未能加载有效书签")
        return
    
    # 使用示例书签
    if args.sample:
        sample_bookmarks = generate_sample_bookmarks()
        update_pdf_bookmarks(args.pdf_path, sample_bookmarks, args.output)
        return
    
    # 删除所有书签
    if args.delete:
        update_pdf_bookmarks(args.pdf_path, [], args.output)
        return
    
    # 如果没有提供任何操作参数，显示帮助信息
    if not any(vars(args).values()):
        parser.print_help()

if __name__ == "__main__":
    main()
    # python pdf_bookmark_editor.py path/to/your/pdf.pdf --delete -o output.pdf
    # python pdf_bookmark_editor.py path/to/your/pdf.pdf --extract bookmarks.txt
    # python pdf_bookmark_editor.py path/to/your/pdf.pdf --import new_bookmarks.txt