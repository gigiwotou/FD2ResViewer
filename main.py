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
                # 注意：调色板数据可能是6位颜色值(0-63)，需要转换为8位(0-255)
                red = min(255, self.colorPanelData[i*3] * 4)
                green = min(255, self.colorPanelData[i*3 + 1] * 4)
                blue = min(255, self.colorPanelData[i*3 + 2] * 4)
                
                # 如果颜色值异常，使用灰度替代
                if red == green == blue and red in [4, 248]:
                    red = green = blue = i  # 使用索引作为灰度值
            else:
                # 默认灰度颜色
                red = green = blue = i
            self.colors[i] = Color(red, green, blue, 0)

    def _load_resource(self, filename):
        """加载资源文件并返回字节数据"""
        try:
            with open(filename, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            print(f"警告: 资源文件 {filename} 未找到")
            return None
    
    def thisColor(self, index):
        if 0 <= index < len(self.colors):
            return (self.colors[index].Red, self.colors[index].Green, self.colors[index].Blue)
        else:
            # 返回默认颜色，防止索引越界
            return (0, 0, 0)

class DataBlock:
    def __init__(self, start, length):
        self.startOffset = start
        self.length = length

class BMPMaker:
    def __init__(self):
        # 加载资源文件
        self.BMPHeader1Bit = self._load_resource('SingleBitBMPHeader')
        self.colorPanel_data = self._load_resource('colorPanel')
        self.colornew_data = self._load_resource('colornew')
        self.colornew2_data = self._load_resource('colornew2')
        self.BMPDatas1Bit = bytearray(64)
        self.tempFontBMP = bytearray(len(self.BMPHeader1Bit) + 64) if self.BMPHeader1Bit else bytearray(64)
        self.BMPimage = None

    def _load_resource(self, filename):
        """加载资源文件并返回字节数据"""
        try:
            with open(filename, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            print(f"警告: 资源文件 {filename} 未找到")
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
        num5 = 0
        num6 = 0
        # print(f"makeBMP: width={width}, height={height}, startOffset={startOffset}, length={length}")
        while num <= num2:
            if length > 10 and num % (length // 10) == 0:
                pass  # 需补充进度条更新逻辑
            
            index = datablock[num]
            self.BMPimage.putpixel((num5, num6), colorpanel.thisColor(index))
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
        num10 = 0
        num11 = 0
        
        while num4 <= num3:
            if num4 % 200 == 0:
                pass  # 需补充进度条更新逻辑
            
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
                b = datablock[num4]
                if b >= 192:
                    num7 = b - 192 + 1
                elif 128 <= b < 192:
                    num8 = b - 128 + 1
                elif 64 <= b < 128:
                    num9 = b - 64
                    num8 = 1
                    flag = True
                elif b <= 63:
                    num8 = 1
                    num9 = b
                
                num10 += num7
                if num10 >= width:
                    num10 = 0
                    num11 += 1
                    flag = False
            else:
                for _ in range(num9):
                    if 64 <= b < 128:
                        num10 += 1
                    index = datablock[num4]
                    self.BMPimage.putpixel((num10, num11), colorpanel.thisColor(index))
                    num10 += 1
                    if num10 >= width:
                        num10 = 0
                        num11 += 1
                        flag = False
                num8 -= 1
            num4 += 1
        
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

    def adCharactersToField(self, field, id):
        num = id * 3 + 2
        # 假设MyModule.dataFileDatas[3].datas是字节数据
        # num2 = struct.unpack('<h', MyModule.dataFileDatas[3].datas[MyModule.datablocksFDFIELD[num].startOffset:MyModule.datablocksFDFIELD[num].startOffset+2])[0]
        self.BMPimage = field.copy()
        # 需要补充Graphics绘制逻辑
        return self.BMPimage

    def makeFightBMP(self, datablock, startOffset, length, colorpanel):
        flag = False
        width = struct.unpack('<h', datablock[startOffset+9:startOffset+11])[0]
        height = struct.unpack('<h', datablock[startOffset+11:startOffset+13])[0]
        self.BMPimage = Image.new('RGB', (width, height))
        progress_max = length - 5
        num2 = startOffset + 13
        num3 = startOffset + length - 1
        num4 = num2
        num7 = 0
        num8 = 0
        num9 = 0
        num10 = 0
        num11 = 0
        
        while num4 <= num3:
            if num4 % 200 == 0:
                pass  # 需补充进度条更新逻辑
            
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
                b = datablock[num4]
                if b >= 192:
                    num7 = b - 192 + 1
                elif 128 <= b < 192:
                    num8 = b - 128 + 1
                elif 64 <= b < 128:
                    num9 = b - 64
                    num8 = 1
                    flag = True
                elif b <= 63:
                    num8 = 1
                    num9 = b
                
                num10 += num7
                if num10 >= width:
                    num10 = 0
                    num11 += 1
                    flag = False
            else:
                for _ in range(num9):
                    if 64 <= b < 128:
                        num10 += 1
                    index = datablock[num4]
                    self.BMPimage.putpixel((num10, num11), colorpanel.thisColor(index))
                    num10 += 1
                    if num10 >= width:
                        num10 = 0
                        num11 += 1
                        flag = False
                num8 -= 1
            num4 += 1
        
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
                b = datablock[num2]
                if b >= 192:
                    num5 = b - 192 + 1
                if 128 <= b < 192:
                    num6 = b - 128 + 1
                if 64 <= b < 128:
                    num7 = b - 64
                    num6 = 1
                    flag = True
                if b <= 63:
                    num6 = 1
                    num7 = b
                
                num8 += num5
                if num8 >= width:
                    num8 = 0
                    num9 += 1
                    flag = False
            else:
                for _ in range(num7 + 1):
                    if 64 <= b < 128:
                        num8 += 1
                    index = datablock[num2]
                    self.BMPimage.putpixel((num8, num9), colorpanel.thisColor(index))
                    num8 += 1
                    if num8 >= width:
                        num8 = 0
                        num9 += 1
                        flag = False
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
        while num <= 418:
            index = int((num - 6) / 4)
            array[index] = struct.unpack('<I', self.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            self.datablocksOTHER[num5] = DataBlock(array[num5], array[num5 + 1] - array[num5])
            num5 += 1
        self.datablocksOTHER[num5] = DataBlock(array[num5], len(self.fileDatas) - array[num5])

        # 进度条和列表框更新逻辑占位
        progress_max = 103
        num8 = 0
        # while num8 <= 102:
        #     text = f"ID:{num8:04d}"
        #     if num8 % 4 == 0:
        #         pass  # 进度条更新占位
        #     # 调用AnalysisOtherSubs处理子索引
        #     self.AnalysisOtherSubs(num8)
        #     num8 += 1

    def AnalysisFDFIELD(self):
        array = [0] * 100
        num = 6
        while num <= 402:
            index = int((num - 6) / 4)
            array[index] = struct.unpack('<I', self.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            self.datablocksFDFIELD[num5] = DataBlock(array[num5], array[num5 + 1] - array[num5])
            num5 += 1
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

    def AnalysisDATO(self):
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
                self.dataBlocksDATO[num5][num8] = DataBlock(array2[num8], array2[num8+1] - array2[num8])
                num8 += 1
            self.dataBlocksDATO[num5][num8] = DataBlock(array2[num8], array[num5+1] - array2[num8])
            num5 += 1

        # 进度条和列表框更新逻辑占位
        progress_max = 136
        num11 = 0
        while num11 <= 135:
            num12 = 0
            while num12 <= 3:
                text = f"ID:{num11:04d}-{num12}"
                # ListBoxImages.Items.Add(text)  # UI操作占位
                num12 += 1
            if num11 % 30 == 0:
                pass  # 进度条更新占位
            num11 += 1

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

    def AnalysisTXT(self):
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
                self.datablocksTXT[num5][num9] = DataBlock(array2[num9], array2[num9+1] - array2[num9])
                num9 += 1
            self.datablocksTXT[num5][num9] = DataBlock(array2[num9], array[num5+1] - array2[num9])
            num5 += 1

        # 进度条和列表框更新逻辑占位
        progress_max = 34
        num13 = 0
        while num13 <= 33:
            num14 = self.TXTsubBlockCount[num13] - 1
            num15 = 0
            while num15 <= num14:
                text = f"ID:{num13:04d}-{num15:04d}"
                # ListBoxImages.Items.Add(text)  # UI操作占位
                num15 += 1
            if num13 % 30 == 0:
                pass  # 进度条更新占位
            num13 += 1

    def AnalysisFIGANI(self):
        array = [0] * 409
        num = 6
        while num <= 1638:
            index = int((num - 6) / 4)
            array[index] = struct.unpack('<I', self.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            self.FIGANIsubBlockCount[num5] = self.fileDatas[array[num5]]
            num8 = self.FIGANIsubBlockCount[num5] - 1
            array2 = [0] * (num8 + 1)
            num9 = 0
            while num9 <= num8:
                array2[num9] = array[num5] + struct.unpack('<I', self.fileDatas[array[num5]+8+num9*4 : array[num5]+12+num9*4])[0]
                num9 += 1

            num11 = self.FIGANIsubBlockCount[num5] - 2
            num9 = 0
            while num9 <= num11:
                self.dataBlocksFIGANI[num5][num9] = DataBlock(array2[num9], array2[num9+1] - array2[num9])
                num9 += 1
            self.dataBlocksFIGANI[num5][num9] = DataBlock(array2[num9], array[num5+1] - array2[num9])
            num5 += 1

        # 进度条和列表框更新逻辑占位
        progress_max = 408
        num13 = 0
        while num13 <= 407:
            num14 = self.FIGANIsubBlockCount[num13] - 1
            num15 = 0
            while num15 <= num14:
                text = f"ID:{num13:04d}-{num15:03d}"
                # ListBoxImages.Items.Add(text)  # UI操作占位
                num15 += 1
            if num13 % 30 == 0:
                pass  # 进度条更新占位
            num13 += 1

    def AnalysisICON(self):
        array = [0] * 1681
        num = 6
        while num <= 6726:
            index = int((num - 6) / 4)
            array[index] = struct.unpack('<I', self.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2  # 1679
        num5 = 0
        while num5 <= num4:  # 0 to 1679
            self.datablocksICON[num5] = DataBlock(array[num5], array[num5 + 1] - array[num5])
            num5 += 1
        # 最后一个数据块：使用文件结尾
        self.datablocksICON[num5] = DataBlock(array[num5], len(self.fileDatas) - array[num5])

        # 进度条和列表框更新逻辑占位
        progress_max = 1680
        num8 = 0
        while num8 <= 1679:
            text = f"ID:{num8:05d}"
            # ListBoxImages.Items.Add(text)  # UI操作占位
            if num8 % 80 == 0:
                pass  # 进度条更新占位
            num8 += 1
    
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

    def AnalysisBG(self):
        array = [0] * 57
        num = 6
        while num <= 230:
            index = int((num - 6) / 4)
            array[index] = struct.unpack('<I', self.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            self.dataBlocksBG[num5] = DataBlock(array[num5], array[num5 + 1] - array[num5])
            num5 += 1
        self.dataBlocksBG[num5] = DataBlock(array[num5], len(self.fileDatas) - array[num5])

        # 进度条和列表框更新逻辑占位
        progress_max = 56
        num8 = 0
        while num8 <= 55:
            text = f"ID:{num8:03d}"
            # ListBoxImages.Items.Add(text)  # UI操作占位
            if num8 % 4 == 0:
                pass  # 进度条更新占位
            num8 += 1
   
    def load_fdother_file(self, file_path):
        with open(file_path, 'rb') as f:
            self.fileDatas = f.read()
        # 使用AnalysisOTHER和AnalysisOtherSubs进行文件分析
        self.AnalysisOTHER()
        # print(f'datablocksOTHER长度:{len(self.datablocksOTHER)}')
        # 处理所有子索引
        for subIndex in range(len(self.datablocksOTHER)):
            self.AnalysisOtherSubs(subIndex)
            self.AnalysisOtherSubsImage(subIndex)
            
   

if __name__ == '__main__':
    import sys
    file_path = None
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = 'FDOTHER.DAT'
    
    main = Main()
    main.load_fdother_file(file_path)
    print(f'处理完成，图像已保存至 {main.output_dir} 目录')
    
