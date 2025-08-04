import os
import base64
import threading
import queue
from pathlib import Path
from g4f.client import Client
from tqdm import tqdm

def split_markdown_by_paragraphs(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"错误：未找到文件 '{file_path}'")
        return []
    except Exception as e:
        print(f"错误：读取文件时发生错误 - {e}")
        return []

    paragraphs = content.split('\n')
    paragraphs = [p.strip() for p in paragraphs]
    return [p for p in paragraphs if p]

def translate_markdown_paragraphs(paragraph):
    print(f"正在翻译段落：{paragraph}")
    try:
        client = Client()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": paragraph,
                        },
                        {
                            "type": "text",
                            "text": "翻译英文内容为中文markdown格式，不要总结，不要介绍，行内公式用 $ 表示，行间公式用 $$ 表示，公式序号用\\tag表示",
                        },
                    ],
                }
            ],
            web_search=False,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(e)
        return translate_markdown_paragraphs(paragraph)

    

def translation_worker(task_queue, result_queue, progress_bar):
    while True:
        task = task_queue.get()
        if task is None:  # 退出信号
            break
        index, paragraph = task
        try:
            translated = translate_markdown_paragraphs(paragraph)
            result_queue.put((index, translated))
        except Exception as e:
            print(f"段落 {index} 翻译失败: {e}")
            result_queue.put((index, None))
        finally:
            progress_bar.update(1)
            task_queue.task_done()

def process_markdown_file(input_file, output_file, num_threads=4):
    paragraphs = split_markdown_by_paragraphs(input_file)
    if not paragraphs:
        print(f"警告：文件 '{input_file}' 中没有可处理的段落")
        return
    
    task_queue = queue.Queue()
    result_queue = queue.Queue()
    
    # 初始化进度条
    with tqdm(total=len(paragraphs), desc="翻译进度") as progress_bar:
        # 创建并启动工作线程
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(
                target=translation_worker,
                args=(task_queue, result_queue, progress_bar),
                daemon=True
            )
            t.start()
            threads.append(t)
        
        # 添加任务到队列
        for i, para in enumerate(paragraphs):
            task_queue.put((i, para))
        
        # 等待所有任务完成
        task_queue.join()
        
        # 发送退出信号给所有工作线程
        for _ in range(num_threads):
            task_queue.put(None)
        
        # 等待所有线程结束
        for t in threads:
            t.join()
    
    # 收集并排序结果
    results = [None] * len(paragraphs)
    while not result_queue.empty():
        index, content = result_queue.get()
        if content is not None:
            results[index] = content
    
    # 过滤掉失败的翻译
    translated_content_list = [r for r in results if r is not None]
    if not translated_content_list:
        print(f"错误：所有段落翻译均失败，未生成输出文件")
        return
    
    translated_content = "\n\n".join(translated_content_list)
    
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(translated_content)
        print(f"成功处理文件 '{input_file}'，结果已保存到 '{output_file}'")
    except Exception as e:
        print(f"错误：写入文件 '{output_file}' 时发生错误 - {e}")

if __name__ == "__main__":
    for fp in os.listdir(r"D:\project\QCDReview\50 years of QCD"):
        input_file = os.path.join(r"D:\project\QCDReview\50 years of QCD", fp)
        output_file = os.path.join(r"D:\project\QCDReview\50 years of QCD", fp).replace(".md", ".zh.md")
        num_threads = 4  # 默认使用4个线程，可以根据需要调整
        
        if not os.path.exists(input_file):
            print(f"错误：输入文件 '{input_file}' 不存在")
        else:
            process_markdown_file(input_file, output_file, num_threads)    