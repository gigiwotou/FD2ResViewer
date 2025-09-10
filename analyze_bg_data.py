#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import struct
from PIL import Image
from main import ColorPanel

def analyze_bg_data():
    """详细分析BG.DAT数据"""
    print("详细分析BG.DAT数据...")
    
    # 读取BG.DAT文件
    file_path = 'BG.DAT'
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在")
        return
    
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    print(f"文件总大小: {len(file_data)} 字节")
    
    # 分析文件头
    print("\n=== 文件头 ===")
    header = file_data[:6]
    print(f"文件头: {header.hex()}")
    
    # 分析索引表
    print("\n=== 索引表 ===")
    index_count = 57
    indices = []
    for i in range(index_count):
        offset = 6 + i * 4
        if offset + 4 <= len(file_data):
            index = struct.unpack('<I', file_data[offset:offset+4])[0]
            indices.append(index)
            print(f"索引 {i:2d}: {index:6d} (0x{index:06x})")
    
    # 分析第一个数据块
    print("\n=== 第一个数据块详细分析 ===")
    if len(indices) > 1:
        start_offset = indices[0]
        end_offset = indices[1]
        block_size = end_offset - start_offset
        
        print(f"起始偏移: {start_offset} (0x{start_offset:x})")
        print(f"结束偏移: {end_offset} (0x{end_offset:x})")
        print(f"块大小: {block_size} 字节")
        
        # 读取宽度和高度
        if start_offset + 4 <= len(file_data):
            width = struct.unpack('<h', file_data[start_offset:start_offset+2])[0]
            height = struct.unpack('<h', file_data[start_offset+2:start_offset+4])[0]
            print(f"图像尺寸: {width}x{height}")
            
            # 分析压缩数据
            compressed_data_start = start_offset + 4
            compressed_data_end = start_offset + block_size
            compressed_data_size = compressed_data_end - compressed_data_start
            
            print(f"压缩数据起始: {compressed_data_start} (0x{compressed_data_start:x})")
            print(f"压缩数据结束: {compressed_data_end} (0x{compressed_data_end:x})")
            print(f"压缩数据大小: {compressed_data_size} 字节")
            print(f"压缩率: {compressed_data_size/(width*height)*100:.2f}%")
            
            # 显示前100个压缩字节
            if compressed_data_start + 100 <= len(file_data):
                sample_data = file_data[compressed_data_start:compressed_data_start+100]
                print("\n前100个压缩字节:")
                for i in range(0, len(sample_data), 10):
                    line = f"  {i:3d}-{i+9:3d}: "
                    for j in range(10):
                        if i + j < len(sample_data):
                            line += f"{sample_data[i+j]:3d} "
                    print(line)
            
            # 统计字节值分布
            if compressed_data_start + compressed_data_size <= len(file_data):
                compressed_data = file_data[compressed_data_start:compressed_data_start+compressed_data_size]
                byte_counts = [0] * 256
                for byte_val in compressed_data:
                    byte_counts[byte_val] += 1
                
                print("\n字节值分布:")
                count_0_63 = sum(byte_counts[0:64])
                count_64_127 = sum(byte_counts[64:128])
                count_128_191 = sum(byte_counts[128:192])
                count_192_255 = sum(byte_counts[192:256])
                
                print(f"  0-63:   {count_0_63:6d} ({count_0_63/len(compressed_data)*100:5.1f}%)")
                print(f"  64-127: {count_64_127:6d} ({count_64_127/len(compressed_data)*100:5.1f}%)")
                print(f"  128-191:{count_128_191:6d} ({count_128_191/len(compressed_data)*100:5.1f}%)")
                print(f"  192-255:{count_192_255:6d} ({count_192_255/len(compressed_data)*100:5.1f}%)")
                
                # 显示最常见的字节值
                sorted_bytes = sorted(range(256), key=lambda x: byte_counts[x], reverse=True)
                print(f"\n最常见的10个字节值:")
                for i in range(min(10, 256)):
                    byte_val = sorted_bytes[i]
                    count = byte_counts[byte_val]
                    if count > 0:
                        print(f"  {byte_val:3d} (0x{byte_val:02x}): {count:6d} 次")

