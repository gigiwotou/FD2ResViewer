import io
import os
import struct
from PIL import Image
import sys
from typing import Any, Optional

# 对应C#的DataBlock类
from PIL import ImageColor


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

class DataBlock:
    """数据块结构"""
    def __init__(self, startOffset, length):
        self.startOffset = startOffset
        self.length = length
        
    def __str__(self):
        return f"DataBlock(startOffset={self.startOffset}, length={self.length})"
    
    def __repr__(self):
        return self.__str__()

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
        self.shaps: list[Optional[Image.Image]] = [None] * 401  # 用于存储图块图像的数组

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
        stream = io.BytesIO(self.tempFontBMP)
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
                    if num4 < len(datablock):
                        index = datablock[num4]
                        num7 = 1
                        if 0 <= num10 < width and 0 <= num11 < height:
                            self.BMPimage.putpixel((num10, num11), colorpanel.thisColor(index))
                    num10 += num7
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
                    if num4 < len(datablock):
                        index = datablock[num4]
                        num7 = 1
                        if 0 <= num10 < width and 0 <= num11 < height:
                            self.BMPimage.putpixel((num10, num11), colorpanel.thisColor(index))
                    num10 += num7
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

import os
import struct
from PIL import Image

class Main:
    """FD2资源分析主类"""

    def __init__(self):
        self.fileDatas = None
        self.output_dir = 'output_images'
        self.bmp_maker = BMPMaker()
        
        # 初始化实例变量（不是类变量）
        # 统一变量命名规则：使用驼峰命名法，并在变量名中表明类型
        self.datablocksICON: list[Optional[DataBlock]] = [None] * 1681  # List[Optional[DataBlock]]
        self.datablocksBG: list[Optional[DataBlock]] = [None] * 57  # List[Optional[DataBlock]]
        self.datablocksTAI: list[Optional[DataBlock]] = [None] * 57  # List[Optional[DataBlock]]
        self.datablocksDATO: list[list[Optional[DataBlock]]] = [[None for _ in range(4)] for _ in range(137)]  # List[List[Optional[DataBlock]]]
        self.datablocksFDFIELD: list[Optional[DataBlock]] = [None] * 100  # List[Optional[DataBlock]]
        self.datablocksOTHER: list[Optional[DataBlock]] = [None] * 104  # List[Optional[DataBlock]]
        self.datablocksOTHERSubs: Optional[list[Optional[DataBlock]]] = None  # Optional[List[Optional[DataBlock]]]
        self.datablocksFDSHAP: list[list[Optional[DataBlock]]] = [[None for _ in range(401)] for _ in range(67)]  # List[List[Optional[DataBlock]]]
        self.subBlockCountsFDSHAP: list[int] = [0] * 67  # List[int]
        self.datablocksTXT: list[list[Optional[DataBlock]]] = [[None for _ in range(701)] for _ in range(35)]  # List[List[Optional[DataBlock]]]
        self.subBlockCountsTXT: list[int] = [0] * 35  # List[int]
        self.datablocksFIGANI: list[list[Optional[DataBlock]]] = [[None for _ in range(41)] for _ in range(409)]  # List[List[Optional[DataBlock]]]
        self.subBlockCountsFIGANI: list[int] = [0] * 409  # List[int]
        self.datablocksANI: list[list[Optional[DataBlock]]] = [[None for _ in range(100)] for _ in range(9)]  # List[List[Optional[DataBlock]]] - ANI文件有9个分段
        self.subBlockCountsANI: list[int] = [0] * 9  # List[int] - ANI文件有9个分段
        self.shapsDone: bool = False  # bool
        self.shaps: list[Optional[Image.Image]] = [None] * 401  # 用于存储图块图像的数组
        
        # 文件数据变量
        self.fileDatasBG: Optional[bytes] = None  # Optional[bytes]
        self.fileDatasDATO: Optional[bytes] = None  # Optional[bytes]

        self.fileDatasFDFIELD: Optional[bytes] = None  # Optional[bytes]
        self.fileDatasOTHER: Optional[bytes] = None  # Optional[bytes]
        self.fileDatasFDSHAP: Optional[bytes] = None  # Optional[bytes]
        self.fileDatasTXT: Optional[bytes] = None  # Optional[bytes]
        self.fileDatasFIGANI: Optional[bytes] = None  # Optional[bytes]
        self.fileDatasFD2: Optional[bytes] = None  # Optional[bytes]
        
        os.makedirs(self.output_dir, exist_ok=True)

    def AnalysisFDFIELD(self):
        array = [0] * 100
        num = 6
        # 确保self.fileDatas不为None
        if self.fileDatas is None:
            return
        while num <= 402:
            index = int((num - 6) / 4)
            # 确保索引在有效范围内
            if index < len(array) and num + 4 <= len(self.fileDatas):
                array[index] = struct.unpack('<I', self.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            # 确保索引在有效范围内
            if num5 < len(self.datablocksFDFIELD) and num5 + 1 < len(array):
                self.datablocksFDFIELD[num5] = DataBlock(array[num5], array[num5 + 1] - array[num5])
            num5 += 1
        # 处理最后一个数据块
        if num5 < len(self.datablocksFDFIELD) and num5 < len(array) and self.fileDatas is not None:
            self.datablocksFDFIELD[num5] = DataBlock(array[num5], len(self.fileDatas) - array[num5])

        # 进度条和列表框更新逻辑占位
        progress_max = 99
        num8 = 0
        while num8 <= 98:
            text = f"ID:{num8:03d}"
            # ListBoxImages.Items.Add(text)  # UI操作占位
            if num8 % 4 == 0:
                pass  # 进度条更新占位

            num8 += 3

    def AnalysisOTHER(self):
        """分析FDOTHER数据结构"""
        if self.fileDatas is None:
            return
        array = [0] * 104
        num = 6
        while num <= 418:  # 6 + (104-1)*4 = 418
            index = int((num - 6) / 4)
            if num + 4 <= len(self.fileDatas):
                array[index] = struct.unpack('<I', self.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            # 确保索引在有效范围内
            if num5 < len(self.datablocksOTHER) and num5 + 1 < len(array):
                self.datablocksOTHER[num5] = DataBlock(array[num5], array[num5 + 1] - array[num5])
            num5 += 1
        # 处理最后一个数据块
        if num5 < len(self.datablocksOTHER) and num5 < len(array) and self.fileDatas is not None:
            self.datablocksOTHER[num5] = DataBlock(array[num5], len(self.fileDatas) - array[num5])

        # 进度条和列表框更新逻辑占位
        progress_max = 103
        num8 = 0
        while num8 <= 102:
            text = f"ID:{num8:04d}"
            if num8 % 4 == 0:
                pass  # 进度条更新占位
            # 调用AnalysisOtherSubs处理子索引
            self.AnalysisOtherSubs(num8)
            num8 += 1
    
    def AnalysisOtherSubs(self, subIndex):
        if subIndex in (1, 14):
            # 添加None检查
            if self.datablocksOTHER[subIndex] is None or self.fileDatas is None:
                return
            datablock = self.datablocksOTHER[subIndex]
            if datablock is None:
                return
            num43 = datablock.startOffset + 6
            sWidth = struct.unpack('<h', self.fileDatas[datablock.startOffset : datablock.startOffset+2])[0]
            sHeight = struct.unpack('<h', self.fileDatas[datablock.startOffset+2 : datablock.startOffset+4])[0]
            num44 = struct.unpack('<h', self.fileDatas[datablock.startOffset+4 : datablock.startOffset+6])[0]
            self.datablocksOTHERSubs = [None] * (num44)
            array5 = [0] * num44
            num45 = num44 - 1
            num46 = 0
            while num46 <= num45:
                array5[num46] = struct.unpack('<I', self.fileDatas[num43 + num46*4 : num43 + (num46+1)*4])[0]
                num46 += 1

            num48 = num44 - 2
            num46 = 0
            while num46 <= num48:
                if self.datablocksOTHERSubs is not None:
                    self.datablocksOTHERSubs[num46] = DataBlock(array5[num46], array5[num46+1] - array5[num46])
                num46 += 1
            if self.datablocksOTHERSubs is not None:
                self.datablocksOTHERSubs[num46] = DataBlock(array5[num46], datablock.length - array5[num46])

            # 进度条和列表框更新逻辑占位
            num51 = 0
            while num51 < num44:
                text5 = f"ID:{num51:09d}"
                # ListBoxSecond.Items.Add(text5)
                if num51 % (num44 // 10) == 0:
                    pass  # 进度条更新
                num51 += 1

        elif subIndex == 2:
            # 添加None检查
            if self.datablocksOTHER[subIndex] is None or self.fileDatas is None:
                return
            datablock = self.datablocksOTHER[subIndex]
            if datablock is None:
                return
            startOffset2 = datablock.startOffset
            num34 = int(struct.unpack('<I', self.fileDatas[startOffset2:startOffset2+4])[0] / 4)
            array4 = [0] * num34
            self.datablocksOTHERSubs = [None] * num34  # type: ignore
            num36 = 0
            while num36 < num34:
                array4[num36] = struct.unpack('<I', self.fileDatas[startOffset2 + num36*4 : startOffset2 + (num36+1)*4])[0]
                num36 += 1

            num38 = num34 - 2
            num36 = 0
            while num36 <= num38:
                if self.datablocksOTHERSubs is not None:
                    self.datablocksOTHERSubs[num36] = DataBlock(array4[num36], array4[num36+1] - array4[num36])
                num36 += 1
            if self.datablocksOTHERSubs is not None:
                self.datablocksOTHERSubs[num36] = DataBlock(array4[num36], datablock.length - array4[num36])

            # 进度条和列表框更新逻辑占位
            num41 = 0
            while num41 < num34:
                text4 = f"ID:{num41:09d}"
                # ListBoxSecond.Items.Add(text4)
                if num41 % (num34 // 10) == 0:
                    pass  # 进度条更新
                num41 += 1

        elif subIndex == 4:
            # 添加None检查
            if self.datablocksOTHER[subIndex] is None:
                return
            datablock = self.datablocksOTHER[subIndex]
            if datablock is None:
                return
            obj = datablock.length / 32
            array2 = [i*32 for i in range(int(obj))]
            self.datablocksOTHERSubs = [None] * len(array2)  # type: ignore
            num17 = 0
            while num17 < len(array2)-1:
                if self.datablocksOTHERSubs is not None:
                    self.datablocksOTHERSubs[num17] = DataBlock(array2[num17], array2[num17+1] - array2[num17])
                num17 += 1
            if self.datablocksOTHERSubs is not None:
                self.datablocksOTHERSubs[num17] = DataBlock(array2[num17], datablock.length - array2[num17])

            # 进度条和列表框更新逻辑占位
            num22 = 0
            while num22 < len(array2):
                text2 = f"ID:{num22:09d}"
                # ListBoxSecond.Items.Add(text2)
                if num22 % (len(array2) // 10) == 0:
                    pass  # 进度条更新
                num22 += 1

        elif subIndex in (5, 6, 9, 96):
            # 添加None检查
            if self.datablocksOTHER[subIndex] is None or self.fileDatas is None:
                return
            datablock = self.datablocksOTHER[subIndex]
            if datablock is None:
                return
            num3 = datablock.startOffset + 4
            # print(f"解析数据段 subIndex：{subIndex}. 起始地址: 0x{datablock.startOffset:X}")
            num4 = struct.unpack('<h', self.fileDatas[num3:num3+2])[0]
            # print(f"subIndex: {subIndex}, num4: {num4}")
            array = [0] * num4
            self.datablocksOTHERSubs = [None] * num4  # type: ignore
            num6 = 0
            while num6 < num4:
                array[num6] = struct.unpack('<I', self.fileDatas[num3+2 + num6*4 : num3+6 + num6*4])[0]
                # print(f"subIndex: {subIndex}, num6: {num6}, array[num6]: {array[num6]}")
                # print(f"subIndex: {subIndex}, num6: {num6}, array[num6]: 0x{datablock.startOffset + array[num6]:X}")
                num6 += 1

            num9 = num4 - 2
            num6 = 0
            while num6 <= num9:
                if self.datablocksOTHERSubs is not None:
                    self.datablocksOTHERSubs[num6] = DataBlock(array[num6], array[num6+1] - array[num6])
                num6 += 1
            if self.datablocksOTHERSubs is not None:
                self.datablocksOTHERSubs[num6] = DataBlock(array[num6], datablock.length - array[num6])

            # 进度条和列表框更新逻辑占位
            num12 = 0
            while num12 < num4:
                text = f"ID:{num12:09d}"
                # ListBoxSecond.Items.Add(text)
                if num12 % (num4 // 10) == 0:
                    pass  # 进度条更新
                num12 += 1

        elif subIndex in (7, 12, 13, 63):
            # 添加None检查
            if self.datablocksOTHER[subIndex] is None or self.fileDatas is None:
                return
            datablock = self.datablocksOTHER[subIndex]
            if datablock is None:
                return
            num24 = datablock.startOffset + 6
            short_value = struct.unpack('<h', self.fileDatas[num24:num24+2])[0]
            num25 = int(round((short_value - 6) / 4.0 - 1.0))
            num25 = max(0, num25)
            array3 = [0] * num25  # 数组长度匹配C#的num25
            self.datablocksOTHERSubs = [None] * num25  # type: ignore
            num26 = num25 - 1  # 循环上限保持num25-1，与C#一致
            num27 = 0
            while num27 <= num26:
                array3[num27] = struct.unpack('<I', self.fileDatas[num24 + num27*4 : num24 + (num27+1)*4])[0]
                num27 += 1

            num29 = len(array3) - 2  # 修正为Python的len()语法
            num27 = 0
            while num27 <= num29:
                if self.datablocksOTHERSubs is not None:
                    self.datablocksOTHERSubs[num27] = DataBlock(array3[num27], array3[num27+1] - array3[num27])
                num27 += 1
            if self.datablocksOTHERSubs is not None:
                self.datablocksOTHERSubs[num27] = DataBlock(array3[num27], datablock.length - array3[num27])

            # 进度条和列表框更新逻辑占位
            num31 = num25 - 1  # 对应C#的num31 = num25 - 1
            num32 = 0
            while num32 <= num31:
                text3 = f"ID:{num32:09d}"
                # ListBoxSecond.Items.Add(text3)
                if num25 >= 10 and num32 % (num25 // 10) == 0:
                    pass  # 进度条更新
                num32 += 1

        elif subIndex in (10, 15):
            # 添加None检查
            if self.datablocksOTHER[subIndex] is None or self.fileDatas is None:
                return
            datablock = self.datablocksOTHER[subIndex]
            if datablock is None:
                return
            # 调用BMPMaker生成面部图像
            bmp_maker = BMPMaker()
            sWidth = struct.unpack('<h', self.fileDatas[datablock.startOffset : datablock.startOffset+2])[0]
            sHeight = struct.unpack('<h', self.fileDatas[datablock.startOffset+2 : datablock.startOffset+4])[0]
            image = bmp_maker.makeFaceBMP(
                self.fileDatas,
                datablock.startOffset,
                datablock.length,
                ColorPanel(1)  # 使用灰色调色板
            )
            image_path = os.path.join(self.output_dir, f'face_{subIndex}.png')
            image.save(image_path)

        elif subIndex in (11, 16, 17, 46, 47, 56, 59, 60, 61, 62, 69, 70, 71, 72, 73, 74, 75, 97, 98, 100):
            # 添加None检查
            if self.datablocksOTHER[subIndex] is None or self.fileDatas is None:
                return
            datablock = self.datablocksOTHER[subIndex]
            if datablock is None:
                return
            sWidth = struct.unpack('<h', self.fileDatas[datablock.startOffset : datablock.startOffset+2])[0]
            sHeight = struct.unpack('<h', self.fileDatas[datablock.startOffset+2 : datablock.startOffset+4])[0]
            bmp_maker = BMPMaker()
            # 使用资源文件初始化调色板
            # colorpanel = ColorPanel(1)
            if 73 < subIndex < 76:
                colorpanel = ColorPanel(2)
            else:
                colorpanel = ColorPanel(1)
            image = bmp_maker.makeShapBMP(
                sWidth, sHeight,
                self.fileDatas,
                datablock.startOffset + 4,
                datablock.length - 4,
                colorpanel
            )
            image_path = os.path.join(self.output_dir, f'shap_{subIndex}.png')
            image.save(image_path)
        elif subIndex == 55:
            # 添加None检查
            if self.datablocksOTHER[subIndex] is None or self.fileDatas is None:
                return
            datablock = self.datablocksOTHER[subIndex]
            if datablock is None:
                return
            sWidth = struct.unpack('<h', self.fileDatas[datablock.startOffset : datablock.startOffset+2])[0]
            sHeight = struct.unpack('<h', self.fileDatas[datablock.startOffset+2 : datablock.startOffset+4])[0]
            bmp_maker = BMPMaker()
            image = bmp_maker.makeBMP(
                sWidth, sHeight,
                self.fileDatas,
                datablock.startOffset + 4,
                datablock.length - 4,
                ColorPanel(1)
            )
            image_path = os.path.join(self.output_dir, f'other_{subIndex}.png')
            image.save(image_path)
        elif subIndex == 79:
            # 添加None检查
            if self.datablocksOTHER[subIndex] is None or self.fileDatas is None:
                return
            datablock = self.datablocksOTHER[subIndex]
            if datablock is None:
                return
            num3 = datablock.startOffset + 2
            print(f"解析数据段 subIndex：{subIndex}. 起始地址: 0x{datablock.startOffset:X}")
            # 从num3 + 4位置开始读取num4
            num4 = struct.unpack('<h', self.fileDatas[num3:num3+2])[0]
            print(f"subIndex: {subIndex}, num4: {num4}")

            array = [0] * num4
            self.datablocksOTHERSubs = [None] * num4  # type: ignore
            num6 = 0
            while num6 < num4:
                array[num6] = struct.unpack('<I', self.fileDatas[num3+6 + num6*4 : num3+10 + num6*4])[0]
                print(f"subIndex: {subIndex}, num6: {num6}, array[num6]: 0x{datablock.startOffset + array[num6]:X}")
                num6 += 1

            num9 = num4 - 2
            num6 = 0
            while num6 <= num9:
                if self.datablocksOTHERSubs is not None:
                    self.datablocksOTHERSubs[num6] = DataBlock(array[num6], array[num6+1] - array[num6])
                if self.datablocksOTHERSubs is not None and self.datablocksOTHERSubs[num6] is not None:
                    datablock_sub = self.datablocksOTHERSubs[num6]
                    if datablock_sub is not None:
                        print(f"subIndex: {subIndex}, num6: {num6}, array[num6]: 0x{array[num6]:X}, length: {datablock_sub.length}")
                num6 += 1
        
            if self.datablocksOTHERSubs is not None and num6 < len(self.datablocksOTHERSubs):
                self.datablocksOTHERSubs[num6] = DataBlock(array[num6], datablock.length - array[num6])
          
        else:
            print(f"未解析数据段 subIndex：{subIndex}. 起始地址: 0x{self.datablocksOTHER[subIndex].startOffset:X}")

    def AnalysisOtherSubsImage(self, subIndex):
        if self.datablocksOTHERSubs and len(self.datablocksOTHERSubs) > 0:
            # Converted from ListBoxSecond_SelectedIndexChanged in MainForm.cs
            num = subIndex
            num3 = num
            # print(f"len:{len(self.datablocksOTHERSubs)}, subIndex:{subIndex}")
            for num2 in range(len(self.datablocksOTHERSubs)):
                if num3 == 1 or num3 == 96:
                    # 添加None检查
                    if self.datablocksOTHER[num] is None or self.datablocksOTHERSubs[num2] is None:
                        continue
                    datablock = self.datablocksOTHER[num]
                    datablockSub = self.datablocksOTHERSubs[num2]
                    if datablock is None or datablockSub is None:
                        continue
                    start_offset = datablock.startOffset + datablockSub.startOffset
                    sWidth = 24  # 默认值
                    sHeight = 24  # 默认值
                    if num == 96:
                        sWidth = 24
                        sHeight = 24
                    else:
                        # sWidth = struct.unpack('<h', self.fileDatas[start_offset:start_offset+2])[0]
                        # sHeight = struct.unpack('<h', self.fileDatas[start_offset+2:start_offset+4])[0]
                        if datablock is not None and self.fileDatas is not None:
                            sWidth = struct.unpack('<h', self.fileDatas[datablock.startOffset : datablock.startOffset+2])[0]
                            sHeight = struct.unpack('<h', self.fileDatas[datablock.startOffset+2 : datablock.startOffset+4])[0]
                    # print(f"subIndex: {subIndex}, num2: {num2:03d}, start_offset: {start_offset}, sWidth: {sWidth}, sHeight: {sHeight}")

                    # 生成形状图像                
                    image = self.bmp_maker.makeShapBMP(
                        sWidth, sHeight,
                        self.fileDatas,
                        start_offset,
                        datablockSub.length,
                        ColorPanel(1)
                    )
                    image_path = os.path.join(self.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                    image.save(image_path)
 
                if num3 == 2:
                    # 添加None检查
                    if self.datablocksOTHER[num] is None or self.datablocksOTHERSubs[num2] is None:
                        continue
                    datablock = self.datablocksOTHER[num]
                    datablockSub = self.datablocksOTHERSubs[num2]
                    if datablock is None or datablockSub is None:
                        continue
                    start_offset = datablock.startOffset + datablockSub.startOffset
                    
                    sWidth = 0  # 默认值
                    sHeight = 0  # 默认值
                    if self.fileDatas is not None and start_offset + 2 <= len(self.fileDatas) and start_offset + 4 <= len(self.fileDatas):
                        sWidth = struct.unpack('<h', self.fileDatas[start_offset:start_offset+2])[0]
                        sHeight = struct.unpack('<h', self.fileDatas[start_offset+2:start_offset+4])[0]

                    data_offset = start_offset + 4
                    
                    # 生成其他类型图像                      
                    image = self.bmp_maker.makeBMP(
                        sWidth, sHeight,
                        self.fileDatas,
                        data_offset,
                        datablockSub.length - 4,
                        ColorPanel(1)
                    )
                    image_path = os.path.join(self.output_dir, f'other_{subIndex}_{num2:03d}.png')
                    image.save(image_path)
                    

                if num3 == 4:
                    # 添加None检查
                    if self.datablocksOTHER[num3] is None or self.datablocksOTHERSubs[num2] is None:
                        continue
                    datablock = self.datablocksOTHER[num3]
                    datablockSub = self.datablocksOTHERSubs[num2]
                    if datablock is None or datablockSub is None:
                        continue
                    data_offset = datablock.startOffset + datablockSub.startOffset
                    
                    # 生成字体图像                
                    image = self.bmp_maker.makeFontBMP(
                        self.fileDatas,
                        data_offset,
                        datablockSub.length
                    )
                    image_path = os.path.join(self.output_dir, f'font_{subIndex}_{num2:03d}.png')
                    image.save(image_path)
                   
                if num3 == 5:
                    # 添加None检查
                    if self.datablocksOTHER[num3] is None or self.datablocksOTHERSubs[num2] is None:
                        continue
                    datablock = self.datablocksOTHER[num3]
                    datablockSub = self.datablocksOTHERSubs[num2]
                    if datablock is None or datablockSub is None:
                        continue
                    start_offset = datablock.startOffset + datablockSub.startOffset

                    sWidth = 0  # 默认值
                    sHeight = 0  # 默认值
                    if self.fileDatas is not None and start_offset + 2 <= len(self.fileDatas) and start_offset + 4 <= len(self.fileDatas):
                        sWidth = struct.unpack('<h', self.fileDatas[start_offset:start_offset+2])[0]
                        sHeight = struct.unpack('<h', self.fileDatas[start_offset+2:start_offset+4])[0]

                    # print(f"subIndex: {subIndex}, num2: {num2:03d}, start_offset: {start_offset}, sWidth: {sWidth}, sHeight: {sHeight}, data_offset: {start_offset}")
                    if num2 < 20:
                        data_offset = start_offset + 4
                        # 生成其他类型图像                    
                        image = self.bmp_maker.makeBMP(
                            sWidth, sHeight,
                            self.fileDatas,
                            data_offset,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'other_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 < 23:
                        data_offset = start_offset
                        if self.fileDatas is not None and data_offset + 4 <= len(self.fileDatas):
                            sWidth = struct.unpack('<h', self.fileDatas[data_offset:data_offset+2])[0]
                            sHeight = struct.unpack('<h', self.fileDatas[data_offset+2:data_offset+4])[0]
                        # 生成面部图像                
                        image = self.bmp_maker.makeFaceBMP(
                            self.fileDatas,
                            data_offset,
                            datablockSub.length,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'face_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 < 31:
                        data_offset = start_offset + 4
                        # 生成其他类型图像                    
                        image = self.bmp_maker.makeBMP(
                            sWidth, sHeight,
                            self.fileDatas,
                            data_offset,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'other_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 < 53:
                        image = self.bmp_maker.makeShapBMP(
                            sWidth, sHeight,
                            self.fileDatas,
                            start_offset + 4,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 < 64 and num2 != 59:
                        data_offset = start_offset + 4
                        # 生成其他类型图像                    
                        image = self.bmp_maker.makeBMP(
                            sWidth, sHeight,
                            self.fileDatas,
                            data_offset,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'other_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 != 59:
                        if num2 < 119 and num2 != 93:
                            data_offset = start_offset
                            if self.fileDatas is not None and data_offset + 4 <= len(self.fileDatas):
                                sWidth = struct.unpack('<h', self.fileDatas[data_offset:data_offset+2])[0]
                                sHeight = struct.unpack('<h', self.fileDatas[data_offset+2:data_offset+4])[0]
                            # 生成面部图像                
                            image = self.bmp_maker.makeFaceBMP(
                                self.fileDatas,
                                data_offset,
                                datablockSub.length,
                                ColorPanel(1)
                            )
                            image_path = os.path.join(self.output_dir, f'face_{subIndex}_{num2:03d}.png')
                            image.save(image_path)
                        else:
                            image = self.bmp_maker.makeShapBMP(
                            sWidth, sHeight,
                            self.fileDatas,
                            start_offset + 4,
                            datablockSub.length - 4,
                            ColorPanel(1)
                            )
                            image_path = os.path.join(self.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                            image.save(image_path)

                if num3 == 7:
                    # 添加None检查
                    if self.datablocksOTHER[num] is None or self.datablocksOTHERSubs[num2] is None:
                        continue
                    datablock = self.datablocksOTHER[num]
                    datablockSub = self.datablocksOTHERSubs[num2]
                    if datablock is None or datablockSub is None:
                        continue
                    start_offset = datablock.startOffset + datablockSub.startOffset
                    sWidth = 0  # 默认值
                    sHeight = 0  # 默认值
                    if self.fileDatas is not None and start_offset + 2 <= len(self.fileDatas) and start_offset + 4 <= len(self.fileDatas):
                        sWidth = struct.unpack('<h', self.fileDatas[start_offset:start_offset+2])[0]
                        sHeight = struct.unpack('<h', self.fileDatas[start_offset+2:start_offset+4])[0]
                    color_panel = ColorPanel(3)  # Create new color panel with ID 3
                    data_offset = start_offset + 4
                    # print(f"subIndex: {subIndex}, num2: {num2:03d}, start_offset: {start_offset}, sWidth: {sWidth}, sHeight: {sHeight}, data_offset: {data_offset}")
                    # 生成形状图像                
                    image = self.bmp_maker.makeShapBMP(
                        sWidth, sHeight,
                        self.fileDatas,
                        data_offset,
                        datablockSub.length - 4,
                        color_panel
                    )
                    image_path = os.path.join(self.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                    image.save(image_path)

                if num3 in (6, 9):
                    # 添加None检查
                    if self.datablocksOTHER[num3] is None or self.datablocksOTHERSubs[num2] is None:
                        continue
                    datablock = self.datablocksOTHER[num3]
                    datablockSub = self.datablocksOTHERSubs[num2]
                    if datablock is None or datablockSub is None:
                        continue
                    start_offset = datablock.startOffset + datablockSub.startOffset
                    sWidth = 0  # 默认值
                    sHeight = 0  # 默认值
                    if self.fileDatas is not None and start_offset + 2 <= len(self.fileDatas) and start_offset + 4 <= len(self.fileDatas):
                        sWidth = struct.unpack('<h', self.fileDatas[start_offset:start_offset+2])[0]
                        sHeight = struct.unpack('<h', self.fileDatas[start_offset+2:start_offset+4])[0]
                    data_offset = start_offset
                    if self.fileDatas is not None and data_offset + 2 <= len(self.fileDatas) and data_offset + 4 <= len(self.fileDatas):
                        sWidth = struct.unpack('<h', self.fileDatas[data_offset:data_offset+2])[0]
                        sHeight = struct.unpack('<h', self.fileDatas[data_offset+2:data_offset+4])[0]
                
                    # 生成面部图像                
                    image = self.bmp_maker.makeFaceBMP(
                        self.fileDatas,
                        data_offset,
                        datablockSub.length,
                        ColorPanel(1)
                    )
                    image_path = os.path.join(self.output_dir, f'face_{subIndex}_{num2:03d}.png')
                    image.save(image_path)
                   

                if num3 in (12, 63):
                    # 添加None检查
                    if self.datablocksOTHER[num3] is None or self.datablocksOTHERSubs[num2] is None:
                        continue
                    datablock = self.datablocksOTHER[num3]
                    datablockSub = self.datablocksOTHERSubs[num2]
                    if datablock is None or datablockSub is None:
                        continue
                    start_offset = datablock.startOffset + datablockSub.startOffset
                    sWidth = 0  # 默认值
                    sHeight = 0  # 默认值
                    if self.fileDatas is not None and start_offset + 2 <= len(self.fileDatas) and start_offset + 4 <= len(self.fileDatas):
                        sWidth = struct.unpack('<h', self.fileDatas[start_offset:start_offset+2])[0]
                        sHeight = struct.unpack('<h', self.fileDatas[start_offset+2:start_offset+4])[0]
                    
                    if num2 == 0 or (num2 >= 23 and num2 <= 29):
                        data_offset = start_offset + 4
                        # 生成形状图像                      
                        image = self.bmp_maker.makeShapBMP(
                            sWidth, sHeight,
                            self.fileDatas,
                            data_offset,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 == 1 or num2 == 2 or (num2 >= 11 and num2 < 22):
                        data_offset = start_offset
                        if self.fileDatas is not None and data_offset + 2 <= len(self.fileDatas) and data_offset + 4 <= len(self.fileDatas):
                            sWidth = struct.unpack('<h', self.fileDatas[data_offset:data_offset+2])[0]
                            sHeight = struct.unpack('<h', self.fileDatas[data_offset+2:data_offset+4])[0]
                        # 生成面部图像                    
                        image = self.bmp_maker.makeFaceBMP(
                            self.fileDatas,
                            data_offset,
                            datablockSub.length,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'face_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    else:
                        data_offset = start_offset + 4
                        # 生成其他类型图像                    
                        image = self.bmp_maker.makeBMP(
                            sWidth, sHeight,
                            self.fileDatas,
                            data_offset,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'other_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    

                if num3 == 13:
                    # 添加None检查
                    if self.datablocksOTHER[num3] is None or self.datablocksOTHERSubs[num2] is None:
                        continue
                    datablock = self.datablocksOTHER[num3]
                    datablockSub = self.datablocksOTHERSubs[num2]
                    if datablock is None or datablockSub is None:
                        continue
                    start_offset = datablock.startOffset + datablockSub.startOffset
                    sWidth = 0  # 默认值
                    sHeight = 0  # 默认값
                    if self.fileDatas is not None and start_offset + 2 <= len(self.fileDatas) and start_offset + 4 <= len(self.fileDatas):
                        sWidth = struct.unpack('<h', self.fileDatas[start_offset:start_offset+2])[0]
                        sHeight = struct.unpack('<h', self.fileDatas[start_offset+2:start_offset+4])[0]
                    
                    if num2 == 0:
                        data_offset = start_offset + 4
                        # 生成形状图像                      
                        image = self.bmp_maker.makeShapBMP(
                            sWidth, sHeight,
                            self.fileDatas,
                            data_offset,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 == 1 or num2 == 2 or num2 >= 11:
                        data_offset = start_offset
                        if self.fileDatas is not None and data_offset + 2 <= len(self.fileDatas) and data_offset + 4 <= len(self.fileDatas):
                            sWidth = struct.unpack('<h', self.fileDatas[data_offset:data_offset+2])[0]
                            sHeight = struct.unpack('<h', self.fileDatas[data_offset+2:data_offset+4])[0]
                        # 生成面部图像                    
                        image = self.bmp_maker.makeFaceBMP(
                            self.fileDatas,
                            data_offset,
                            datablockSub.length,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'face_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    else:
                        data_offset = start_offset + 4
                        # 生成其他类型图像                    
                        image = self.bmp_maker.makeBMP(
                            sWidth, sHeight,
                            self.fileDatas,
                            data_offset,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'other_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    

                if num3 == 14:
                    # 添加None检查
                    if self.datablocksOTHER[num] is None or self.datablocksOTHERSubs[num2] is None:
                        continue
                    datablock = self.datablocksOTHER[num]
                    datablockSub = self.datablocksOTHERSubs[num2]
                    if datablock is None or datablockSub is None:
                        continue
                    start_offset = datablock.startOffset + datablockSub.startOffset
                    sWidth = 0  # 默认값
                    sHeight = 0  # 默认값
                    if self.fileDatas is not None and start_offset + 2 <= len(self.fileDatas) and start_offset + 4 <= len(self.fileDatas):
                        sWidth = struct.unpack('<h', self.fileDatas[start_offset:start_offset+2])[0]
                        sHeight = struct.unpack('<h', self.fileDatas[start_offset+2:start_offset+4])[0]
                    
                    if num2 == 0 or num2 >= 23:
                        data_offset = start_offset + 4
                        # 生成形状图像                    
                        image = self.bmp_maker.makeShapBMP(
                            sWidth, sHeight,
                            self.fileDatas,
                            data_offset,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 == 1 or num2 == 2 or (num2 >= 11 and num2 < 23):
                        data_offset = start_offset
                        if self.fileDatas is not None and data_offset + 2 <= len(self.fileDatas) and data_offset + 4 <= len(self.fileDatas):
                            sWidth = struct.unpack('<h', self.fileDatas[data_offset:data_offset+2])[0]
                            sHeight = struct.unpack('<h', self.fileDatas[data_offset+2:data_offset+4])[0]
                        # 生成面部图像                    
                        image = self.bmp_maker.makeFaceBMP(
                            self.fileDatas,
                            data_offset,
                            datablockSub.length,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'face_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    else:
                        data_offset = start_offset + 4
                        # 生成其他类型图像                    
                        image = self.bmp_maker.makeBMP(
                            sWidth, sHeight,
                            self.fileDatas,
                            data_offset,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'other_{subIndex}_{num2:03d}.png')
                        image.save(image_path)

                # if num3 == 79:
                #     # 添加None检查
                #     if self.datablocksOTHER[num3] is None or self.datablocksOTHERSubs[num2] is None:
                #         continue
                #     datablock = self.datablocksOTHER[num3]
                #     datablockSub = self.datablocksOTHERSubs[num2]
                #     if datablock is None or datablockSub is None:
                #         continue
                #     start_offset = datablock.startOffset + datablockSub.startOffset

                #     sWidth = 0 
                #     sHeight = 0  
                #     if self.fileDatas is not None and start_offset + 2 <= len(self.fileDatas) and start_offset + 4 <= len(self.fileDatas):
                #         sWidth = struct.unpack('<h', self.fileDatas[start_offset:start_offset+2])[0]
                #         sHeight = struct.unpack('<h', self.fileDatas[start_offset+2:start_offset+4])[0]

                #     # print(f"subIndex: {subIndex}, num2: {num2:03d}, start_offset: {start_offset}, sWidth: {sWidth}, sHeight: {sHeight}, data_offset: {start_offset}")
                    
                #     data_offset = start_offset + 4
                #     # 生成其他类型图像                    
                #     image = self.bmp_maker.makeBMP(
                #         sWidth, sHeight,
                #         self.fileDatas,
                #         data_offset,
                #         datablockSub.length - 4,
                #         ColorPanel(1)
                #     )
                #     image_path = os.path.join(self.output_dir, f'other_{subIndex}_{num2:03d}.png')
                #     image.save(image_path)

    def AnalysisICON(self):
        array = [0] * 1681
        num = 6
        # 确保self.fileDatas不为None
        if self.fileDatas is None:
            return
        while num <= 6726:
            index = int((num - 6) / 4)
            # 确保索引在有效范围内
            if index < len(array) and num + 4 <= len(self.fileDatas):
                array[index] = struct.unpack('<I', self.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            # 确保索引在有效范围内
            if num5 < len(self.datablocksICON):
                self.datablocksICON[num5] = DataBlock(array[num5], array[num5 + 1] - array[num5])
            num5 += 1
        # 处理最后一个数据块
        if num5 < len(self.datablocksICON) and num5 < len(array) and self.fileDatas is not None:
            self.datablocksICON[num5] = DataBlock(array[num5], len(self.fileDatas) - array[num5])

    def AnalysisFDSHAP(self):
        if self.fileDatasFDSHAP is None:
            return
        array = [0] * 67
        num = 6
        while num <= 270:
            index = int((num - 6) / 4)
            if num + 4 <= len(self.fileDatasFDSHAP):
                array[index] = struct.unpack('<I', self.fileDatasFDSHAP[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            if array[num5] + 6 <= len(self.fileDatasFDSHAP):
                self.subBlockCountsFDSHAP[num5] = struct.unpack('<h', self.fileDatasFDSHAP[array[num5]+4 : array[num5]+6])[0]
            subBlockCount = self.subBlockCountsFDSHAP[num5] - 1
            array2 = [0] * (subBlockCount + 1)
            num9 = 0
            while num9 <= subBlockCount:
                if array[num5] + 10 + num9*4 <= len(self.fileDatasFDSHAP):
                    array2[num9] = array[num5] + struct.unpack('<I', self.fileDatasFDSHAP[array[num5]+6+num9*4 : array[num5]+10+num9*4])[0]
                num9 += 1

            subBlockIndexMax = self.subBlockCountsFDSHAP[num5] - 2
            num9 = 0
            while num9 <= subBlockIndexMax:
                if num5 < len(self.datablocksFDSHAP) and num9 < len(self.datablocksFDSHAP[num5]):
                    self.datablocksFDSHAP[num5][num9] = DataBlock(array2[num9], array2[num9+1] - array2[num9])
                num9 += 1
            if num5 < len(self.datablocksFDSHAP) and num9 < len(self.datablocksFDSHAP[num5]):
                self.datablocksFDSHAP[num5][num9] = DataBlock(array2[num9], array[num5+1] - array2[num9])
            num5 += 2

        # 进度条和列表框更新逻辑占位
        progress_max = 66
        mainBlockIndex = 0
        while mainBlockIndex <= 66:
            subBlockCount = self.subBlockCountsFDSHAP[mainBlockIndex] - 1
            subBlockIndex = 0
            while subBlockIndex <= subBlockCount:
                text = f"ID:{mainBlockIndex:03d}-{subBlockIndex:04d}"
                # ListBoxImages.Items.Add(text)  # UI操作占位
                subBlockIndex += 1
            if mainBlockIndex % 10 == 0:
                pass  # 进度条更新占位
            mainBlockIndex += 1
        self.shapsDone = True

    def AnalysisTXT(self):
        """分析FDTXT数据结构"""
        if self.fileDatas is None:
            return
        array = [0] * 35
        num = 6
        while num <= 142:
            index = int((num - 6) / 4)
            if num + 4 <= len(self.fileDatas):
                array[index] = struct.unpack('<I', self.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        mainBlockIndex = 0
        while mainBlockIndex <= num4:
            if array[mainBlockIndex] + 2 <= len(self.fileDatas):
                self.subBlockCountsTXT[mainBlockIndex] = int(struct.unpack('<h', self.fileDatas[array[mainBlockIndex]:array[mainBlockIndex]+2])[0] / 2)
            subBlockCount = self.subBlockCountsTXT[mainBlockIndex] - 1
            array2 = [0] * (subBlockCount + 1)
            subBlockIndex = 0
            while subBlockIndex <= subBlockCount:
                if array[mainBlockIndex] + (subBlockIndex+1)*2 <= len(self.fileDatas):
                    array2[subBlockIndex] = array[mainBlockIndex] + struct.unpack('<h', self.fileDatas[array[mainBlockIndex] + subBlockIndex*2 : array[mainBlockIndex] + (subBlockIndex+1)*2])[0]
                subBlockIndex += 1

            subBlockIndexMax = self.subBlockCountsTXT[mainBlockIndex] - 2
            subBlockIndex = 0
            while subBlockIndex <= subBlockIndexMax:
                # 确保不会越界
                if mainBlockIndex < len(self.datablocksTXT) and subBlockIndex < len(self.datablocksTXT[mainBlockIndex]):
                    self.datablocksTXT[mainBlockIndex][subBlockIndex] = DataBlock(array2[subBlockIndex], array2[subBlockIndex+1] - array2[subBlockIndex])
                subBlockIndex += 1
            # 处理最后一个数据块
            if mainBlockIndex < len(self.datablocksTXT) and subBlockIndex < len(self.datablocksTXT[mainBlockIndex]):
                self.datablocksTXT[mainBlockIndex][subBlockIndex] = DataBlock(array2[subBlockIndex], array[mainBlockIndex+1] - array2[subBlockIndex])
            mainBlockIndex += 1

        # 进度条和列表框更新逻辑占位
        progress_max = 34
        mainBlockIndex = 0
        while mainBlockIndex <= 33:
            if mainBlockIndex < len(self.subBlockCountsTXT):
                subBlockCount = self.subBlockCountsTXT[mainBlockIndex] - 1
                subBlockIndex = 0
                while subBlockIndex <= subBlockCount:
                    text = f"ID:{mainBlockIndex:04d}-{subBlockIndex:04d}"
                    # ListBoxImages.Items.Add(text)  # UI操作占位
                    subBlockIndex += 1
            if mainBlockIndex % 30 == 0:
                pass  # 进度条更新占位
            mainBlockIndex += 1

    def AnalysisDATO(self):
        """分析DATO数据结构"""
        if self.fileDatas is None:
            return
        array = [0] * 137
        num = 6
        while num <= 550:
            index = int((num - 6) / 4)
            if num + 4 <= len(self.fileDatas):
                array[index] = struct.unpack('<I', self.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            array2 = [0] * 4
            num8 = 0
            while num8 <= 3:
                if array[num5] + (num8+1)*4 <= len(self.fileDatas):
                    array2[num8] = array[num5] + struct.unpack('<I', self.fileDatas[array[num5] + num8*4 : array[num5] + (num8+1)*4])[0]
                num8 += 1

            num8 = 0
            while num8 <= 2:
                # 确保不会越界
                if num5 < len(self.datablocksDATO) and num8 < len(self.datablocksDATO[num5]):
                    self.datablocksDATO[num5][num8] = DataBlock(array2[num8], array2[num8+1] - array2[num8])
                num8 += 1
            # 处理最后一个数据块
            if num5 < len(self.datablocksDATO) and num8 < len(self.datablocksDATO[num5]):
                self.datablocksDATO[num5][num8] = DataBlock(array2[num8], array[num5+1] - array2[num8])
            num5 += 1

    def AnalysisBG(self):
        """分析BG数据结构"""
        if self.fileDatas is None:
            return
        array = [0] * 57
        num = 6
        while num <= 230:
            index = int((num - 6) / 4)
            if num + 4 <= len(self.fileDatas):
                array[index] = struct.unpack('<I', self.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            # 确保不会越界
            if num5 < len(self.datablocksBG):
                self.datablocksBG[num5] = DataBlock(array[num5], array[num5 + 1] - array[num5])
            num5 += 1
        # 处理最后一个数据块
        if num5 < len(self.datablocksBG):
            self.datablocksBG[num5] = DataBlock(array[num5], len(self.fileDatas) - array[num5])

    def AnalysisTAI(self):
        """分析TAI数据结构（专用）"""
        if self.fileDatas is None:
            return
        array = [0] * 57
        num = 6
        while num <= 230:
            index = int((num - 6) / 4)
            if num + 4 <= len(self.fileDatas):
                array[index] = struct.unpack('<I', self.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            # 确保不会越界
            if num5 < len(self.datablocksTAI):
                self.datablocksTAI[num5] = DataBlock(array[num5], array[num5 + 1] - array[num5])
            num5 += 1
        # 处理最后一个数据块
        if num5 < len(self.datablocksTAI):
            self.datablocksTAI[num5] = DataBlock(array[num5], len(self.fileDatas) - array[num5])

    def AnalysisFIGANI(self):
        """分析FIGANI数据结构
        对应C#版本的AnalysisFIGANI方法
        """
        # 创建一个大小为409的数组来存储偏移量
        array = [0] * 409
        num = 6
        
        # 确保self.fileDatas不为None
        if self.fileDatas is None:
            return
        
        # 读取偏移量数据
        while num <= 1638:
            # 与C#版本保持一致：使用四舍五入计算索引
            index = int(round((num - 6) / 4.0))
            # 确保索引在有效范围内
            if index < len(array) and num + 4 <= len(self.fileDatas):
                array[index] = struct.unpack('<I', self.fileDatas[num:num+4])[0]
            num += 4
        
        # 用于存储子块偏移量的数组
        array2 = [0] * 41
        num4 = len(array) - 2  # 对应C#中的array.Length - 2
        num5 = 0
        
        # 处理每个FIGANI块
        while num5 <= num4:
            # 读取子块数量
            if array[num5] + 1 <= len(self.fileDatas):
                self.subBlockCountsFIGANI[num5] = self.fileDatas[array[num5]]
            else:
                self.subBlockCountsFIGANI[num5] = 0
                num5 += 1
                continue
            
            num8 = self.subBlockCountsFIGANI[num5] - 1
            num9 = 0
            
            # 读取子块偏移量
            while num9 <= num8:
                if array[num5] + 8 + num9 * 4 + 4 <= len(self.fileDatas) and num9 < len(array2):
                    array2[num9] = array[num5] + struct.unpack('<I', self.fileDatas[array[num5] + 8 + num9 * 4 : array[num5] + 8 + (num9+1)*4])[0]
                num9 += 1
            
            # 创建DataBlock对象
            num11 = self.subBlockCountsFIGANI[num5] - 2
            num9 = 0
            
            while num9 <= num11:
                if num9 + 1 < len(array2):
                    self.datablocksFIGANI[num5][num9] = DataBlock(array2[num9], array2[num9 + 1] - array2[num9])
                num9 += 1
            
            # 处理最后一个子块
            if num9 < len(array2) and num5 + 1 < len(array):
                self.datablocksFIGANI[num5][num9] = DataBlock(array2[num9], array[num5 + 1] - array2[num9])
            
            num5 += 1
        
        # 进度条和列表框更新逻辑占位
        progress_max = 408
        num13 = 0
        
        while num13 <= 407:
            num14 = self.subBlockCountsFIGANI[num13] - 1
            num15 = 0
            
            while num15 <= num14:
                # 格式化ID文本
                text = f"{num13:04d}-{num15:03d}"
                # ListBoxImages.Items.Add(f"ID:{text}")  # UI操作占位
                num15 += 1
            
            # 更新进度条（每30个块更新一次）
            if num13 % 30 == 0:
                pass  # 进度条更新占位
            
            num13 += 1
        
        # 完成进度
        # ProgressBar.Value = ProgressBar.Maximum  # UI操作占位

    def AnalysisANI(self):
        """分析ANI数据结构
        ANI文件有9个分段，每段包含动画数据
        每个段以"AFM - Animation File Manager..."开头，后面是"Empty Title."，然后是帧数据
        根据分析，30x63动画精灵在每个段的固定偏移位置（0xd0 = 208字节处）
        """
        # 读取9个主要分段的偏移量 (跳过文件头的6字节)
        segment_offsets = []
        for i in range(9):
            offset_bytes = self.fileDatas[6 + i*4:6 + (i+1)*4]
            offset = struct.unpack('<I', offset_bytes)[0]
            segment_offsets.append(offset)
        
        # 分析每个段
        for i in range(9):
            start_offset = segment_offsets[i]
            end_offset = segment_offsets[i+1] if i+1 < len(segment_offsets) else len(self.fileDatas)
            
            frame_idx = 0
            frames_found = 0
            
            # 检查固定位置是否有有效的30x63帧 (在段内偏移0xd0处)
            fixed_pos = start_offset + 0xd0  # 0xd0 = 208字节
            
            if fixed_pos + 6 <= len(self.fileDatas):
                length = struct.unpack('<H', self.fileDatas[fixed_pos:fixed_pos+2])[0]
                width = struct.unpack('<H', self.fileDatas[fixed_pos+2:fixed_pos+4])[0]
                height = struct.unpack('<H', self.fileDatas[fixed_pos+4:fixed_pos+6])[0]
                
                # 检查是否是30x63帧
                if width == 30 and height == 63 and length > 0 and fixed_pos + 6 + length <= end_offset:
                    # 创建数据块，包含帧头和数据
                    frame_size = 6 + length  # 帧头(6字节) + 数据
                    self.datablocksANI[i][frame_idx] = DataBlock(fixed_pos, frame_size)
                    frames_found += 1
                    frame_idx += 1
                    print(f"段{i}: 找到30x63动画精灵，位置: 0x{fixed_pos:06x}")
            
            # 同时也搜索其他可能的帧（在Empty Title之后的区域）
            segment_data = self.fileDatas[start_offset:end_offset]
            empty_title_pos = segment_data.find(b"Empty Title.")
            
            if empty_title_pos != -1:
                # 从Empty Title之后开始搜索其他帧（但避免重复检测30x63帧的位置）
                current_file_pos = start_offset + empty_title_pos + len(b"Empty Title.")
                
                while current_file_pos < end_offset - 6 and frame_idx < len(self.datablocksANI[i]):
                    # 跳过已知的30x63帧位置，避免重复
                    if abs(current_file_pos - (start_offset + 0xd0)) < 10:  # 避免在30x63附近重复搜索
                        current_file_pos += 2
                        continue
                        
                    if current_file_pos + 6 <= len(self.fileDatas):
                        length = struct.unpack('<H', self.fileDatas[current_file_pos:current_file_pos+2])[0]
                        width = struct.unpack('<H', self.fileDatas[current_file_pos+2:current_file_pos+4])[0]
                        height = struct.unpack('<H', self.fileDatas[current_file_pos+4:current_file_pos+6])[0]
                        
                        # 检查是否是合理的帧数据
                        if (10 <= width <= 320 and 10 <= height <= 240 and 
                            width * height <= length and  # 长度应至少等于像素数
                            length > 0 and current_file_pos + 6 + length <= end_offset):  # 确保数据不超出段范围
                            
                            # 创建数据块，包含帧头和数据
                            frame_size = 6 + length  # 帧头(6字节) + 数据
                            self.datablocksANI[i][frame_idx] = DataBlock(current_file_pos, frame_size)
                            frames_found += 1
                            frame_idx += 1
                            print(f"段{i}: 找到{width}x{height}动画精灵，位置: 0x{current_file_pos:06x}")
                            break  # 暂时每个段最多找2个帧，避免解析错误
                            
                    current_file_pos += 2
            
            # 设置找到的帧数量
            self.subBlockCountsANI[i] = frames_found

