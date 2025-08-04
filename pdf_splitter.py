import os
import re
from PyPDF2 import PdfReader, PdfWriter

def parse_page_range(page_range_str):
    """解析页码范围字符串，返回一个包含所有页码的列表"""
    pages = []
    # 处理类似 "1,3-5,7" 的格式
    for part in page_range_str.split(','):
        part = part.strip()
        if '-' in part:
            # 处理范围，如 "3-5"
            start, end = part.split('-')
            try:
                start = int(start.strip())
                end = int(end.strip())
                # 页码从 1 开始，所以需要调整为 0 索引
                pages.extend(range(start - 1, end))
            except ValueError:
                print(f"无效的页码范围: {part}")
                return []
        else:
            # 处理单个页码，如 "1"
            try:
                pages.append(int(part.strip()) - 1)
            except ValueError:
                print(f"无效的页码: {part}")
                return []
    return pages

def split_pdf(input_path, output_base, page_ranges):
    """根据指定的页码范围拆分 PDF 文件"""
    try:
        # 读取原始 PDF
        with open(input_path, 'rb') as file:
            reader = PdfReader(file)
            total_pages = len(reader.pages)
            
            # 为每个页码范围创建一个新的 PDF
            for i, page_range in enumerate(page_ranges, 1):
                pages = parse_page_range(page_range)
                
                # 验证页码是否有效
                invalid_pages = [p + 1 for p in pages if p < 0 or p >= total_pages]
                if invalid_pages:
                    print(f"页码 {', '.join(map(str, invalid_pages))} 超出了 PDF 的总页数 {total_pages}")
                    continue
                
                if not pages:
                    print(f"忽略空的页码范围: {page_range}")
                    continue
                
                # 创建写入器并添加选定的页面
                writer = PdfWriter()
                for page_num in pages:
                    writer.add_page(reader.pages[page_num])
                
                # 生成输出文件名
                output_filename = f"{output_base}_part{i}.pdf"
                
                # 写入新的 PDF 文件
                with open(output_filename, 'wb') as output_file:
                    writer.write(output_file)
                
                print(f"已创建: {output_filename}，包含页码: {', '.join(map(lambda x: str(x + 1), pages))}")
    
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{input_path}'")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    print("=== PDF 按页拆分工具 ===")
    
    # 获取输入文件路径
    input_file = input("请输入要拆分的 PDF 文件路径: ").strip()
    
    # 检查文件是否存在且为 PDF
    if not os.path.isfile(input_file):
        print(f"错误: 文件 '{input_file}' 不存在")
    elif not input_file.lower().endswith('.pdf'):
        print(f"错误: 文件 '{input_file}' 不是 PDF 文件")
    else:
        # 获取输出文件基本名称
        file_base = os.path.splitext(os.path.basename(input_file))[0]
        output_base = input(f"请输入输出文件的基本名称 (默认: {file_base}_split): ").strip()
        if not output_base:
            output_base = f"{file_base}_split"
        
        # 获取页码范围
        print("\n请输入要拆分的页码范围，格式示例:")
        print("  - 单个页码: 1")
        print("  - 连续页码: 3-5")
        print("  - 组合页码: 1,3-5,7")
        print("  - 多个范围用分号分隔: 1-3;5-7;10")
        
        ranges_input = input("请输入页码范围: ").strip()
        
        # 分割多个页码范围
        page_ranges = [r.strip() for r in ranges_input.split(';') if r.strip()]
        
        if not page_ranges:
            print("错误: 未输入有效的页码范围")
        else:
            split_pdf(input_file, output_base, page_ranges)    