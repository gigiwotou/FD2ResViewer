#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import struct
from fd2_analyzer import FD2Analyzer

def analyze_bg_structure():
    """分析BG.DAT文件结构"""
    print("分析BG.DAT文件结构...")
    
    # 检查文件是否存在
    file_path = 'BG.DAT'
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在")
        return
    
    # 创建分析器
    analyzer = FD2Analyzer()
    
    # 读取文件数据
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    print(f"文件大小: {len(file_data)} 字节")
    
    # 分析文件头
    print("\n=== 文件头分析 ===")
    header_data = file_data[:6]
    print(f"文件头: {header_data.hex()}")
    
    # 分析索引表
    print("\n=== 索引表分析 ===")
    index_count = 57  # BG.DAT有57个背景
    indices = []
    for i in range(index_count):
        offset = 6 + i * 4
        if offset + 4 <= len(file_data):
            index = struct.unpack('<I', file_data[offset:offset+4])[0]
            indices.append(index)
            print(f"索引 {i:2d}: {index:6d} (0x{index:06x})")
    
    # 分析数据块
    print("\n=== 数据块分析 ===")
    for i in range(min(5, len(indices)-1)):  # 只分析前5个数据块
        start_offset = indices[i]
        end_offset = indices[i+1]
        block_size = end_offset - start_offset
        
        if start_offset + 4 <= len(file_data):
            width = struct.unpack('<h', file_data[start_offset:start_offset+2])[0]
            height = struct.unpack('<h', file_data[start_offset+2:start_offset+4])[0]
            compressed_size = block_size - 4
            
            print(f"数据块 {i}:")
            print(f"  起始偏移: {start_offset} (0x{start_offset:x})")
            print(f"  结束偏移: {end_offset} (0x{end_offset:x})")
            print(f"  块大小: {block_size} 字节")
            print(f"  图像尺寸: {width}x{height}")
            print(f"  压缩数据大小: {compressed_size} 字节")
            print(f"  压缩率: {compressed_size/(width*height)*100:.2f}%")
            
            # 显示前20个压缩字节
            if start_offset + 4 + 20 <= len(file_data):
                compressed_data = file_data[start_offset+4:start_offset+4+20]
                print(f"  前20个压缩字节: {compressed_data.hex()}")

if __name__ == '__main__':
    analyze_bg_structure()