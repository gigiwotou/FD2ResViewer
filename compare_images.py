#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PIL import Image, ImageChops

def compare_images():
    """比较两个图像是否相同"""
    # 切换到图像输出目录
    image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output_images')
    os.chdir(image_dir)
    
    # 加载两个图像
    image1_path = 'bg_original_00000.png'
    image2_path = 'bg_manual_00000.png'
    
    if not os.path.exists(image1_path) or not os.path.exists(image2_path):
        print("图像文件不存在")
        return
    
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)
    
    # 比较图像
    diff = ImageChops.difference(image1, image2)
    
    # 如果图像相同，diff应该是一张全黑的图像
    if diff.getbbox() is None:
        print("两个图像完全相同")
    else:
        print("两个图像不相同")
        # 计算差异
        total_pixels = image1.width * image1.height
        diff_pixels = 0
        for x in range(image1.width):
            for y in range(image1.height):
                if diff.getpixel((x, y)) != (0, 0, 0):
                    diff_pixels += 1
        
        print(f"图像尺寸: {image1.width}x{image1.height}")
        print(f"差异像素数: {diff_pixels}")
        print(f"差异比例: {diff_pixels/total_pixels*100:.2f}%")
        
        # 保存差异图像
        diff.save('bg_diff.png')
        print("差异图像已保存为 bg_diff.png")

if __name__ == '__main__':
    compare_images()