import os
import argparse
from pdf2image import convert_from_path
from PIL import Image
import time

def pdf_to_png(pdf_path, output_dir=None, dpi=300, fmt='png', thread_count=4, progress_callback=None):
    """
    将 PDF 文件转换为 PNG 图片
    
    参数:
        pdf_path (str): PDF 文件路径
        output_dir (str, optional): 输出目录，默认为 PDF 所在目录
        dpi (int, optional): 图像分辨率，默认为 300 DPI
        fmt (str, optional): 输出格式，默认为 'png'
        thread_count (int, optional): 处理线程数，默认为 4
        progress_callback (function, optional): 进度回调函数，接收当前页数和总页数
    """
    # 确保输出目录存在
    if output_dir is None:
        output_dir = os.path.dirname(pdf_path)

    os.makedirs(output_dir, exist_ok=True)

    # 获取 PDF 文件名（不含扩展名）
    pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]

    try:
        # 计算开始时间
        start_time = time.time()

        # 转换 PDF 为图像列表
        images = convert_from_path(
            pdf_path,
            dpi=dpi,
            output_folder=None,  # 设为 None 以便手动保存，确保兼容性
            fmt=fmt,
            thread_count=thread_count,
            use_pdftocairo=True  # 使用 pdftocairo 后端以获得更好的质量
        )

        # 保存图像
        for i, image in enumerate(images, 1):
            image_path = os.path.join(output_dir, f"{pdf_filename}_page{i}.{fmt}")
            image.save(image_path, fmt.upper())

            # 调用进度回调
            if progress_callback:
                progress_callback(i, len(images), pdf_path)

        # 计算耗时
        elapsed_time = time.time() - start_time
        print(f"转换完成: {pdf_path} -> {len(images)} 页, 耗时: {elapsed_time:.2f} 秒")

        return len(images)

    except Exception as e:
        print(f"错误: 转换 {pdf_path} 时发生错误: {e}")
        return 0

def convert_pdfs(input_path, output_dir=None, dpi=300, fmt='png', thread_count=4):
    """
    转换单个 PDF 或目录中的所有 PDF
    
    参数:
        input_path (str): PDF 文件路径或包含 PDF 的目录
        output_dir (str, optional): 输出目录
        dpi (int, optional): 图像分辨率
        fmt (str, optional): 输出格式
        thread_count (int, optional): 处理线程数
    """
    if os.path.isfile(input_path) and input_path.lower().endswith('.pdf'):
        # 处理单个 PDF 文件
        pdf_to_png(input_path, output_dir, dpi, fmt, thread_count)

    elif os.path.isdir(input_path):
        # 处理目录中的所有 PDF 文件
        pdf_files = [f for f in os.listdir(input_path) if f.lower().endswith('.pdf')]

        if not pdf_files:
            print(f"错误: 目录 '{input_path}' 中未找到 PDF 文件")
            return

        total_pdfs = len(pdf_files)

        for i, pdf_file in enumerate(pdf_files, 1):
            pdf_path = os.path.join(input_path, pdf_file)

            # 如果指定了输出目录，为每个 PDF 创建单独的子目录
            if output_dir:
                pdf_output_dir = os.path.join(output_dir, os.path.splitext(pdf_file)[0])
            else:
                pdf_output_dir = None

            print(f"正在处理 {i}/{total_pdfs}: {pdf_file}")
            pdf_to_png(pdf_path, pdf_output_dir, dpi, fmt, thread_count)
    else:
        print(f"错误: 路径 '{input_path}' 不是有效的文件或目录")

def progress_callback(current, total, pdf_path):
    """进度回调函数"""
    progress = (current / total) * 100
    print(f"\r{pdf_path}: 正在处理第 {current}/{total} 页 ({progress:.1f}%)", end='')
    if current == total:
        print()  # 完成后换行

if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='将 PDF 转换为 PNG 图片')
    parser.add_argument('input', help='PDF 文件路径或包含 PDF 的目录')
    parser.add_argument('-o', '--output', help='输出目录')
    parser.add_argument('-d', '--dpi', type=int, default=300, help='图像分辨率 (默认: 300 DPI)')
    parser.add_argument('-t', '--threads', type=int, default=4, help='处理线程数 (默认: 4)')
    # python pdf_to_png.py input.pdf -o output_dir -d 300 -t 4

    # 解析命令行参数
    args = parser.parse_args()

    print("=== PDF 转 PNG 工具 ===")
    print(f"输入: {args.input}")
    print(f"输出目录: {args.output if args.output else '与输入相同'}")
    print(f"DPI: {args.dpi}")
    print(f"线程数: {args.threads}")
    print("------------------------")

    # 执行转换
    convert_pdfs(args.input, args.output, args.dpi, 'png', args.threads)    