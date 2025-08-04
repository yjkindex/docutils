import os
import base64
import threading
import queue
from pathlib import Path
from g4f.client import Client
from tqdm import tqdm


def process_image(image_path, output_dir, client, progress_queue=None):
    """处理单个图片文件，发送OCR请求并保存结果"""
    try:
        # 读取并编码图片
        with open(image_path, "rb") as file:
            base64_image = base64.b64encode(file.read()).decode("utf-8")

        # 构建请求
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            },
                        },
                        {
                            "type": "text",
                            "text": "只识别图片内容为markdown格式，翻译为中文，不要总结，不要介绍，行内公式用 $ 表示，行间公式用 $$ 表示，公式序号用\\tag表示",
                        },
                    ],
                }
            ],
            web_search=False,
        )

        # 保存结果
        image_name = os.path.basename(image_path)
        output_name = os.path.splitext(image_name)[0] + ".md"
        output_path = os.path.join(output_dir, output_name)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(response.choices[0].message.content)

        if progress_queue:
            progress_queue.put(1)  # 通知进度更新
        return True, f"成功处理: {image_name}"
    except Exception as e:
        if progress_queue:
            progress_queue.put(0)  # 通知处理失败
        return False, f"处理失败 {image_path}: {str(e)}"


def worker(input_queue, output_dir, client, progress_queue=None):
    """工作线程函数，从队列中获取任务并处理"""
    while True:
        image_path = input_queue.get()
        if image_path is None:  # 结束信号
            break
        success, message = process_image(image_path, output_dir, client, progress_queue)
        print(message)
        input_queue.task_done()


def main(input_dir, output_dir, num_threads=4):
    """主函数，协调多线程处理图片"""
    # 确保输出目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 获取所有PNG图片
    image_files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.lower().endswith(".png")
    ]

    if not image_files:
        print("未找到PNG图片")
        return

    print(f"找到 {len(image_files)} 张图片")

    # 创建工作队列
    work_queue = queue.Queue()
    progress_queue = queue.Queue()

    # 添加所有图片到队列
    for image_path in image_files:
        work_queue.put(image_path)

    # 添加结束信号
    for _ in range(num_threads):
        work_queue.put(None)

    # 创建并启动工作线程
    client = Client()  # 每个线程共享同一个客户端实例
    threads = []

    for _ in range(num_threads):
        t = threading.Thread(
            target=worker, args=(work_queue, output_dir, client, progress_queue)
        )
        t.daemon = True
        t.start()
        threads.append(t)

    # 显示进度条
    processed_count = 0
    success_count = 0
    with tqdm(total=len(image_files), desc="处理进度") as pbar:
        while processed_count < len(image_files):
            result = progress_queue.get()
            processed_count += 1
            success_count += result
            pbar.update(1)

    # 等待所有线程完成
    for t in threads:
        t.join()

    print(f"处理完成！成功: {success_count}, 失败: {len(image_files) - success_count}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="多线程图片OCR和翻译工具")
    parser.add_argument("--input", "-i", required=True, help="输入图片文件夹路径")
    parser.add_argument("--output", "-o", required=True, help="输出Markdown文件夹路径")
    parser.add_argument("--threads", "-t", type=int, default=4, help="线程数")

    args = parser.parse_args()

    main(args.input, args.output, args.threads)

    # python gptocr.py -i input_folder -o output_folder -t 4
