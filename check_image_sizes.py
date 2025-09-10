#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PIL import Image

def main():
    # 切换到图像输出目录
    image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output_images')
    os.chdir(image_dir)
    
    # 检查前几个BG图像的尺寸
    for i in range(5):
        image_path = f'bg_{i:05d}.png'
        if os.path.exists(image_path):
            with Image.open(image_path) as img:
                print(f'{image_path}: {img.width}x{img.height}')
        else:
            print(f'{image_path}: 文件不存在')

if __name__ == '__main__':
    main()