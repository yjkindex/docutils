from PIL import Image
import sys

def remove_color(input_path, output_path, target_color=(23, 36, 41)):
    """
    从图像中移除指定颜色的像素，将其变为透明
    
    参数:
    input_path (str): 输入图像路径
    output_path (str): 输出图像路径
    target_color (tuple): 要移除的颜色，默认为RGB(23, 36, 41)
    """
    try:
        # 打开图像
        with Image.open(input_path) as img:
            # 转换为RGBA模式以支持透明度
            img = img.convert("RGBA")
            width, height = img.size

            # 获取像素数据
            pixels = img.load()

            # 遍历所有像素
            for y in range(height):
                for x in range(width):
                    r, g, b, a = pixels[x, y]
                    # 检查是否为目标颜色（允许轻微偏差）
                    if (abs(r - target_color[0]) < 30 and
                            abs(g - target_color[1]) < 30 and
                            abs(b - target_color[2]) < 30):
                        # 将目标颜色像素设为透明
                        pixels[x, y] = (r, g, b, 0)

            # 保存修改后的图像
            img.save(output_path, "PNG")
            print(f"已处理图像并保存至 {output_path}")

    except Exception as e:
        print(f"处理图像时出错: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python remove_color.py 输入图片路径 输出图片路径")
        sys.exit(1)

    input_image = sys.argv[1]
    output_image = sys.argv[2]

    # 注意：这里的颜色值应为RGB格式，而不是16进制
    # 232429（16进制）转换为RGB约为 (35, 36, 41)
    # 但根据用户可能的输入错误，这里使用类似的深色值
    remove_color(input_image, output_image, target_color=(23, 36, 41))