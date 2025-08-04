import os
import argparse
from PyPDF2 import PdfReader, PdfWriter, PageObject

def merge_pdfs(input_pdfs, output_pdf, add_top_level_bookmarks=True):
    """
    合并多个 PDF 文件并选择性地添加顶级书签
    
    参数:
    input_pdfs (list): 输入 PDF 文件路径列表
    output_pdf (str): 输出 PDF 文件路径
    add_top_level_bookmarks (bool): 是否为每个输入 PDF 添加顶级书签
    """
    pdf_writer = PdfWriter()
    page_offset = 0
    
    for pdf_path in input_pdfs:
        if not os.path.exists(pdf_path):
            print(f"警告: 文件 '{pdf_path}' 不存在，已跳过。")
            continue
        
        try:
            pdf_reader = PdfReader(pdf_path)
            num_pages = len(pdf_reader.pages)
            
            # 添加所有页面到输出 PDF
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                pdf_writer.add_page(page)
            
            # 获取文件名作为书签标题
            pdf_name = os.path.basename(pdf_path)
            pdf_name = os.path.splitext(pdf_name)[0]
            
            # 添加顶级书签（如果需要）
            if add_top_level_bookmarks:
                top_level_bookmark = pdf_writer.add_outline_item(pdf_name, page_offset)
            else:
                top_level_bookmark = None
            
            # 复制原始书签并调整页码
            if pdf_reader.outline:
                copy_bookmarks(pdf_reader, pdf_writer, pdf_reader.outline, parent=top_level_bookmark, page_offset=page_offset)
            
            # 更新页面偏移量
            page_offset += num_pages
            
        except Exception as e:
            print(f"警告: 处理文件 '{pdf_path}' 时出错: {str(e)}，已跳过。")
    
    # 写入合并后的 PDF
    if not pdf_writer.pages:
        print("错误: 没有有效的页面可合并。")
        return
    
    try:
        with open(output_pdf, 'wb') as out:
            pdf_writer.write(out)
        print(f"成功合并 {len(input_pdfs)} 个 PDF 文件到 '{output_pdf}'")
    except Exception as e:
        print(f"错误: 写入文件 '{output_pdf}' 时出错: {str(e)}")

def copy_bookmarks(reader, writer, outlines, parent=None, page_offset=0):
    """
    递归复制书签并调整页码
    
    参数:
    reader (PdfReader): 源 PDF 阅读器
    writer (PdfWriter): 目标 PDF 写入器
    outlines (list): 当前级别的书签列表
    parent: 父级书签
    page_offset (int): 页码偏移量
    """
    for outline in outlines:
        if isinstance(outline, list):
            # 递归处理子书签
            copy_bookmarks(reader, writer, outline, parent=parent, page_offset=page_offset)
        else:
            try:
                # 获取原始书签的页码
                if hasattr(outline, 'page') and outline.page is not None:
                    page_number = reader.get_page_number(outline.page)
                    # 创建新书签
                    title = outline.title if hasattr(outline, 'title') else "未命名书签"
                    new_bookmark = writer.add_outline_item(title, page_number + page_offset, parent=parent)
                    
                    # 如果有子书签，递归处理
                    if hasattr(outline, 'children') and outline.children:
                        copy_bookmarks(reader, writer, outline.children, parent=new_bookmark, page_offset=page_offset)
            except Exception as e:
                print(f"警告: 复制书签时出错: {str(e)}，已跳过。")

def main():
    parser = argparse.ArgumentParser(description='合并多个 PDF 文件并更新书签')
    parser.add_argument('-o', '--output', required=True, help='输出 PDF 文件路径')
    parser.add_argument('-t', '--no-top-level', action='store_true', help='不添加顶级书签')
    parser.add_argument('pdfs', nargs='+', help='输入 PDF 文件路径列表')

    
    args = parser.parse_args()
    # python pdf_merger.py -o merged.pdf file1.pdf file2.pdf file3.pdf
    # 检查输出文件目录是否存在
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            print(f"错误: 创建输出目录时出错: {str(e)}")
            return
    
    merge_pdfs(args.pdfs, args.output, not args.no_top_level)

if __name__ == "__main__":
    main()    