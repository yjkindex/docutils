import os
import asyncio
import base64
import shutil
import re
import sys
import time

import aiohttp
import g4f.api


def traverse_folder_manually(folder_path, file_list=None):
    if file_list is None:
        file_list = []
    try:
        items = os.listdir(folder_path)
        for item in items:
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                traverse_folder_manually(item_path,file_list)
            else:
                file_list.append(item_path)
    except PermissionError:
        print(f"没有权限访问 {folder_path}")
    return file_list

async def kimi_ocr(image_path,output_path):
    print("requesting: "+image_path)
    with open(image_path, 'rb') as file:
        base64_image = base64.b64encode(file.read()).decode('utf-8')



    api_url = 'http://127.0.0.1:1337/v1/chat/completions'
    request_data = {
        "model":"gpt-4.1",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "只识别图片内容为markdown格式，翻译为中文，不要总结，不要介绍，行内公式用 $ 表示，行间公式用 $$ 表示，公式序号用\\tag表示"
                    }
                ]
            }
        ],
        "use_search": False
    }
    timeout = aiohttp.ClientTimeout(total=600)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(api_url, json=request_data) as response:
            response_data = await response.json()
            print(response_data)
            result= response_data['choices'][0]['message']['content']
            match = re.search(r'```markdown\n(.*?)```', result, re.DOTALL)
            if match:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(match.group(1))
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result)
            print("save to:", output_path)


def copy_directory(source_dir, destination_dir):
    # try:
        # 若目标目录不存在，则创建
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        # 遍历源目录中的所有文件和子目录
        for item in os.listdir(source_dir):
            s = os.path.join(source_dir, item)
            d = os.path.join(destination_dir, item)
            if os.path.isdir(s):
                copy_directory(s, d)
            else:
                shutil.copy2(s, d)
async def main(png_package_path_set,output_dir):

    time.sleep(2)
    os.makedirs(output_dir, exist_ok=True)

    for png_package_path in png_package_path_set.split(","):
        png_package_path.replace('"','').replace("'",'')
        png_package_name = os.path.basename(png_package_path)
        os.makedirs(output_dir+"\\" + png_package_name,exist_ok=True)
        target_dir = output_dir+"\\" + png_package_name
        copy_directory(png_package_path, target_dir)
        request_task= []
        for folder in traverse_folder_manually(target_dir):
            write_path = folder.replace(".png",".md")
            if not os.path.exists(write_path):
                task_obj = asyncio.create_task(kimi_ocr(folder,write_path))
                request_task.append(task_obj)
                await asyncio.sleep(1)
            else:
                print("file exists:", write_path)

        for task_obj in request_task:
            await task_obj


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1],sys.argv[2]))
    # python 
