"""基础解析器类，定义解析器的通用接口"""

import os
import struct
from typing import Optional, List
from PIL import Image
from abc import ABC, abstractmethod


class DataBlock:
    """数据块结构"""
    def __init__(self, startOffset, length):
        self.startOffset = startOffset
        self.length = length
        
    def __str__(self):
        return f"DataBlock(startOffset={self.startOffset}, length={self.length})"
    
    def __repr__(self):
        return self.__str__()


class Color:
    def __init__(self, red, green, blue, reserved):
        self.Red = red
        self.Green = green
        self.Blue = blue
        self.Reserved = reserved


class ColorPanel:
    def __init__(self, id):
        self.colors = [Color(0, 0, 0, 0) for _ in range(256)]
        self.colorPanelData = bytearray(768)  # 256 colors × 3 bytes each
        
        # 用户未提供Resource.cs，使用示例颜色数据作为替代
        if id == 1:
            # 示例颜色数据：生成渐变灰色调色板
            # self.colorPanelData = bytearray([i//12 for i in range(768)])
            loaded_data = self._load_resource('colorPanel')
            if loaded_data:
                self.colorPanelData = loaded_data
            else:
                # 如果没有资源文件，生成默认灰度调色板
                self.colorPanelData = bytearray([i//3 for i in range(768)])
        elif id == 2:
            # 示例颜色数据：生成蓝色系调色板
            # self.colorPanelData = bytearray([b for i in range(256) for b in (0, 0, i//4)])
            loaded_data = self._load_resource('colornew2')
            if loaded_data:
                self.colorPanelData = loaded_data
            else:
                # 如果没有资源文件，生成默认蓝色调色板
                self.colorPanelData = bytearray([b for i in range(256) for b in (0, 0, i//4)])
        else:
            # 示例颜色数据：生成红色系调色板
            # self.colorPanelData = bytearray([b for i in range(256) for b in (i//4, 0, 0)])
            loaded_data = self._load_resource('colornew')
            if loaded_data:
                self.colorPanelData = loaded_data
            else:
                # 如果没有资源文件，生成默认红色调色板
                self.colorPanelData = bytearray([b for i in range(256) for b in (i//4, 0, 0)])
        
        for i in range(256):
            if self.colorPanelData and len(self.colorPanelData) >= (i*3 + 3):
                # 正确的6位颜色值转换为8位的方法：左移2位并保留低4位
                # 这样可以保持颜色的精度和连续性
                red_value = self.colorPanelData[i*3]
                green_value = self.colorPanelData[i*3 + 1]
                blue_value = self.colorPanelData[i*3 + 2]
                
                # 正确的转换方式：(value << 2) | (value >> 4)
                red = (red_value << 2) | (red_value >> 4)
                green = (green_value << 2) | (green_value >> 4)
                blue = (blue_value << 2) | (blue_value >> 4)
            else:
                # 默认灰度颜色
                red = green = blue = i
            self.colors[i] = Color(red, green, blue, 0)

    def _load_resource(self, filename):
        """加载资源文件并返回字节数据"""
        # 构造资源文件的完整路径
        resource_path = os.path.join('resources', filename)
        try:
            with open(resource_path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            print(f"警告: 资源文件 {resource_path} 未找到")
            return None
    
    def thisColor(self, index):
        if 0 <= index < len(self.colors):
            return (self.colors[index].Red, self.colors[index].Green, self.colors[index].Blue)
        else:
            # 返回默认颜色，防止索引越界
            return (0, 0, 0)


class BMPMaker:
    def __init__(self):
        # 加载资源文件
        self.BMPHeader1Bit = self._load_resource('SingleBitBMPHeader') or bytearray(64)  # 提供默认值
        self.colorPanel_data = self._load_resource('colorPanel')
        self.colornew_data = self._load_resource('colornew')
        self.colornew2_data = self._load_resource('colornew2')
        self.BMPDatas1Bit = bytearray(64)
        self.tempFontBMP = bytearray(len(self.BMPHeader1Bit) + 64) if self.BMPHeader1Bit else bytearray(64)
        self.BMPimage = None
        self.shaps = [None] * 401  # 用于存储图块图像的数组

    def _load_resource(self, filename):
        """加载资源文件并返回字节数据"""
        # 构造资源文件的完整路径
        resource_path = os.path.join('resources', filename)
        try:
            with open(resource_path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            print(f"警告: 资源文件 {resource_path} 未找到")
            return None

    def makeFontBMP(self, datablock, startOffset, length):
        num = length - 1
        num2 = 0
        while num2 <= num:
            idx = 60 - num2 * 2
            self.BMPDatas1Bit[idx] = datablock[startOffset + num2]
            self.BMPDatas1Bit[idx + 1] = datablock[startOffset + num2 + 1]
            self.BMPDatas1Bit[idx + 2] = 0
            self.BMPDatas1Bit[idx + 3] = 0
            num2 += 2
        
        self.tempFontBMP = bytearray(self.BMPHeader1Bit)
        self.tempFontBMP.extend(self.BMPDatas1Bit)
        from io import BytesIO
        stream = BytesIO(self.tempFontBMP)
        self.BMPimage = Image.open(stream)
        return self.BMPimage

    def makeBMP(self, width, height, datablock, startOffset, length, colorpanel):
        self.BMPimage = Image.new('RGB', (width, height))
        num2 = startOffset + length - 1
        num = startOffset
        num5 = 0  # x坐标
        num6 = 0  # y坐标
        # print(f"makeBMP: width={width}, height={height}, startOffset={startOffset}, length={length}")
        while num <= num2:
            # 检查坐标是否在图像范围内
            if num6 >= height:
                break  # 防止y坐标越界
                
            if num5 >= width:
                num5 = 0
                num6 += 1
                # 再次检查y坐标
                if num6 >= height:
                    break  # 防止y坐标越界
            
            index = datablock[num]
            # 检查数据索引是否有效
            if num < len(datablock):
                self.BMPimage.putpixel((num5, num6), colorpanel.thisColor(index))
            else:
                # 数据不足，使用默认颜色
                self.BMPimage.putpixel((num5, num6), (0, 0, 0))
            num5 += 1
            if num5 == width:
                num5 = 0
                num6 += 1
            num += 1
        
        return self.BMPimage

    def makeFaceBMP(self, datablock, startOffset, length, colorpanel):
        num = 0
        flag = True
        num2 = 1
        width = struct.unpack('<h', datablock[startOffset:startOffset+2])[0]
        height = struct.unpack('<h', datablock[startOffset+2:startOffset+4])[0]
        self.BMPimage = Image.new('RGB', (width, height))
        num4 = startOffset + 4
        num5 = startOffset + length - 1
        num = num4
        num11 = 0
        num12 = 0
        # print(f"makeFaceBMP: width={width}, height={height}, startOffset={startOffset}, length={length}")
        while num <= num5:
            if num % 200 == 0:
                pass  # 需补充进度条更新逻辑
            
            b = datablock[num]
            if b > 192 and flag:
                num2 = b - 192
                flag = False
            else:
                flag = True
                for _ in range(num2):
                    self.BMPimage.putpixel((num11, num12), colorpanel.thisColor(b))
                    num11 += 1
                    if num11 == width:
                        num11 = 0
                        num12 += 1
                num2 = 1
            num += 1
        
        return self.BMPimage

    def makeBgBMP(self, datablock, startOffset, length, colorpanel):
        flag = False
        width = struct.unpack('<h', datablock[startOffset:startOffset+2])[0]
        height = struct.unpack('<h', datablock[startOffset+2:startOffset+4])[0]
        self.BMPimage = Image.new('RGB', (width, height))
        progress_max = length - 5
        num2 = startOffset + 4
        num3 = startOffset + length - 1
        num4 = num2
        num7 = 0
        num8 = 0
        num9 = 0
        b = 0
        num10 = 0
        num11 = 0
        
        while num4 <= num3:
            if num4 % 200 == 0:
                pass  # 需补充进度条更新逻辑
            
            # 修复flag处理逻辑，使其与C#版本完全一致
            if num7 != 0:
                num7 = 0
                flag = True
            else:
                flag = False
            
            # 关键修复：flag会被num8的值覆盖
            flag = (num8 != 0)
            
            # 修复逻辑判断，使其与C#版本完全一致
            # C#中的 if (unchecked(0 - (flag ? 1 : 0)) == 0) 等价于 if not flag:
            if not flag:
                num7 = 0
                num8 = 0
                num9 = 0
                if num4 < len(datablock):
                    b = datablock[num4]
                    if b >= 192:
                        num7 = b - 192 + 1
                    if 128 <= b < 192:
                        num8 = b - 128 + 1
                    if 64 <= b < 128:
                        num9 = b - 64
                        num8 = 1
                        flag = True
                    if b <= 63:
                        num8 = 1
                        num9 = b
                
                num10 += num7
                if num10 >= width:
                    num10 = 0
                    num11 += 1
                    flag = False
            else:
                # 修复循环逻辑，使其与C#版本完全一致
                num12 = num9
                num13 = 0
                while True:
                    if num13 > num12:
                        break
                    if 64 <= b < 128:
                        num10 += 1
                    index = datablock[num4]
                    self.BMPimage.putpixel((num10, num11), colorpanel.thisColor(index))
                    num10 += 1
                    if num10 >= width:
                        num10 = 0
                        num11 += 1
                        flag = False
                    num13 += 1
                num8 -= 1
            num4 += 1
        
        return self.BMPimage

    def makeFightBMP(self, datablock, startOffset, length, colorpanel):
        flag = False
        # 与C#版本保持一致：直接从startOffset+9和startOffset+11位置读取宽度和高度
        width = struct.unpack('<h', datablock[startOffset+9:startOffset+11])[0]
        height = struct.unpack('<h', datablock[startOffset+11:startOffset+13])[0]
        
        # 确保宽度和高度在合理范围内
        width = max(1, min(width, 1000))
        height = max(1, min(height, 1000))
        
        self.BMPimage = Image.new('RGB', (width, height))
        progress_max = length - 5
        # 与C#版本保持一致：从startOffset+13开始读取数据
        num2 = startOffset + 13
        num3 = startOffset + length - 1
        num4 = num2
        num7 = 0
        num8 = 0
        num9 = 0
        b = 0
        num10 = 0
        num11 = 0
        
        # 添加调试信息
        # print(f"makeFightBMP: width={width}, height={height}, startOffset={startOffset}, length={length}")
        
        while num4 <= num3 and num4 < len(datablock):
            if num4 % 200 == 0:
                pass  # 需补充进度条更新逻辑
            
            # 修复flag处理逻辑，使其与C#版本完全一致
            if num7 != 0:
                num7 = 0
                flag = True
            else:
                flag = False
            
            # 关键修复：flag会被num8的值覆盖
            flag = (num8 != 0)
            
            # 修复逻辑判断，使其与C#版本完全一致
            # C#中的 if (unchecked(0 - (flag ? 1 : 0)) == 0) 等价于 if not flag:
            if not flag:
                num7 = 0
                num8 = 0
                num9 = 0
                if num4 < len(datablock):
                    b = datablock[num4]
                    # print(f"  非flag分支: num4={num4}, b={b}")
                    if b >= 192:
                        num7 = b - 192 + 1
                        # print(f"    跳过 {num7} 个像素")
                    if 128 <= b < 192:  # 修复条件判断逻辑，使用if而非elif
                        num8 = b - 128 + 1
                        # print(f"    重复 {num8} 次")
                    if 64 <= b < 128:   # 修复条件判断逻辑，使用if而非elif
                        num9 = b - 64
                        num8 = 1
                        flag = True
                        # print(f"    连续绘制 {num9} 个像素")
                    if b <= 63:         # 修复条件判断逻辑，使用if而非elif
                        num8 = 1
                        num9 = b
                        # print(f"    单像素绘制 {num9} 次")
                
                num10 += num7
                # print(f"    num10 += num7: {num10 - num7} + {num7} = {num10}")
                if num10 >= width:
                    num10 = 0
                    num11 += 1
                    flag = False
                    # print(f"    换行: num10=0, num11={num11}")
                # 在非flag分支中增加num4
                num4 += 1
                # print(f"    非flag分支中num4增加: {num4-1} -> {num4}")
            else:
                # print(f"  flag分支: num4={num4}, num9={num9}")
                # 修复循环逻辑，使其与C#版本完全一致
                num12 = num9
                num13 = 0
                while True:
                    if num13 > num12:
                        # print(f"    num13({num13}) > num12({num12}), 退出循环")
                        break
                    # print(f"    循环第 {num13} 次:")
                    if 64 <= b < 128:
                        num10 += 1
                        # print(f"      64 <= b < 128, num10 += 1: {num10 - 1} -> {num10}")
                        # 检查是否需要换行
                        if num10 >= width:
                            num10 = 0
                            num11 += 1
                            flag = False
                            # print(f"      换行: num10=0, num11={num11}")
                    # 修复：在正确的位置读取颜色索引
                    if num4 < len(datablock):
                        index = datablock[num4]
                        # print(f"      读取颜色索引: index={index}")
                        num7 = 1  # 重置num7为1
                        if 0 <= num10 < width and 0 <= num11 < height:
                            # print(f"      绘制像素: ({num10}, {num11}) = 索引 {index}")
                            self.BMPimage.putpixel((num10, num11), colorpanel.thisColor(index))
                    num10 += num7
                    # print(f"      num10 += num7: {num10 - num7} + {num7} = {num10}")
                    if num10 >= width:
                        num10 = 0
                        num11 += 1
                        flag = False
                        # print(f"      换行: num10=0, num11={num11}")
                    num13 += 1
                num8 -= 1
                # print(f"    num8减少: {num8 + 1} -> {num8}")
                # 修复：确保在else分支中正确增加num4
                num4 += 1
                # print(f"    flag分支中num4增加: {num4-1} -> {num4}")
        
        return self.BMPimage

    def makeFieldBMP(self, datablock, order, startOffset, length, colorpanel):
        width = struct.unpack('<h', datablock[startOffset:startOffset+2])[0]
        height = struct.unpack('<h', datablock[startOffset+2:startOffset+4])[0]
        self.BMPimage = Image.new('RGB', (width * 24, height * 24))
        num3 = startOffset + 4
        num4 = startOffset + length - 1
        num5 = num3
        num9 = 0
        num10 = 0
        
        while num5 <= num4:
            num8 = struct.unpack('<h', datablock[num5:num5+2])[0]
            # 使用shaps数组中的图像进行拼接
            # 修复：添加更严格的边界检查
            if (hasattr(self, 'shaps') and self.shaps and 
                0 <= num8 < len(self.shaps) and self.shaps[num8] is not None):
                # 将图块图像粘贴到地图图像上
                self.BMPimage.paste(self.shaps[num8], (num9 * 24, num10 * 24))
            num9 += 1
            if num9 >= width:
                num9 = 0
                num10 += 1
            num5 += 4
        
        return self.BMPimage

    def makeTAIBMP(self, datablock, startOffset, length, colorpanel):
        """TAI文件专用图像生成方法"""
        flag = False
        width = struct.unpack('<h', datablock[startOffset:startOffset+2])[0]
        height = struct.unpack('<h', datablock[startOffset+2:startOffset+4])[0]
        self.BMPimage = Image.new('RGB', (width, height))
        progress_max = length - 5
        num2 = startOffset + 4
        num3 = startOffset + length - 1
        num4 = num2
        num7 = 0
        num8 = 0
        num9 = 0
        b = 0
        num10 = 0
        num11 = 0
        
        while num4 <= num3:
            if num4 % 200 == 0:
                pass  # 需补充进度条更新逻辑
            
            # 修复flag处理逻辑，使其与C#版本完全一致
            if num7 != 0:
                num7 = 0
                flag = True
            else:
                flag = False
            
            # 关键修复：flag会被num8的值覆盖
            flag = (num8 != 0)
            
            # 修复逻辑判断，使其与C#版本完全一致
            # C#中的 if (unchecked(0 - (flag ? 1 : 0)) == 0) 等价于 if not flag:
            if not flag:
                num7 = 0
                num8 = 0
                num9 = 0
                if num4 < len(datablock):
                    b = datablock[num4]
                    if b >= 192:
                        num7 = b - 192 + 1
                    if 128 <= b < 192:
                        num8 = b - 128 + 1
                    if 64 <= b < 128:
                        num9 = b - 64
                        num8 = 1
                        flag = True
                    if b <= 63:
                        num8 = 1
                        num9 = b
                
                num10 += num7
                if num10 >= width:
                    num10 = 0
                    num11 += 1
                    flag = False
            else:
                # 修复循环逻辑，使其与C#版本完全一致
                num12 = num9
                num13 = 0
                while True:
                    if num13 > num12:
                        break
                    if 64 <= b < 128:
                        num10 += 1
                    index = datablock[num4]
                    self.BMPimage.putpixel((num10, num11), colorpanel.thisColor(index))
                    num10 += 1
                    if num10 >= width:
                        num10 = 0
                        num11 += 1
                        flag = False
                    num13 += 1
                num8 -= 1
            num4 += 1
        
        return self.BMPimage

    def adCharactersToField(self, field, id):
        num = id * 3 + 2
        # 假设MyModule.dataFileDatas[3].datas是字节数据
        # num2 = struct.unpack('<h', MyModule.dataFileDatas[3].datas[MyModule.datablocksFDFIELD[num].startOffset:MyModule.datablocksFDFIELD[num].startOffset+2])[0]
        self.BMPimage = field.copy()
        # 需要补充Graphics绘制逻辑
        return self.BMPimage

    def makeShapBMP(self, width, height, datablock, startOffset, length, colorpanel):
        flag = False
        self.BMPimage = Image.new('RGB', (width, height))
        progress_max = length
        num = startOffset + length - 1
        num2 = startOffset
        num5 = 0
        num6 = 0
        num7 = 0
        num8 = 0
        num9 = 0
        b = 0  # 初始化b变量
        # print(f"makeShapBMP: width={width}, height={height}, startOffset={startOffset}, length={length}")
        while num2 <= num:
            if num2 % 200 == 0:
                pass  # 需补充进度条更新逻辑
            
            if num5 != 0:
                num5 = 0
                flag = True
            else:
                flag = False
            
            flag = (num6 != 0)
            if not flag:
                num5 = 0
                num6 = 0
                num7 = 0
                if num2 < len(datablock):
                    b = datablock[num2]
                if b >= 192:
                    num5 = b - 192 + 1
                elif 128 <= b < 192:
                    num6 = b - 128 + 1
                elif 64 <= b < 128:
                    num7 = b - 64
                    num6 = 1
                    flag = True
                elif b <= 63:
                    num6 = 1
                    num7 = b
                
                num8 += num5
                if num8 >= width:
                    num8 = 0
                    num9 += 1
                    flag = False
            else:
                # 修复循环逻辑，使其与C#版本完全一致
                num10 = num7
                num11 = 0
                while True:
                    if num11 > num10:
                        break
                    if 64 <= b < 128:
                        num8 += 1
                    index = datablock[num2]
                    self.BMPimage.putpixel((num8, num9), colorpanel.thisColor(index))
                    num8 += 1
                    if num8 >= width:
                        num8 = 0
                        num9 += 1
                        flag = False
                    num11 += 1
                num6 -= 1
            num2 += 1
        
        return self.BMPimage

    def makeANIBMP(self, datablock, startOffset, length, colorpanel):
        """ANI文件专用图像生成方法，处理[长度][宽度][高度][数据]格式"""
        flag = False
        # 从startOffset开始读取 [长度][宽度][高度]
        frame_length = struct.unpack('<H', datablock[startOffset:startOffset+2])[0]
        width = struct.unpack('<H', datablock[startOffset+2:startOffset+4])[0]
        height = struct.unpack('<H', datablock[startOffset+4:startOffset+6])[0]
        
        # 确保宽度和高度在合理范围内
        width = max(1, min(width, 1000))
        height = max(1, min(height, 1000))
        
        self.BMPimage = Image.new('RGB', (width, height))
        
        # 从startOffset+6开始是实际的图像数据
        data_start = startOffset + 6
        data_end = min(data_start + frame_length, startOffset + length)
        
        num4 = data_start
        num7 = 0  # 跳过的像素数
        num8 = 0  # 重复次数
        num9 = 0  # 连续绘制的像素数
        b = 0
        num10 = 0  # x坐标
        num11 = 0  # y坐标
        
        while num4 < data_end:
            if num4 % 200 == 0:
                pass  # 需补充进度条更新逻辑
            
            # 修复flag处理逻辑，使其与C#版本完全一致
            if num7 != 0:
                num7 = 0
                flag = True
            else:
                flag = False
            
            # 关键修复：flag会被num8的值覆盖
            flag = (num8 != 0)
            
            # 修复逻辑判断，使其与C#版本完全一致
            # C#中的 if (unchecked(0 - (flag ? 1 : 0)) == 0) 等价于 if not flag:
            if not flag:
                num7 = 0
                num8 = 0
                num9 = 0
                if num4 < len(datablock):
                    b = datablock[num4]
                    if b >= 192:
                        num7 = b - 192 + 1
                    if 128 <= b < 192:
                        num8 = b - 128 + 1
                    if 64 <= b < 128:
                        num9 = b - 64
                        num8 = 1
                        flag = True
                    if b <= 63:
                        num8 = 1
                        num9 = b
                
                num10 += num7
                if num10 >= width:
                    num10 = 0
                    num11 += 1
                    flag = False
            else:
                # 修复循环逻辑，使其与C#版本完全一致
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
                            self.BMPimage.putpixel((num10, num11), colorpanel.thisColor(index))
                    num10 += 1
                    if num10 >= width:
                        num10 = 0
                        num11 += 1
                        flag = False
                    num13 += 1
                num8 -= 1
            num4 += 1
        
        return self.BMPimage


class BaseParser:
    """基础解析器类"""
    
    def __init__(self, file_data: Optional[bytes] = None):
        self.file_data = file_data
        
    def set_file_data(self, file_data: bytes):
        """设置要解析的文件数据"""
        self.file_data = file_data


class BaseImageParser(BaseParser):
    """基础图像解析器类，包含图像生成方法"""
    
    def __init__(self, file_data: Optional[bytes] = None):
        super().__init__(file_data)
        self.bmp_maker = BMPMaker()
        
    def make_bmp(self, width: int, height: int, start_offset: int, length: int, colorpanel: ColorPanel):
        """通用BMP生成方法"""
        if self.file_data is None:
            raise ValueError("file_data is None")
        return self.bmp_maker.makeBMP(width, height, self.file_data, start_offset, length, colorpanel)
        
    def make_face_bmp(self, start_offset: int, length: int, colorpanel: ColorPanel):
        """面部图像生成方法"""
        if self.file_data is None:
            raise ValueError("file_data is None")
        return self.bmp_maker.makeFaceBMP(self.file_data, start_offset, length, colorpanel)
        
    def make_bg_bmp(self, start_offset: int, length: int, colorpanel: ColorPanel):
        """背景图像生成方法"""
        if self.file_data is None:
            raise ValueError("file_data is None")
        return self.bmp_maker.makeBgBMP(self.file_data, start_offset, length, colorpanel)
        
    def make_fight_bmp(self, start_offset: int, length: int, colorpanel: ColorPanel):
        """战斗图像生成方法"""
        if self.file_data is None:
            raise ValueError("file_data is None")
        return self.bmp_maker.makeFightBMP(self.file_data, start_offset, length, colorpanel)
        
    def make_field_bmp(self, order: int, start_offset: int, length: int, colorpanel: ColorPanel, shaps: List[Optional['Image.Image']]):
        """地图图像生成方法"""
        if self.file_data is None:
            raise ValueError("file_data is None")
        return self.bmp_maker.makeFieldBMP(self.file_data, order, start_offset, length, colorpanel)
        
    def make_shap_bmp(self, width: int, height: int, start_offset: int, length: int, colorpanel: ColorPanel):
        """形状图像生成方法"""
        if self.file_data is None:
            raise ValueError("file_data is None")
        return self.bmp_maker.makeShapBMP(width, height, self.file_data, start_offset, length, colorpanel)
        
    def make_tai_bmp(self, start_offset: int, length: int, colorpanel: ColorPanel):
        """TAI图像生成方法"""
        if self.file_data is None:
            raise ValueError("file_data is None")
        return self.bmp_maker.makeTAIBMP(self.file_data, start_offset, length, colorpanel)
        
    def make_ani_bmp(self, start_offset: int, length: int, colorpanel: ColorPanel):
        """动画图像生成方法"""
        if self.file_data is None:
            raise ValueError("file_data is None")
        return self.bmp_maker.makeANIBMP(self.file_data, start_offset, length, colorpanel)
        
    def make_font_bmp(self, start_offset: int, length: int):
        """字体图像生成方法"""
        if self.file_data is None:
            raise ValueError("file_data is None")
        return self.bmp_maker.makeFontBMP(self.file_data, start_offset, length)