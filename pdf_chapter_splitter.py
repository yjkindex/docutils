import os
import re
import fitz  # PyMuPDF库，用于PDF处理
from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
import argparse

def extract_bookmarks(pdf_path):
    """提取PDF中的书签信息"""
    bookmarks = []
    try:
        with fitz.open(pdf_path) as doc:
            toc = doc.get_toc()  # 获取目录
            for entry in toc:
                level, title, page = entry
                # 页码在PyMuPDF和PyPDF2中相差1
                bookmarks.append((level, title, page - 1))
        return bookmarks
    except Exception as e:
        print(f"提取书签时出错: {e}")
        return []

def split_pdf_by_bookmarks(pdf_path, output_dir=None, prefix="chapter_", clean_names=True):
    """根据书签拆分PDF"""
    if not output_dir:
        output_dir = os.path.splitext(pdf_path)[0] + "_chapters"

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 读取PDF
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)

        # 提取书签
        bookmarks = extract_bookmarks(pdf_path)
        if not bookmarks:
            print("未找到书签信息，无法按章节拆分。")
            return False

        print(f"找到 {len(bookmarks)} 个书签: {bookmarks}")

        # 准备拆分点
        split_points = []
        prev_page = 0

        # 处理每个书签
        for i, (level, title, page) in enumerate(bookmarks):
            # 清理标题中的非法字符
            if clean_names:
                safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)
            else:
                safe_title = title

            # 如果标题为空，生成默认标题
            if not safe_title.strip():
                safe_title = f"chapter_{i+1}"

            # 确定章节的结束页
            if i < len(bookmarks) - 1:
                end_page = bookmarks[i+1][2]
            else:
                end_page = num_pages

            # 章节信息
            chapter_info = {
                'title': safe_title,
                'start_page': page,
                'end_page': end_page,
                'level': level
            }
            split_points.append(chapter_info)

        # 拆分PDF
        print(f"开始拆分为 {len(split_points)} 个章节...")
        for i, chapter in enumerate(tqdm(split_points, desc="正在拆分")):
            writer = PdfWriter()

            # 添加页面
            for page_num in range(chapter['start_page'], chapter['end_page']):
                writer.add_page(reader.pages[page_num])

            # 生成输出文件名
            if len(split_points) > 1:
                output_filename = f"{prefix}{i+1:03d}_{chapter['title']}.pdf"
            else:
                output_filename = f"{prefix}{chapter['title']}.pdf"

            output_path = os.path.join(output_dir, output_filename)

            # 写入文件
            with open(output_path, 'wb') as output_pdf:
                writer.write(output_pdf)

        print(f"拆分完成! 共生成 {len(split_points)} 个文件，保存在: {output_dir}")
        return True

    except Exception as e:
        print(f"拆分PDF时出错: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='按PDF书签拆分章节')
    parser.add_argument('pdf_path', help='PDF文件路径')
    parser.add_argument('-o', '--output', help='输出目录，默认为"原文件名_chapters"')
    parser.add_argument('-p', '--prefix', default='chapter_', help='输出文件前缀，默认为"chapter_"')
    parser.add_argument('--keep-names', action='store_true', help='保留原书签名称中的特殊字符')
    # python pdf_chapter_splitter.py example.pdf -o output_dir -p my_chapter_ --keep-names
    args = parser.parse_args()

    # 检查文件是否存在
    if not os.path.exists(args.pdf_path):
        print(f"错误: 文件 {args.pdf_path} 不存在")
        return

    # 检查文件是否为PDF
    if not args.pdf_path.lower().endswith('.pdf'):
        print(f"错误: 文件 {args.pdf_path} 不是PDF文件")
        return

    # 执行拆分
    split_pdf_by_bookmarks(
        args.pdf_path,
        output_dir=args.output,
        prefix=args.prefix,
        clean_names=not args.keep_names
    )

if __name__ == "__main__":
    main()

    # python pdf_chapter_splitter.py example.pdf -o output_dir -p my_chapter_ --keep-names