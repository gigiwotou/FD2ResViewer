#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import struct
from PIL import Image
from main import ColorPanel

def manual_bg_decompress_original(datablock, startOffset, length, colorpanel):
    """原始实现的解压缩方法"""
    width = struct.unpack('<h', datablock[startOffset:startOffset+2])[0]
    height = struct.unpack('<h', datablock[startOffset+2:startOffset+4])[0]
    image = Image.new('RGB', (width, height))
    
    num4 = startOffset + 4
    num3 = startOffset + length - 1
    num7 = 0
    num8 = 0
    num9 = 0
    num10 = 0
    num11 = 0
    
    while num4 <= num3:
        if num7 != 0:
            num7 = 0
            flag = True
        else:
            flag = False
        
        flag = (num8 != 0)
        
        if not flag:
            num7 = 0
            num8 = 0
            num9 = 0
            if num4 < len(datablock):
                b = datablock[num4]
                if b >= 192:
                    num7 = b - 192 + 1
                elif 128 <= b < 192:
                    num8 = b - 128 + 1
                elif 64 <= b < 128:
                    num9 = b - 64
                    num8 = 1
                elif b <= 63:
                    num8 = 1
                    num9 = b
                
                num10 += num7
                if num10 >= width:
                    num10 = 0
                    num11 += 1
        else:
            if num4 < len(datablock):
                b = datablock[num4]
                for _ in range(num9):
                    if 64 <= b < 128:
                        num10 += 1
                    if num4 < len(datablock):
                        index = datablock[num4]
                        if 0 <= num10 < width and 0 <= num11 < height:
                            image.putpixel((num10, num11), colorpanel.thisColor(index))
                    num10 += 1
                    if num10 >= width:
                        num10 = 0
                        num11 += 1
            num8 -= 1
        num4 += 1
    
    return image

def manual_bg_decompress_fixed(datablock, startOffset, length, colorpanel):
    """修复后的解压缩方法"""
    width = struct.unpack('<h', datablock[startOffset:startOffset+2])[0]
    height = struct.unpack('<h', datablock[startOffset+2:startOffset+4])[0]
    image = Image.new('RGB', (width, height))
    
    num4 = startOffset + 4
    num3 = startOffset + length - 1
    num7 = 0
    num8 = 0
    num9 = 0
    num10 = 0
    num11 = 0
    
    while num4 <= num3:
        # 修复flag处理逻辑
        if num7 != 0:
            num7 = 0
            flag = True
        else:
            flag = False
        
        # 关键修复：flag会被num8的值覆盖
        flag = (num8 != 0)
        
        if not flag:
            num7 = 0
            num8 = 0
            num9 = 0
            if num4 < len(datablock):
                b = datablock[num4]
                if b >= 192:
                    num7 = b - 192 + 1
                elif 128 <= b < 192:
                    num8 = b - 128 + 1
                elif 64 <= b < 128:
                    num9 = b - 64
                    num8 = 1
                elif b <= 63:
                    num8 = 1
                    num9 = b
                
                num10 += num7
                if num10 >= width:
                    num10 = 0
                    num11 += 1
        else:
            # 修复循环逻辑
            if num4 < len(datablock):
                b = datablock[num4]
                num12 = num9
                num13 = 0
                while True:
                    if num13 > num12:
                        break
                    if 64 <= b < 128:
                        num10 += 1
                    if num4 < len(datablock):
                        index = datablock[num4]
                        if 0 <= num10 < width and 0 <= num11 < height:
                            image.putpixel((num10, num11), colorpanel.thisColor(index))
                    num10 += 1
                    if num10 >= width:
                        num10 = 0
                        num11 += 1
                    num13 += 1
            num8 -= 1
        num4 += 1
    
    return image

def compare_compression_methods():
    """比较不同的压缩算法实现"""
    print("比较不同的BG.DAT压缩算法实现...")
    
    # 读取BG.DAT文件
    file_path = 'BG.DAT'
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在")
        return
    
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    # 获取第一个背景的数据
    start_offset = 234
    width = struct.unpack('<h', file_data[start_offset:start_offset+2])[0]
    height = struct.unpack('<h', file_data[start_offset+2:start_offset+4])[0]
    print(f"图像尺寸: {width}x{height}")
    
    colorpanel = ColorPanel(1)
    
    # 使用原始方法生成图像
    print("使用原始方法生成图像...")
    image1 = manual_bg_decompress_original(
        file_data, start_offset, 1004, colorpanel
    )
    image1.save(os.path.join('output_images', 'bg_original_method.png'))
    print(f"原始方法生成图像尺寸: {image1.width}x{image1.height}")
    
    # 使用修复后的方法生成图像
    print("使用修复后的方法生成图像...")
    image2 = manual_bg_decompress_fixed(
        file_data, start_offset, 1004, colorpanel
    )
    image2.save(os.path.join('output_images', 'bg_fixed_method.png'))
    print(f"修复后方法生成图像尺寸: {image2.width}x{image2.height}")
    
    # 比较两个图像
    if image1.tobytes() == image2.tobytes():
        print("两个图像完全相同")
    else:
        print("两个图像不同")
        
        # 计算差异
        diff_count = 0
        for x in range(width):
            for y in range(height):
                if image1.getpixel((x, y)) != image2.getpixel((x, y)):
                    diff_count += 1
        
        print(f"差异像素数: {diff_count}")
        print(f"差异比例: {diff_count/(width*height)*100:.2f}%")

if __name__ == '__main__':
    compare_compression_methods()