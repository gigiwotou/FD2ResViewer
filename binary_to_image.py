import os
import struct
import argparse
from PIL import Image, ImageColor, ImageDraw
from main import ColorPanel  # 导入ColorPanel类

class BinaryToImageConverter:
    def __init__(self):
        # 从ColorPanel(1)获取颜色
        self.color_panel = ColorPanel(1)
        # 从ColorPanel获取256种颜色
        self.palette = [self.color_panel.thisColor(i) for i in range(256)]
        # 确保调色板至少有256种颜色，如果不足则用索引0的颜色补齐
        if len(self.palette) < 256:
            self.palette += [self.palette[0] for _ in range(256 - len(self.palette))]
        
    def read_binary_file(self, file_path):
        """读取二进制文件内容"""
        with open(file_path, 'rb') as f:
            return f.read()

    def calculate_image_size(self, data_length, width, bits_per_pixel):
        """计算图像尺寸"""
        bytes_per_pixel = bits_per_pixel // 8
        pixels_per_row = width
        total_pixels = data_length // bytes_per_pixel
        height = (total_pixels + width - 1) // width  # 向上取整
        return width, height

    def parse_data(self, data, width, height, bits_per_pixel):
        """解析二进制数据为像素值"""
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        bytes_per_pixel = bits_per_pixel // 8
        total_pixels = width * height
        pixel_index = 0
        
        # 处理所有像素点，包括数据不足的情况
        for pixel_index in range(total_pixels):
            # 计算像素位置
            x = pixel_index % width
            y = pixel_index // width
            
            # 默认为索引0的颜色
            color = self.palette[0]
            
            # 只有当数据足够时才解析
            if pixel_index < len(data) // bytes_per_pixel:
                i = pixel_index
                # 根据颜色位数解析数据
                if bits_per_pixel == 8:
                    # 8位颜色 - 每个字节对应一个像素
                    if i < len(data):
                        color_index = data[i]
                        # 确保颜色索引在有效范围内
                        color_index = min(max(color_index, 0), 255)
                        color = self.palette[color_index]
                else:
                    # 对于其他位数，我们只支持8位，这里简化处理
                    raise ValueError("只支持8位颜色模式")
            
            draw.point((x, y), fill=color)
        
        return image

    def convert(self, input_file, output_file):
        """将二进制文件转换为图像"""
        # 固定参数
        width = 320
        bits_per_pixel = 8  # 每个字节作为一个颜色索引

        # 读取二进制数据
        data = self.read_binary_file(input_file)
        if not data:
            raise ValueError("无法读取输入文件或文件为空")

        # 计算图像尺寸
        width, height = self.calculate_image_size(len(data), width, bits_per_pixel)
        print(f"生成图像尺寸: {width}x{height}")

        # 解析数据并创建图像
        image = self.parse_data(data, width, height, bits_per_pixel)

        # 保存图像
        image.save(output_file)
        print(f"图像已保存到: {output_file}")
        return output_file

    # 移除set_palette方法，因为我们现在使用ColorPanel的颜色

if __name__ == '__main__':
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='将二进制文件转换为图像')
    parser.add_argument('input_file', help='输入二进制文件路径')
    parser.add_argument('output_file', help='输出图像文件路径')
    
    args = parser.parse_args()
    
    # 检查输入文件是否存在
    if not os.path.exists(args.input_file):
        print(f"错误: 输入文件 '{args.input_file}' 不存在")
        exit(1)
    
    # 创建转换器并转换
    converter = BinaryToImageConverter()
    try:
        converter.convert(args.input_file, args.output_file)
    except Exception as e:
        print(f"转换失败: {e}")
        exit(1)