def manual_decompress_step_by_step():
    """逐步手动解压缩以验证算法"""
    print("\n=== 逐步手动解压缩 ===")
    
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
    
    # 创建图像
    image = Image.new('RGB', (width, height))
    colorpanel = ColorPanel(1)
    
    # 压缩数据开始位置
    data_start = start_offset + 4
    data_end = start_offset + 1004  # 第一个数据块大小为1004字节
    
    # 按照C#逻辑实现解压缩
    num4 = data_start
    num3 = data_end - 1
    num7 = 0
    num8 = 0
    num9 = 0
    num10 = 0  # x坐标
    num11 = 0  # y坐标
    
    step = 0
    max_steps = 50  # 只测试前50步
    
    pixel_count = 0
    
    while num4 <= num3 and step < max_steps:
        print(f"\n步骤 {step}:")
        print(f"  num4={num4}, num7={num7}, num8={num8}, num9={num9}")
        print(f"  坐标: ({num10}, {num11})")
        
        # C#逻辑
        flag = False
        if num7 != 0:
            num7 = 0
            flag = True
            print(f"  num7 != 0, flag = True")
        else:
            flag = False
            print(f"  num7 == 0, flag = False")
        
        # 这是关键差异：在C#中，flag会被num8的值覆盖
        flag = (num8 != 0)
        print(f"  flag 被 num8 覆盖: {flag}")
        
        if not flag:
            print("  进入非flag分支")
            num7 = 0
            num8 = 0
            num9 = 0
            if num4 < len(file_data):
                b = file_data[num4]
                print(f"  读取字节 b={b}")
                if b >= 192:
                    num7 = b - 192 + 1
                    print(f"  b >= 192, num7 = {num7}")
                elif 128 <= b < 192:
                    num8 = b - 128 + 1
                    print(f"  128 <= b < 192, num8 = {num8}")
                elif 64 <= b < 128:
                    num9 = b - 64
                    num8 = 1
                    print(f"  64 <= b < 128, num9 = {num9}, num8 = {num8}")
                elif b <= 63:
                    num8 = 1
                    num9 = b
                    print(f"  b <= 63, num8 = {num8}, num9 = {num9}")
                
                num10 += num7
                print(f"  num10 += num7: {num10}")
                if num10 >= width:
                    num10 = 0
                    num11 += 1
                    print(f"  换行: num10=0, num11={num11}")
        else:
            print("  进入flag分支")
            if num4 < len(file_data) and num9 > 0:
                b = file_data[num4]
                print(f"  处理像素数据, b={b}, num9={num9}")
                
                # 严格按照C#的while(true)循环实现
                num12 = num9
                num13 = 0
                while True:
                    if num13 > num12:
                        break
                    print(f"    循环 {num13}/{num12}")
                    
                    if 64 <= b < 128:
                        num10 += 1
                        print(f"      b在64-128之间, num10 += 1: {num10}")
                    
                    if num4 < len(file_data):
                        index = file_data[num4]
                        print(f"      设置像素 ({num10}, {num11}) 为颜色索引 {index}")
                        if 0 <= num10 < width and 0 <= num11 < height:
                            color = colorpanel.thisColor(index)
                            image.putpixel((num10, num11), color)
                            pixel_count += 1
                            print(f"      成功设置像素 {pixel_count}")
                        else:
                            print(f"      坐标超出范围: ({num10}, {num11})")
                    
                    num10 += 1
                    print(f"      num10 += 1: {num10}")
                    if num10 >= width:
                        num10 = 0
                        num11 += 1
                        print(f"      换行: num10=0, num11={num11}")
                    
                    num13 += 1
                
            num8 -= 1
            print(f"  num8 -= 1: {num8}")
        num4 += 1
        step += 1
    
    print(f"\n总共处理了 {pixel_count} 个像素")
    
    # 保存图像
    image.save(os.path.join('output_images', 'bg_step_by_step.png'))
    print(f"逐步解压缩图像已保存")

if __name__ == '__main__':
    analyze_bg_data()
    manual_decompress_step_by_step()