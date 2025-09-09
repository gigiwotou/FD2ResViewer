import os
import struct
import time
from PIL import Image
from main import ColorPanel, BMPMaker, DataBlock

class ImageFinder:
    def __init__(self, file_path, output_dir='output_images_fuzzy'):
        self.file_path = file_path
        self.output_dir = output_dir
        self.fileDatas = None
        self.color_panel = ColorPanel(1)  # 使用灰色调色板
        self.bmp_maker = BMPMaker()
        os.makedirs(self.output_dir, exist_ok=True)
        
    def load_file(self):
        """加载二进制文件数据"""
        try:
            with open(self.file_path, 'rb') as f:
                self.fileDatas = bytearray(f.read())
            return len(self.fileDatas) > 0
        except Exception as e:
            print(f"加载文件时出错: {e}")
            return False
        
    def analyze_data_pattern(self, data_start, data_length):
        """分析数据模式，判断可能的压缩类型"""
        # 检查数据长度是否足够
        if data_length < 100:
            return 'unknown'
        
        byte_values = self.fileDatas[data_start:data_start+100]
        
        # 计算零值的比例
        zero_count = sum(1 for b in byte_values if b == 0)
        zero_ratio = zero_count / 100
        
        # 统计不同范围的字节出现频率
        count_192_255 = sum(1 for b in byte_values if b >= 192)
        count_128_191 = sum(1 for b in byte_values if 128 <= b < 192)
        count_64_127 = sum(1 for b in byte_values if 64 <= b < 128)
        count_0_63 = sum(1 for b in byte_values if 0 < b < 64)
        
        # 检查是否有明显的重复模式 (可能是压缩格式)
        has_repeat_pattern = False
        for i in range(50):
            if i+10 < 100 and byte_values[i:i+10] == byte_values[i+10:i+20]:
                has_repeat_pattern = True
                break
        
        # 如果有大量重复模式或高比例的192-255字节，可能是压缩格式
        if has_repeat_pattern or count_192_255 > 15 or count_128_191 > 15:
            return 'compressed'
        # 如果有较多的64-127字节且零值较少，可能是shape格式
        elif count_64_127 > 15 and zero_ratio < 0.3:
            return 'shape'
        # 如果零值比例很高，可能是背景图格式
        elif zero_ratio > 0.5:
            return 'bg'
        # 如果大部分值在0-63之间，可能是面部格式
        elif count_0_63 > 50:
            return 'face'
        # 否则可能是原始格式
        else:
            return 'raw'
        
    def fuzzy_search_images(self, min_width=16, max_width=1024, min_height=16, max_height=1024, max_images=100):
        """模糊搜索图像数据段
        Args:
            min_width: 最小宽度
            max_width: 最大宽度
            min_height: 最小高度
            max_height: 最大高度
            max_images: 最大找到的图像数量
        """
        if not self.fileDatas:
            if not self.load_file():
                print("无法加载文件")
                return 0
        
        file_size = len(self.fileDatas)
        found_count = 0
        last_progress = 0
        start_time = time.time()
        
        try:
            # 遍历文件中的每个可能位置
            for offset in range(file_size - 4):  # 至少需要4字节(宽+高)
                # 显示进度
                progress = int(offset / (file_size - 4) * 100)
                if progress != last_progress and progress % 5 == 0:
                    elapsed = time.time() - start_time
                    print(f"进度: {progress}%, 已找到: {found_count} 个图像, 用时: {elapsed:.1f}秒")
                    last_progress = progress
                
                # 达到最大图像数量则停止
                if found_count >= max_images:
                    break
                
                try:
                    # 尝试解析宽度和高度 (16位有符号整数, 小端序)
                    width = struct.unpack('<h', self.fileDatas[offset:offset+2])[0]
                    height = struct.unpack('<h', self.fileDatas[offset+2:offset+4])[0]
                    
                    # 检查宽度和高度是否在合理范围内
                    if not (min_width <= width <= max_width and min_height <= height <= max_height):
                        continue
                    
                    # 确定数据起始位置
                    data_start = offset + 4
                    
                    # 尝试不同的解析方法
                    # 1. 首先尝试原始格式 (makeBMP)
                    expected_data_length = width * height
                    data_end = data_start + expected_data_length
                    if data_end <= file_size:
                        # 分析数据模式
                        data_pattern = self.analyze_data_pattern(data_start, expected_data_length)
                        
                        # 根据数据模式选择合适的解析函数
                        try:
                            if data_pattern == 'raw':
                                # 使用原始格式解析
                                image = self.bmp_maker.makeBMP(
                                    width, height,
                                    self.fileDatas,
                                    data_start,
                                    expected_data_length,
                                    self.color_panel
                                )
                                method = 'makeBMP'
                            elif data_pattern == 'shape':
                                # 使用形状格式解析
                                image = self.bmp_maker.makeShapBMP(
                                    width, height,
                                    self.fileDatas,
                                    data_start,
                                    expected_data_length,
                                    self.color_panel
                                )
                                method = 'makeShapBMP'
                            elif data_pattern == 'face':
                                # 尝试面部格式解析
                                image = self.bmp_maker.makeFaceBMP(
                                    self.fileDatas,
                                    offset,  # 注意：makeFaceBMP的startOffset是包含宽高的
                                    expected_data_length + 4,  # 包含宽高的4字节
                                    self.color_panel
                                )
                                method = 'makeFaceBMP'
                            elif data_pattern == 'bg':
                                # 尝试背景图格式解析
                                image = self.bmp_maker.makeBgBMP(
                                    width, height,
                                    self.fileDatas,
                                    data_start,
                                    expected_data_length,
                                    self.color_panel
                                )
                                method = 'makeBgBMP'
                            elif data_pattern == 'compressed':
                                # 尝试战斗图格式解析 (通常是压缩的)
                                image = self.bmp_maker.makeFightBMP(
                                    self.fileDatas,
                                    offset,  # 注意：makeFightBMP的startOffset是包含宽高的
                                    expected_data_length + 4,  # 包含宽高的4字节
                                    self.color_panel
                                )
                                method = 'makeFightBMP'
                            else:
                                # 默认使用原始格式
                                image = self.bmp_maker.makeBMP(
                                    width, height,
                                    self.fileDatas,
                                    data_start,
                                    expected_data_length,
                                    self.color_panel
                                )
                                method = 'makeBMP'
                            
                            # 保存图像
                            image_path = os.path.join(self.output_dir, f'fuzzy_image_{found_count}_w{width}_h{height}_offset{offset:08X}_{method}.png')
                            image.save(image_path)
                            print(f"找到可能的图像: 宽度={width}, 高度={height}, 偏移=0x{offset:X}, 方法={method}")
                            print(f"图像已保存到: {image_path}")
                            found_count += 1
                        except Exception as e:
                            # 如果一种方法失败，尝试其他方法
                            continue
                    
                except Exception as e:
                    # 忽略解析错误
                    continue
        except KeyboardInterrupt:
            print("搜索已被用户中断")
        
        elapsed_time = time.time() - start_time
        print(f"模糊搜索完成，共找到 {found_count} 个可能的图像，用时: {elapsed_time:.1f}秒")
        return found_count

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("用法: python image_finder.py <二进制文件路径> [最大图像数量]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    max_images = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    
    finder = ImageFinder(file_path)
    finder.fuzzy_search_images(max_images=max_images)