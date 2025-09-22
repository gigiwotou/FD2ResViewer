import os
import struct
import io
from PIL import Image
import sys
from typing import Any

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
        # 从数据块的起始位置读取宽度和高度
        # 修正：宽度和高度应该从startOffset和startOffset+2位置读取
        width = struct.unpack('<h', datablock[startOffset:startOffset+2])[0]
        height = struct.unpack('<h', datablock[startOffset+2:startOffset+4])[0]
        # 确保宽度和高度为正数
        if width <= 0 or height <= 0:
            # 如果直接读取的值不合理，尝试其他位置
            width = struct.unpack('<h', datablock[startOffset+9:startOffset+11])[0]
            height = struct.unpack('<h', datablock[startOffset+11:startOffset+13])[0]
        
        # 确保宽度和高度在合理范围内
        width = max(1, min(width, 1000))
        height = max(1, min(height, 1000))
        
        self.BMPimage = Image.new('RGB', (width, height))
        progress_max = length - 5
        num2 = startOffset + 4  # 从数据开始位置读取（修正为startOffset + 4）
        num3 = startOffset + length - 1
        num4 = num2
        num7 = 0
        num8 = 0
        num9 = 0
        b = 0
        num10 = 0
        num11 = 0
        
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
                    if b >= 192:
                        num7 = b - 192 + 1
                    if 128 <= b < 192:  # 修复条件判断逻辑，使用if而非elif
                        num8 = b - 128 + 1
                    if 64 <= b < 128:   # 修复条件判断逻辑，使用if而非elif
                        num9 = b - 64
                        num8 = 1
                        flag = True
                    if b <= 63:         # 修复条件判断逻辑，使用if而非elif
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
                        num7 = 1  # 重置num7为1
                        if 0 <= num10 < width and 0 <= num11 < height:
                            self.BMPimage.putpixel((num10, num11), colorpanel.thisColor(index))
                    num10 += num7
                    if num10 >= width:
                        num10 = 0
                        num11 += 1
                        flag = False
                    num13 += 1
                num8 -= 1
                num4 += 1  # 只在else分支中增加num4
            num4 += 1  # 在所有情况下都增加num4
        
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
            # 假设MyModule.shaps[num8]是一个PIL Image对象
            # self.BMPimage.paste(MyModule.shaps[num8], (num9 * 24, num10 * 24))
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
        self.datablocksICON = [None] * 1681
        self.dataBlocksBG = [None] * 57
        self.dataBlocksDATO = [[None for _ in range(4)] for _ in range(137)]
        self.datablocksFDFIELD = [None] * 100
        self.datablocksOTHER = [None] * 104
        self.datablocksOTHERSubs = None
        self.dataBlocksFDSHAP = [[None for _ in range(401)] for _ in range(67)]
        self.FDSHAPsubBlockCount = [0] * 67
        self.datablocksTXT = [[None for _ in range(701)] for _ in range(35)]
        self.TXTsubBlockCount = [0] * 35
        self.dataBlocksFIGANI = [[None for _ in range(41)] for _ in range(409)]
        self.FIGANIsubBlockCount = [0] * 409
        self.shapsDone = False
        
        # 文件数据变量
        self.bgFileDatas = None
        self.datoFileDatas = None
        self.fieldFileDatas = None
        self.otherFileDatas = None
        self.shapFileDatas = None
        self.txtFileDatas = None
        self.figaniFileDatas = None
        self.fd2FileDatas = None
        
        os.makedirs(self.output_dir, exist_ok=True)
   

    def AnalysisOTHER(self):
        array = [0] * 104
        num = 6
        # 确保self.fileDatas不为None
        if self.fileDatas is None:
            return
        while num <= 418:
            index = int((num - 6) / 4)
            # 确保索引在有效范围内
            if index < len(array) and num + 4 <= len(self.fileDatas):
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

    def AnalysisFDSHAP(self):
        array = [0] * 67
        num = 6
        while num <= 270:
            index = int((num - 6) / 4)
            array[index] = struct.unpack('<I', self.shapFileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            self.FDSHAPsubBlockCount[num5] = struct.unpack('<h', self.shapFileDatas[array[num5]+4 : array[num5]+6])[0]
            num8 = self.FDSHAPsubBlockCount[num5] - 1
            array2 = [0] * (num8 + 1)
            num9 = 0
            while num9 <= num8:
                array2[num9] = array[num5] + struct.unpack('<I', self.shapFileDatas[array[num5]+6+num9*4 : array[num5]+10+num9*4])[0]
                num9 += 1

            num11 = self.FDSHAPsubBlockCount[num5] - 2
            num9 = 0
            while num9 <= num11:
                self.dataBlocksFDSHAP[num5][num9] = DataBlock(array2[num9], array2[num9+1] - array2[num9])
                num9 += 1
            self.dataBlocksFDSHAP[num5][num9] = DataBlock(array2[num9], array[num5+1] - array2[num9])
            num5 += 2

        # 进度条和列表框更新逻辑占位
        progress_max = 66
        num13 = 0
        while num13 <= 66:
            num14 = self.FDSHAPsubBlockCount[num13] - 1
            num15 = 0
            while num15 <= num14:
                text = f"ID:{num13:03d}-{num15:04d}"
                # ListBoxImages.Items.Add(text)  # UI操作占位
                num15 += 1
            if num13 % 10 == 0:
                pass  # 进度条更新占位
            num13 += 1
        self.shapsDone = True

    # def AnalysisFIGANI(self):
    #     if self.fileDatas is None:
    #         return
            
    #     array = [0] * 409
    #     num = 6
    #     # 修复主块偏移量读取逻辑，确保与C#版本一致
    #     while num <= 1638:
    #         index = int(round((num - 6) / 4.0))
    #         if index < len(array) and num + 4 <= len(self.fileDatas):
    #             array[index] = struct.unpack('<I', self.fileDatas[num:num+4])[0]
    #         num += 4

    #     array2 = [0] * 41
    #     num4 = len(array) - 2
    #     num5 = 0
    #     while num5 <= num4:
    #         # 读取子块计数
    #         if array[num5] < len(self.fileDatas) and array[num5] > 0:
    #             self.FIGANIsubBlockCount[num5] = self.fileDatas[array[num5]]
    #         else:
    #             self.FIGANIsubBlockCount[num5] = 0
            
    #         # 读取子块偏移量 (使用正确的偏移量计算方法)
    #         num8 = self.FIGANIsubBlockCount[num5] - 1
    #         num9 = 0
    #         while num9 <= num8 and self.FIGANIsubBlockCount[num5] > 0:
    #             if array[num5] + 8 + num9 * 4 + 4 <= len(self.fileDatas):
    #                 # 读取原始偏移量值
    #                 raw_bytes = self.fileDatas[array[num5] + 8 + num9 * 4:array[num5] + 12 + num9 * 4]
    #                 # 使用字节1-2组合作为相对偏移量
    #                 relative_offset = raw_bytes[1] + (raw_bytes[2] << 8)
    #                 # 计算实际偏移量
    #                 array2[num9] = array[num5] + relative_offset
    #             else:
    #                 array2[num9] = 0
    #             num9 += 1

    #         # 对偏移量进行排序，确保按正确顺序处理
    #         valid_offsets = [offset for offset in array2[:self.FIGANIsubBlockCount[num5]] if offset > 0]
    #         valid_offsets.sort()
            
    #         # 重新分配排序后的偏移量
    #         for i in range(len(valid_offsets)):
    #             if i < len(array2):
    #                 array2[i] = valid_offsets[i]
    #         # 填充剩余位置为0
    #         for i in range(len(valid_offsets), self.FIGANIsubBlockCount[num5]):
    #             if i < len(array2):
    #                 array2[i] = 0

    #         # 创建数据块
    #         num11 = self.FIGANIsubBlockCount[num5] - 2
    #         num9 = 0
    #         while num9 <= num11 and self.FIGANIsubBlockCount[num5] > 0:
    #             if num9 < len(array2) and num9 + 1 < len(array2):
    #                 length = array2[num9 + 1] - array2[num9]
    #                 if length > 0 and array2[num9] < len(self.fileDatas):
    #                     # 确保数据结构已初始化
    #                     if self.dataBlocksFIGANI[num5] is None:
    #                         self.dataBlocksFIGANI[num5] = [None] * 41
    #                     if num9 < len(self.dataBlocksFIGANI[num5]):
    #                         self.dataBlocksFIGANI[num5][num9] = DataBlock(array2[num9], length)
    #             num9 += 1

    #         # 处理最后一个数据块
    #         if self.FIGANIsubBlockCount[num5] > 0:
    #             # 确保数据结构已初始化
    #             if self.dataBlocksFIGANI[num5] is None:
    #                 self.dataBlocksFIGANI[num5] = [None] * 41
                    
    #             if num9 < self.FIGANIsubBlockCount[num5]:
    #                 if (num5 + 1) < len(array) and array[num5+1] < len(self.fileDatas) and array[num5+1] > 0:
    #                     # 使用下一个主块的起始位置计算长度
    #                     length = array[num5+1] - array2[num9]
    #                 else:
    #                     # 对于最后一个主块，使用文件长度计算
    #                     length = len(self.fileDatas) - array2[num9]
    #                 if length > 0 and array2[num9] < len(self.fileDatas):
    #                     if num9 < len(self.dataBlocksFIGANI[num5]):
    #                         self.dataBlocksFIGANI[num5][num9] = DataBlock(array2[num9], length)
            
    #         num5 += 1
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
    
    def AnalysisOtherSubs(self, subIndex):
        if subIndex in (1, 14):
            num43 = self.datablocksOTHER[subIndex].startOffset + 6
            sWidth = struct.unpack('<h', self.fileDatas[self.datablocksOTHER[subIndex].startOffset : self.datablocksOTHER[subIndex].startOffset+2])[0]
            sHeight = struct.unpack('<h', self.fileDatas[self.datablocksOTHER[subIndex].startOffset+2 : self.datablocksOTHER[subIndex].startOffset+4])[0]
            num44 = struct.unpack('<h', self.fileDatas[self.datablocksOTHER[subIndex].startOffset+4 : self.datablocksOTHER[subIndex].startOffset+6])[0]
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
                self.datablocksOTHERSubs[num46] = DataBlock(array5[num46], array5[num46+1] - array5[num46])
                num46 += 1
            self.datablocksOTHERSubs[num46] = DataBlock(array5[num46], self.datablocksOTHER[subIndex].length - array5[num46])

            # 进度条和列表框更新逻辑占位
            num51 = 0
            while num51 < num44:
                text5 = f"ID:{num51:09d}"
                # ListBoxSecond.Items.Add(text5)
                if num51 % (num44 // 10) == 0:
                    pass  # 进度条更新
                num51 += 1

        elif subIndex == 2:
            startOffset2 = self.datablocksOTHER[subIndex].startOffset
            num34 = int(struct.unpack('<I', self.fileDatas[startOffset2:startOffset2+4])[0] / 4)
            array4 = [0] * num34
            self.datablocksOTHERSubs = [None] * num34
            num36 = 0
            while num36 < num34:
                array4[num36] = struct.unpack('<I', self.fileDatas[startOffset2 + num36*4 : startOffset2 + (num36+1)*4])[0]
                num36 += 1

            num38 = num34 - 2
            num36 = 0
            bmp_maker = BMPMaker()
            colorpanel = ColorPanel(1)
            while num36 <= num38:
                self.datablocksOTHERSubs[num36] = DataBlock(array4[num36], array4[num36+1] - array4[num36])
                # # 解析宽度和高度
                # data_offset = self.datablocksOTHER[subIndex].startOffset + self.datablocksOTHERSubs[num36].startOffset
                # sWidth = struct.unpack('<h', self.fileDatas[data_offset:data_offset+2])[0]
                # sHeight = struct.unpack('<h', self.fileDatas[data_offset+2:data_offset+4])[0]
                # # 生成图像                
                # image = bmp_maker.makeBMP(
                #     sWidth, sHeight,
                #     self.fileDatas,
                #     data_offset + 4,
                #     self.datablocksOTHERSubs[num36].length - 4,
                #     colorpanel
                # )
                # image_path = os.path.join(self.output_dir, f'other_{subIndex}_{num36}.png')
                # image.save(image_path)
                
                num36 += 1
            self.datablocksOTHERSubs[num36] = DataBlock(array4[num36], self.datablocksOTHER[subIndex].length - array4[num36])

            # 进度条和列表框更新逻辑占位
            num41 = 0
            while num41 < num34:
                text4 = f"ID:{num41:09d}"
                # ListBoxSecond.Items.Add(text4)
                if num41 % (num34 // 10) == 0:
                    pass  # 进度条更新
                num41 += 1

        elif subIndex == 4:
            obj = self.datablocksOTHER[subIndex].length / 32
            array2 = [i*32 for i in range(int(obj))]
            self.datablocksOTHERSubs = [None] * len(array2)
            num17 = 0
            while num17 < len(array2)-1:
                self.datablocksOTHERSubs[num17] = DataBlock(array2[num17], array2[num17+1] - array2[num17])
                num17 += 1
            self.datablocksOTHERSubs[num17] = DataBlock(array2[num17], self.datablocksOTHER[subIndex].length - array2[num17])

            # 进度条和列表框更新逻辑占位
            num22 = 0
            while num22 < len(array2):
                text2 = f"ID:{num22:09d}"
                # ListBoxSecond.Items.Add(text2)
                if num22 % (len(array2) // 10) == 0:
                    pass  # 进度条更新
                num22 += 1

        elif subIndex in (5, 6, 9, 96):
            num3 = self.datablocksOTHER[subIndex].startOffset + 4
            # print(f"解析数据段 subIndex：{subIndex}. 起始地址: 0x{self.datablocksOTHER[subIndex].startOffset:X}")
            num4 = struct.unpack('<h', self.fileDatas[num3:num3+2])[0]
            # print(f"subIndex: {subIndex}, num4: {num4}")
            array = [0] * num4
            self.datablocksOTHERSubs = [None] * num4
            num6 = 0
            while num6 < num4:
                array[num6] = struct.unpack('<I', self.fileDatas[num3+2 + num6*4 : num3+6 + num6*4])[0]
                # print(f"subIndex: {subIndex}, num6: {num6}, array[num6]: {array[num6]}")
                # print(f"subIndex: {subIndex}, num6: {num6}, array[num6]: 0x{self.datablocksOTHER[subIndex].startOffset + array[num6]:X}")
                num6 += 1

            num9 = num4 - 2
            num6 = 0
            while num6 <= num9:
                self.datablocksOTHERSubs[num6] = DataBlock(array[num6], array[num6+1] - array[num6])
                num6 += 1
            self.datablocksOTHERSubs[num6] = DataBlock(array[num6], self.datablocksOTHER[subIndex].length - array[num6])

            # 进度条和列表框更新逻辑占位
            num12 = 0
            while num12 < num4:
                text = f"ID:{num12:09d}"
                # ListBoxSecond.Items.Add(text)
                if num12 % (num4 // 10) == 0:
                    pass  # 进度条更新
                num12 += 1

        elif subIndex in (7, 12, 13, 63):
            num24 = self.datablocksOTHER[subIndex].startOffset + 6
            short_value = struct.unpack('<h', self.fileDatas[num24:num24+2])[0]
            num25 = int(round((short_value - 6) / 4.0 - 1.0))
            num25 = max(0, num25)
            array3 = [0] * num25  # 数组长度匹配C#的num25
            self.datablocksOTHERSubs = [None] * num25
            num26 = num25 - 1  # 循环上限保持num25-1，与C#一致
            num27 = 0
            while num27 <= num26:
                array3[num27] = struct.unpack('<I', self.fileDatas[num24 + num27*4 : num24 + (num27+1)*4])[0]
                num27 += 1

            num29 = len(array3) - 2  # 修正为Python的len()语法
            num27 = 0
            while num27 <= num29:
                self.datablocksOTHERSubs[num27] = DataBlock(array3[num27], array3[num27+1] - array3[num27])
                num27 += 1
            self.datablocksOTHERSubs[num27] = DataBlock(array3[num27], self.datablocksOTHER[subIndex].length - array3[num27])

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
            # 调用BMPMaker生成面部图像
            bmp_maker = BMPMaker()
            sWidth = struct.unpack('<h', self.fileDatas[self.datablocksOTHER[subIndex].startOffset : self.datablocksOTHER[subIndex].startOffset+2])[0]
            sHeight = struct.unpack('<h', self.fileDatas[self.datablocksOTHER[subIndex].startOffset+2 : self.datablocksOTHER[subIndex].startOffset+4])[0]
            image = bmp_maker.makeFaceBMP(
                self.fileDatas,
                self.datablocksOTHER[subIndex].startOffset,
                self.datablocksOTHER[subIndex].length,
                ColorPanel(1)  # 使用灰色调色板
            )
            image_path = os.path.join(self.output_dir, f'face_{subIndex}.png')
            image.save(image_path)

        elif subIndex in (11, 16, 17, 46, 47, 56, 59, 60, 61, 62, 69, 70, 71, 72, 73, 74, 75, 97, 98, 100):
            sWidth = struct.unpack('<h', self.fileDatas[self.datablocksOTHER[subIndex].startOffset : self.datablocksOTHER[subIndex].startOffset+2])[0]
            sHeight = struct.unpack('<h', self.fileDatas[self.datablocksOTHER[subIndex].startOffset+2 : self.datablocksOTHER[subIndex].startOffset+4])[0]
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
                self.datablocksOTHER[subIndex].startOffset + 4,
                self.datablocksOTHER[subIndex].length - 4,
                colorpanel
            )
            image_path = os.path.join(self.output_dir, f'shap_{subIndex}.png')
            image.save(image_path)

        elif subIndex == 55:
            sWidth = struct.unpack('<h', self.fileDatas[self.datablocksOTHER[subIndex].startOffset : self.datablocksOTHER[subIndex].startOffset+2])[0]
            sHeight = struct.unpack('<h', self.fileDatas[self.datablocksOTHER[subIndex].startOffset+2 : self.datablocksOTHER[subIndex].startOffset+4])[0]
            bmp_maker = BMPMaker()
            image = bmp_maker.makeBMP(
                sWidth, sHeight,
                self.fileDatas,
                self.datablocksOTHER[subIndex].startOffset + 4,
                self.datablocksOTHER[subIndex].length - 4,
                ColorPanel(1)
            )
            image_path = os.path.join(self.output_dir, f'other_{subIndex}.png')
            image.save(image_path)
        elif subIndex == 79:
            num3 = self.datablocksOTHER[subIndex].startOffset + 2
            print(f"解析数据段 subIndex：{subIndex}. 起始地址: 0x{self.datablocksOTHER[subIndex].startOffset:X}")
            # 从num3 + 4位置开始读取num4
            num4 = struct.unpack('<h', self.fileDatas[num3:num3+2])[0]
            print(f"subIndex: {subIndex}, num4: {num4}")

            array = [0] * num4
            self.datablocksOTHERSubs = [None] * num4
            num6 = 0
            while num6 < num4:
                array[num6] = struct.unpack('<I', self.fileDatas[num3+6 + num6*4 : num3+10 + num6*4])[0]
                print(f"subIndex: {subIndex}, num6: {num6}, array[num6]: 0x{self.datablocksOTHER[subIndex].startOffset + array[num6]:X}")
                num6 += 1

            num9 = num4 - 2
            num6 = 0
            while num6 <= num9:
                self.datablocksOTHERSubs[num6] = DataBlock(array[num6], array[num6+1] - array[num6])
                print(f"subIndex: {subIndex}, num6: {num6}, array[num6]: 0x{array[num6]:X}, length: {self.datablocksOTHERSubs[num6].length}")
                num6 += 1
        
            self.datablocksOTHERSubs[num6] = DataBlock(array[num6], self.datablocksOTHER[subIndex].length - array[num6])
          
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
                    start_offset = self.datablocksOTHER[num].startOffset + self.datablocksOTHERSubs[num2].startOffset
                    if num == 96:
                        sWidth = 24
                        sHeight = 24
                    else:
                        # sWidth = struct.unpack('<h', self.fileDatas[start_offset:start_offset+2])[0]
                        # sHeight = struct.unpack('<h', self.fileDatas[start_offset+2:start_offset+4])[0]
                        sWidth = struct.unpack('<h', self.fileDatas[self.datablocksOTHER[num].startOffset : self.datablocksOTHER[num].startOffset+2])[0]
                        sHeight = struct.unpack('<h', self.fileDatas[self.datablocksOTHER[num].startOffset+2 : self.datablocksOTHER[num].startOffset+4])[0]
                    # print(f"subIndex: {subIndex}, num2: {num2:03d}, start_offset: {start_offset}, sWidth: {sWidth}, sHeight: {sHeight}")

                    # 生成形状图像                
                    image = self.bmp_maker.makeShapBMP(
                        sWidth, sHeight,
                        self.fileDatas,
                        start_offset,
                        self.datablocksOTHERSubs[num2].length,
                        ColorPanel(1)
                    )
                    image_path = os.path.join(self.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                    image.save(image_path)
 
                if num3 == 2:
                    start_offset = self.datablocksOTHER[num].startOffset + self.datablocksOTHERSubs[num2].startOffset
                    
                    sWidth = struct.unpack('<h', self.fileDatas[start_offset:start_offset+2])[0]
                    sHeight = struct.unpack('<h', self.fileDatas[start_offset+2:start_offset+4])[0]

                    data_offset = start_offset + 4
                    
                    # 生成其他类型图像                      
                    image = self.bmp_maker.makeBMP(
                        sWidth, sHeight,
                        self.fileDatas,
                        data_offset,
                        self.datablocksOTHERSubs[num2].length - 4,
                        ColorPanel(1)
                    )
                    image_path = os.path.join(self.output_dir, f'other_{subIndex}_{num2:03d}.png')
                    image.save(image_path)
                    

                if num3 == 4:
                    data_offset = self.datablocksOTHER[num3].startOffset + self.datablocksOTHERSubs[num2].startOffset
                    
                    # 生成字体图像                
                    image = self.bmp_maker.makeFontBMP(
                        self.fileDatas,
                        data_offset,
                        self.datablocksOTHERSubs[num2].length
                    )
                    image_path = os.path.join(self.output_dir, f'font_{subIndex}_{num2:03d}.png')
                    image.save(image_path)
                   
                if num3 == 5:
                    start_offset = self.datablocksOTHER[num3].startOffset + self.datablocksOTHERSubs[num2].startOffset

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
                            self.datablocksOTHERSubs[num2].length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'other_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 < 23:
                        data_offset = start_offset
                        image = self.bmp_maker.makeFaceBMP(
                            self.fileDatas,
                            data_offset,
                            self.datablocksOTHERSubs[num2].length,
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
                            self.datablocksOTHERSubs[num2].length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'other_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 < 53:
                        image = self.bmp_maker.makeShapBMP(
                            sWidth, sHeight,
                            self.fileDatas,
                            start_offset + 4,
                            self.datablocksOTHERSubs[num2].length - 4,
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
                            self.datablocksOTHERSubs[num2].length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'other_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 != 59:
                        if num2 < 119 and num2 != 93:
                            data_offset = start_offset
                            sWidth = struct.unpack('<h', self.fileDatas[data_offset:data_offset+2])[0]
                            sHeight = struct.unpack('<h', self.fileDatas[data_offset+2:data_offset+4])[0]
                            # 生成面部图像                
                            image = self.bmp_maker.makeFaceBMP(
                                self.fileDatas,
                                data_offset,
                                self.datablocksOTHERSubs[num2].length,
                                ColorPanel(1)
                            )
                            image_path = os.path.join(self.output_dir, f'face_{subIndex}_{num2:03d}.png')
                            image.save(image_path)
                        else:
                            image = self.bmp_maker.makeShapBMP(
                            sWidth, sHeight,
                            self.fileDatas,
                            start_offset + 4,
                            self.datablocksOTHERSubs[num2].length - 4,
                            ColorPanel(1)
                            )
                            image_path = os.path.join(self.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                            image.save(image_path)

                if num3 == 7:
                    start_offset = self.datablocksOTHER[num].startOffset + self.datablocksOTHERSubs[num2].startOffset
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
                        self.datablocksOTHERSubs[num2].length - 4,
                        color_panel
                    )
                    image_path = os.path.join(self.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                    image.save(image_path)

                if num3 in (6, 9):
                    start_offset = self.datablocksOTHER[num3].startOffset + self.datablocksOTHERSubs[num2].startOffset
                    sWidth = struct.unpack('<h', self.fileDatas[start_offset:start_offset+2])[0]
                    sHeight = struct.unpack('<h', self.fileDatas[start_offset+2:start_offset+4])[0]
                    if num2 != 125:
                        data_offset = start_offset
                    sWidth = struct.unpack('<h', self.fileDatas[data_offset:data_offset+2])[0]
                    sHeight = struct.unpack('<h', self.fileDatas[data_offset+2:data_offset+4])[0]
                
                    # 生成面部图像                
                    image = self.bmp_maker.makeFaceBMP(
                        self.fileDatas,
                        data_offset,
                        self.datablocksOTHERSubs[num2].length,
                        ColorPanel(1)
                    )
                    image_path = os.path.join(self.output_dir, f'face_{subIndex}_{num2:03d}.png')
                    image.save(image_path)
                   

                if num3 in (12, 63):
                    start_offset = self.datablocksOTHER[num3].startOffset + self.datablocksOTHERSubs[num2].startOffset
                    sWidth = struct.unpack('<h', self.fileDatas[start_offset:start_offset+2])[0]
                    sHeight = struct.unpack('<h', self.fileDatas[start_offset+2:start_offset+4])[0]
                    
                    if num2 == 0 or (num2 >= 23 and num2 <= 29):
                        data_offset = start_offset + 4
                        # 生成形状图像                      
                        image = self.bmp_maker.makeShapBMP(
                            sWidth, sHeight,
                            self.fileDatas,
                            data_offset,
                            self.datablocksOTHERSubs[num2].length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 == 1 or num2 == 2 or (num2 >= 11 and num2 < 22):
                        data_offset = start_offset
                        sWidth = struct.unpack('<h', self.fileDatas[data_offset:data_offset+2])[0]
                        sHeight = struct.unpack('<h', self.fileDatas[data_offset+2:data_offset+4])[0]
                        # 生成面部图像                    
                        image = self.bmp_maker.makeFaceBMP(
                            self.fileDatas,
                            data_offset,
                            self.datablocksOTHERSubs[num2].length,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'face_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 != 22:
                        data_offset = start_offset + 4
                        # 生成其他类型图像                    
                        image = self.bmp_maker.makeBMP(
                            sWidth, sHeight,
                            self.fileDatas,
                            data_offset,
                            self.datablocksOTHERSubs[num2].length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'other_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    

                if num3 == 13:
                    start_offset = self.datablocksOTHER[num3].startOffset + self.datablocksOTHERSubs[num2].startOffset
                    sWidth = struct.unpack('<h', self.fileDatas[start_offset:start_offset+2])[0]
                    sHeight = struct.unpack('<h', self.fileDatas[start_offset+2:start_offset+4])[0]
                    
                    if num2 == 0:
                        data_offset = start_offset + 4
                        # 生成形状图像                      
                        image = self.bmp_maker.makeShapBMP(
                            sWidth, sHeight,
                            self.fileDatas,
                            data_offset,
                            self.datablocksOTHERSubs[num2].length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 == 1 or num2 == 2 or num2 >= 11:
                        data_offset = start_offset
                        sWidth = struct.unpack('<h', self.fileDatas[data_offset:data_offset+2])[0]
                        sHeight = struct.unpack('<h', self.fileDatas[data_offset+2:data_offset+4])[0]
                        # 生成面部图像                    
                        image = self.bmp_maker.makeFaceBMP(
                            self.fileDatas,
                            data_offset,
                            self.datablocksOTHERSubs[num2].length,
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
                            self.datablocksOTHERSubs[num2].length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'other_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    

                if num3 == 14:
                    start_offset = self.datablocksOTHER[num].startOffset + self.datablocksOTHERSubs[num2].startOffset
                    sWidth = struct.unpack('<h', self.fileDatas[start_offset:start_offset+2])[0]
                    sHeight = struct.unpack('<h', self.fileDatas[start_offset+2:start_offset+4])[0]
                    
                    if num2 == 0 or num2 >= 23:
                        data_offset = start_offset + 4
                        # 生成形状图像                    
                        image = self.bmp_maker.makeShapBMP(
                            sWidth, sHeight,
                            self.fileDatas,
                            data_offset,
                            self.datablocksOTHERSubs[num2].length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 == 1 or num2 == 2 or (num2 >= 11 and num2 < 23):
                        data_offset = start_offset
                        sWidth = struct.unpack('<h', self.fileDatas[data_offset:data_offset+2])[0]
                        sHeight = struct.unpack('<h', self.fileDatas[data_offset+2:data_offset+4])[0]
                        # 生成面部图像                    
                        image = self.bmp_maker.makeFaceBMP(
                            self.fileDatas,
                            data_offset,
                            self.datablocksOTHERSubs[num2].length,
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
                            self.datablocksOTHERSubs[num2].length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'other_{subIndex}_{num2:03d}.png')
                        image.save(image_path)

                if num3 == 79:
                    start_offset = self.datablocksOTHER[num3].startOffset + self.datablocksOTHERSubs[num2].startOffset

                    sWidth = struct.unpack('<h', self.fileDatas[start_offset:start_offset+2])[0]
                    sHeight = struct.unpack('<h', self.fileDatas[start_offset+2:start_offset+4])[0]

                    # print(f"subIndex: {subIndex}, num2: {num2:03d}, start_offset: {start_offset}, sWidth: {sWidth}, sHeight: {sHeight}, data_offset: {start_offset}")
                    
                    data_offset = start_offset + 4
                    # 生成其他类型图像                    
                    image = self.bmp_maker.makeBMP(
                        sWidth, sHeight,
                        self.fileDatas,
                        data_offset,
                        self.datablocksOTHERSubs[num2].length - 4,
                        ColorPanel(1)
                    )
                    image_path = os.path.join(self.output_dir, f'other_{subIndex}_{num2:03d}.png')
                    image.save(image_path)

    def AnalysisTXT(self):
        """分析FDTXT数据结构"""
        array = [0] * 35
        num = 6
        while num <= 142:
            index = int((num - 6) / 4)
            array[index] = struct.unpack('<I', self.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            self.TXTsubBlockCount[num5] = int(struct.unpack('<h', self.fileDatas[array[num5]:array[num5]+2])[0] / 2)
            num8 = self.TXTsubBlockCount[num5] - 1
            array2 = [0] * (num8 + 1)
            num9 = 0
            while num9 <= num8:
                array2[num9] = array[num5] + struct.unpack('<h', self.fileDatas[array[num5] + num9*2 : array[num5] + (num9+1)*2])[0]
                num9 += 1

            num11 = self.TXTsubBlockCount[num5] - 2
            num9 = 0
            while num9 <= num11:
                # 确保不会越界
                if num5 < len(self.datablocksTXT) and num9 < len(self.datablocksTXT[num5]):
                    self.datablocksTXT[num5][num9] = DataBlock(array2[num9], array2[num9+1] - array2[num9])
                num9 += 1
            # 处理最后一个数据块
            if num5 < len(self.datablocksTXT) and num9 < len(self.datablocksTXT[num5]):
                self.datablocksTXT[num5][num9] = DataBlock(array2[num9], array[num5+1] - array2[num9])
            num5 += 1

        # 进度条和列表框更新逻辑占位
        progress_max = 34
        num13 = 0
        while num13 <= 33:
            if num13 < len(self.TXTsubBlockCount):
                num14 = self.TXTsubBlockCount[num13] - 1
                num15 = 0
                while num15 <= num14:
                    text = f"ID:{num13:04d}-{num15:04d}"
                    # ListBoxImages.Items.Add(text)  # UI操作占位
                    num15 += 1
            if num13 % 30 == 0:
                pass  # 进度条更新占位
            num13 += 1

    def AnalysisDATO(self):
        """分析DATO数据结构"""
        array = [0] * 137
        num = 6
        while num <= 550:
            index = int((num - 6) / 4)
            array[index] = struct.unpack('<I', self.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            array2 = [0] * 4
            num8 = 0
            while num8 <= 3:
                array2[num8] = array[num5] + struct.unpack('<I', self.fileDatas[array[num5] + num8*4 : array[num5] + (num8+1)*4])[0]
                num8 += 1

            num8 = 0
            while num8 <= 2:
                # 确保不会越界
                if num5 < len(self.dataBlocksDATO) and num8 < len(self.dataBlocksDATO[num5]):
                    self.dataBlocksDATO[num5][num8] = DataBlock(array2[num8], array2[num8+1] - array2[num8])
                num8 += 1
            # 处理最后一个数据块
            if num5 < len(self.dataBlocksDATO) and num8 < len(self.dataBlocksDATO[num5]):
                self.dataBlocksDATO[num5][num8] = DataBlock(array2[num8], array[num5+1] - array2[num8])
            num5 += 1

    def AnalysisBG(self):
        """分析BG数据结构"""
        array = [0] * 57
        num = 6
        while num <= 230:
            index = int((num - 6) / 4)
            array[index] = struct.unpack('<I', self.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            # 确保不会越界
            if num5 < len(self.dataBlocksBG):
                self.dataBlocksBG[num5] = DataBlock(array[num5], array[num5 + 1] - array[num5])
            num5 += 1
        # 处理最后一个数据块
        if num5 < len(self.dataBlocksBG):
            self.dataBlocksBG[num5] = DataBlock(array[num5], len(self.fileDatas) - array[num5])

    def AnalysisTAI(self):
        """分析TAI数据结构（专用）"""
        array = [0] * 57
        num = 6
        while num <= 230:
            index = int((num - 6) / 4)
            array[index] = struct.unpack('<I', self.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            # 确保不会越界
            if num5 < len(self.dataBlocksBG):
                self.dataBlocksBG[num5] = DataBlock(array[num5], array[num5 + 1] - array[num5])
            num5 += 1
        # 处理最后一个数据块
        if num5 < len(self.dataBlocksBG):
            self.dataBlocksBG[num5] = DataBlock(array[num5], len(self.fileDatas) - array[num5])

    def AnalysisFIGANI(self):
        """分析FIGANI数据结构"""
        array = [0] * 409
        num = 6
        while num <= 1638 and num < len(self.fileDatas) - 3:
            index = int((num - 6) / 4)
            # 确保索引在有效范围内
            if index < len(array) and num + 4 <= len(self.fileDatas):
                array[index] = struct.unpack('<I', self.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4 and num5 < len(self.FIGANIsubBlockCount):
            # 确保数组索引在有效范围内
            if num5 < len(array) and array[num5] < len(self.fileDatas) and array[num5] > 0:
                self.FIGANIsubBlockCount[num5] = self.fileDatas[array[num5]]
            else:
                self.FIGANIsubBlockCount[num5] = 0
            
            if self.FIGANIsubBlockCount[num5] > 0:
                num8 = self.FIGANIsubBlockCount[num5] - 1
                # 确保数组大小合理
                if num8 >= 0 and num8 < 100:  # 设置合理的上限
                    array2 = [0] * (num8 + 1)
                    num9 = 0
                    while num9 <= num8:
                        start_pos = array[num5] + 1 + num9*4  # 从主分类起始位置+1（跳过子帧数量字节）开始
                        end_pos = array[num5] + 1 + (num9+1)*4
                        # 确保读取位置在文件范围内
                        if start_pos + 4 <= len(self.fileDatas) and end_pos <= len(self.fileDatas):
                            # 读取相对偏移量并计算绝对位置
                            relative_offset = struct.unpack('<I', self.fileDatas[start_pos:start_pos+4])[0]
                            array2[num9] = array[num5] + relative_offset
                        else:
                            array2[num9] = array[num5] + 1 + num9*4  # 默认值
                        num9 += 1

                    num11 = self.FIGANIsubBlockCount[num5] - 2
                    num9 = 0
                    while num9 <= num11 and num5 < len(self.dataBlocksFIGANI) and num9 < len(self.dataBlocksFIGANI[num5]):
                        # 确保不会越界
                        if (num9 + 1) < len(array2):
                            length = array2[num9+1] - array2[num9]
                            if length > 0 and array2[num9] < len(self.fileDatas):
                                self.dataBlocksFIGANI[num5][num9] = DataBlock(array2[num9], length)
                        num9 += 1
                    
                    # 处理最后一个数据块
                    if num9 < len(self.dataBlocksFIGANI[num5]) and num9 > 0:
                        if (num5 + 1) < len(array) and array[num5+1] < len(self.fileDatas) and array[num5+1] > 0:
                            # 使用下一个主块的起始位置计算长度
                            length = array[num5+1] - array2[num9]
                        else:
                            # 对于最后一个主块，使用文件长度计算
                            length = len(self.fileDatas) - array2[num9]
                        if length > 0 and array2[num9] < len(self.fileDatas):
                            self.dataBlocksFIGANI[num5][num9] = DataBlock(array2[num9], length)
                    elif num9 < len(self.dataBlocksFIGANI[num5]) and num9 == 0:
                        # 处理只有一个子帧的情况
                        if (num5 + 1) < len(array) and array[num5+1] < len(self.fileDatas) and array[num5+1] > 0:
                            # 使用下一个主块的起始位置计算长度
                            length = array[num5+1] - array2[num9]
                        else:
                            # 对于最后一个主块，使用文件长度计算
                            length = len(self.fileDatas) - array2[num9]
                        if length > 0 and array2[num9] < len(self.fileDatas):
                            self.dataBlocksFIGANI[num5][num9] = DataBlock(array2[num9], length)
            num5 += 1

        # 进度条和列表框更新逻辑占位
        progress_max = 408
        num13 = 0
        while num13 <= 407 and num13 < len(self.FIGANIsubBlockCount):
            if self.FIGANIsubBlockCount[num13] > 0:
                num14 = self.FIGANIsubBlockCount[num13] - 1
                num15 = 0
                while num15 <= num14 and num13 < len(self.dataBlocksFIGANI) and num15 < len(self.dataBlocksFIGANI[num13]):
                    text = f"ID:{num13:04d}-{num15:03d}"
                    # ListBoxImages.Items.Add(text)  # UI操作占位
                    num15 += 1
            if num13 % 30 == 0:
                pass  # 进度条更新占位
            num13 += 1

    
