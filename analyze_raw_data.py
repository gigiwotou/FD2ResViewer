#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import struct

def analyze_raw_data():
    """分析原始二进制数据"""
    file_path = "FDTXT.DAT"
    
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在")
        return
    
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    print("分析原始二进制数据")
    
    # 分析主索引1的第一个子块
    main_index = 1
    main_index_start = 0x00001E66
    
    # 计算子块数量
    sub_block_count = int(struct.unpack('<h', file_data[main_index_start:main_index_start+2])[0] / 2)
    print(f"主索引{main_index}的子块数量: {sub_block_count}")
    
    # 计算子块偏移数组
    array2 = []
    for j in range(sub_block_count + 1):
        offset = main_index_start + struct.unpack('<h', file_data[main_index_start + j*2 : main_index_start + (j+1)*2])[0]
        array2.append(offset)
    
    # 分析第一个子块的原始数据
    i = 0
    start_offset = array2[i]
    end_offset = array2[i+1] if i < sub_block_count else len(file_data)
    length = end_offset - start_offset
    
    print(f"\n--- 分析子块 {i} 的原始数据 ---")
    print(f"子块偏移: 0x{start_offset:08X} 到 0x{end_offset:08X}")
    print(f"子块长度: {length} 字节")
    
    # 提取文本数据
    text_data = file_data[start_offset:end_offset]
    
    # 显示前64字节的十六进制和ASCII表示
    print("前64字节的详细分析:")
    for i in range(0, min(64, len(text_data)), 16):
        hex_part = ' '.join(f'{b:02X}' for b in text_data[i:i+16])
        ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in text_data[i:i+16])
        print(f"0x{i:04X}: {hex_part:<48} {ascii_part}")
    
    # 尝试不同的解码方式
    print("\n尝试不同的解码方式:")
    
    # 1. 直接UTF-16 LE解码所有数据
    try:
        result1 = text_data.decode('utf-16le', errors='ignore')
        print(f"1. 直接UTF-16 LE解码: {result1[:100]}")
    except Exception as e:
        print(f"1. 直接UTF-16 LE解码失败: {e}")
    
    # 2. 跳过前2字节后UTF-16 LE解码
    if len(text_data) > 2:
        try:
            result2 = text_data[2:].decode('utf-16le', errors='ignore')
            print(f"2. 跳过前2字节后UTF-16 LE解码: {result2[:100]}")
        except Exception as e:
            print(f"2. 跳过前2字节后UTF-16 LE解码失败: {e}")
    
    # 3. 跳过前4字节后UTF-16 LE解码
    if len(text_data) > 4:
        try:
            result3 = text_data[4:].decode('utf-16le', errors='ignore')
            print(f"3. 跳过前4字节后UTF-16 LE解码: {result3[:100]}")
        except Exception as e:
            print(f"3. 跳过前4字节后UTF-16 LE解码失败: {e}")
    
    # 4. 尝试GB2312解码
    try:
        result4 = text_data.decode('gb2312', errors='ignore')
        print(f"4. GB2312解码: {result4[:100]}")
    except Exception as e:
        print(f"4. GB2312解码失败: {e}")
    
    # 5. 尝试GBK解码
    try:
        result5 = text_data.decode('gbk', errors='ignore')
        print(f"5. GBK解码: {result5[:100]}")
    except Exception as e:
        print(f"5. GBK解码失败: {e}")

if __name__ == "__main__":
    analyze_raw_data()