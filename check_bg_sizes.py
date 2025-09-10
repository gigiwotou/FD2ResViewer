#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PIL import Image

def check_bg_sizes():
    """检查BG图片的尺寸"""
    image_dir = 'output_images'
    bg_files = [f for f in os.listdir(image_dir) if f.startswith('bg_') and f.endswith('.png')]
    
    print(f"找到 {len(bg_files)} 个BG图片")
    
    # 检查前10个图片的尺寸
    for i in range(min(10, len(bg_files))):
        bg_file = f'bg_{i:05d}.png'
        if bg_file in bg_files:
            image_path = os.path.join(image_dir, bg_file)
            try:
                with Image.open(image_path) as img:
                    print(f"{bg_file}: {img.width}x{img.height}")
            except Exception as e:
                print(f"{bg_file}: 无法打开图片 - {e}")

if __name__ == '__main__':
    check_bg_sizes()