import json
import re
import sys
import fitz
from pathlib import Path
from pdf2image import convert_from_path


def format_filename(filename):
    """
    格式化文件名，去除非法字符
    """
    illegal_filter = r'[\/:*?"<>|]'
    return re.search(r'^\s*(.*?)\s*$', re.sub(illegal_filter, '', filename)).group(1)


def get_pdf_info(pdf_path):
    """
    获取 PDF 文件的信息，包括大纲、字体信息、插入的图像等
    """
    def r_get_outline(outline, child_type, parent_key=None, parent_list=None):
        if parent_list is None:
            parent_list = []
        if parent_key is None:
            parent_key = {}
        info = {
            "page": outline.page,
            "title": outline.title
        }
        if child_type == "down":
            parent_list = [info]
            parent_key["down"] = parent_list
            new_parent_key = info
        elif child_type == "next":
            parent_list.append(info)
            new_parent_key = info
        else:
            parent_list.append(info)
            new_parent_key = info
        if outline.down:
            r_get_outline(outline.down, "down", new_parent_key, parent_list)
        if outline.next:
            r_get_outline(outline.next, "next", new_parent_key, parent_list)
        return parent_list

    pdf_path = Path(pdf_path)
    try:
        doc = fitz.open(pdf_path)
        info = {
            "FontInfos": doc.FontInfos,
            "InsertedImages": doc.InsertedImages,
            "Pages": doc.page_count,
            "ShownPages": doc.ShownPages,
            "metadata": doc.metadata
        }
        info["Outline"] = r_get_outline(doc.outline, "re", {}, [])
        info["metadata"]["title"] = format_filename(pdf_path.stem)
        doc.close()
        return info
    except Exception as e:
        print(f"获取 PDF 信息时出错: {e}")
        return {
            "Outline": [{"page": 0, "title": pdf_path.stem}],
            "metadata": {"title": pdf_path.stem},
            "Pages": 0
        }


def flatten_outline(outline, parent_path=""):
    """
    扁平化大纲结构，添加路径信息
    """
    flattened = []
    for item in outline:
        item["path"] = parent_path / format_filename(item["title"])
        flattened.append(item)
        if "down" in item:
            flattened.extend(flatten_outline(item["down"], item["path"]))
    return flattened


def save_pngs(pdf_info, images, output_dir):
    """
    将 PDF 页面保存为 PNG 图像
    """
    output_dir = Path(output_dir)
    pdf_title = format_filename(pdf_info["metadata"]["title"])
    main_dir = output_dir / pdf_title

    def add_long_path_prefix(path):
        if isinstance(path, Path) and not str(path).startswith("\\\\?\\"):
            return Path(r'\\?\{}'.format(path.resolve()))
        return path

    main_dir = add_long_path_prefix(main_dir)
    main_dir.mkdir(parents=True, exist_ok=True)

    flattered_outline = flatten_outline(pdf_info["Outline"], main_dir)

    for i in range(len(flattered_outline) - 1):
        folder_path = flattered_outline[i]["path"]
        folder_path = add_long_path_prefix(folder_path)
        folder_path.mkdir(parents=True, exist_ok=True)
        for j in range(flattered_outline[i]["page"], flattered_outline[i + 1]["page"]):
            image_path = folder_path / f"{j}.png"
            image_path = add_long_path_prefix(image_path)
            images[j].save(image_path)

    last_folder = flattered_outline[-1]["path"]
    last_folder = add_long_path_prefix(last_folder)
    last_folder.mkdir(parents=True, exist_ok=True)
    for j in range(flattered_outline[-1]["page"], pdf_info["Pages"]):
        image_path = last_folder / f"{j}.png"
        image_path = add_long_path_prefix(image_path)
        images[j].save(image_path)


def main(pdf_path_set, output_dir):
    """
    主函数，处理多个 PDF 文件并保存为 PNG 图像
    """
    for pdf_path in pdf_path_set.split(","):
        pdf_path = Path(pdf_path.replace('"', '').replace("'", ""))
        try:
            images = convert_from_path(pdf_path, use_pdftocairo=True, thread_count=10)
            pdf_info = get_pdf_info(pdf_path)
            json_path = pdf_path.with_suffix('.json')
            with open(json_path, "w") as f:
                f.write(json.dumps(pdf_info, indent=4))
            save_pngs(pdf_info, images, output_dir)
        except Exception as e:
            print(f"处理 {pdf_path} 时出错: {e}")
    return True


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("用法: python script.py <pdf_path_set> <output_dir>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
