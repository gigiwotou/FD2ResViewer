#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
炎龙骑士团II资源分析器 - 扩展版本
支持多种DAT文件格式的分析和图像提取
"""

import os
import struct
import io
from PIL import Image
import sys
from main import Main, ColorPanel, BMPMaker, DataBlock

class FD2Analyzer(Main):
    """扩展的FD2资源分析器"""
    
    def __init__(self):
        super().__init__()
        self.dataBlocksBG = [None] * 57
        self.dataBlocksDATO = [[None for _ in range(4)] for _ in range(137)]
        self.dataBlocksFDSHAP = [[None for _ in range(401)] for _ in range(67)]
        self.FDSHAPsubBlockCount = [0] * 67
        self.dataBlocksFIGANI = [[None for _ in range(41)] for _ in range(409)]
        self.FIGANIsubBlockCount = [0] * 409
        self.datablocksTXT = [[None for _ in range(701)] for _ in range(35)]
        self.TXTsubBlockCount = [0] * 35
        self.shapFileDatas = None
        
    def load_fdother_file(self, file_path):
        """分析FDOTHER.DAT文件 - 混合资源"""
        print("分析FDOTHER.DAT文件...")
        with open(file_path, 'rb') as f:
            self.fileDatas = f.read()
        
        self.AnalysisOTHER()
        print(f'FDOTHER分析完成，共{len(self.datablocksOTHER)}个主分类')
        
        # 处理所有子索引并生成图像
        total_images = 0
        for subIndex in range(len(self.datablocksOTHER)):
            if self.datablocksOTHER[subIndex] and self.datablocksOTHER[subIndex].length > 4:
                try:
                    # 分析子数据结构
                    self.AnalysisOtherSubs(subIndex)
                    # 生成图像
                    image_count = self.AnalysisOtherSubsImage(subIndex)
                    if image_count > 0:
                        total_images += image_count
                        print(f'主分类{subIndex}: 生成{image_count}个图像')
                except Exception as e:
                    print(f'主分类{subIndex}处理失败: {e}')
        
        print(f'成功提取{total_images}个FDOTHER图像')

    def AnalysisOtherSubsImage(self, subIndex):
        """处理FDOTHER子数据结构并生成图像"""
        image_count = 0
        if self.datablocksOTHERSubs and len(self.datablocksOTHERSubs) > 0:
            num = subIndex
            num3 = num
            
            for num2 in range(len(self.datablocksOTHERSubs)):
                try:
                    if num3 == 1 or num3 == 96:
                        start_offset = self.datablocksOTHER[num].startOffset + self.datablocksOTHERSubs[num2].startOffset
                        if num == 96:
                            sWidth = 24
                            sHeight = 24
                        else:
                            sWidth = struct.unpack('<h', self.fileDatas[self.datablocksOTHER[num].startOffset : self.datablocksOTHER[num].startOffset+2])[0]
                            sHeight = struct.unpack('<h', self.fileDatas[self.datablocksOTHER[num].startOffset+2 : self.datablocksOTHER[num].startOffset+4])[0]
                        
                        # 生成形状图像
                        image = self.bmp_maker.makeShapBMP(
                            sWidth, sHeight,
                            self.fileDatas,
                            start_offset,
                            self.datablocksOTHERSubs[num2].length,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'fdother_shap_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                        image_count += 1
     
                    elif num3 == 2:
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
                        image_path = os.path.join(self.output_dir, f'fdother_other_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                        image_count += 1
                        
                    elif num3 == 4:
                        data_offset = self.datablocksOTHER[num3].startOffset + self.datablocksOTHERSubs[num2].startOffset
                        
                        # 生成字体图像
                        image = self.bmp_maker.makeFontBMP(
                            self.fileDatas,
                            data_offset,
                            self.datablocksOTHERSubs[num2].length
                        )
                        image_path = os.path.join(self.output_dir, f'fdother_font_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                        image_count += 1

                    elif num3 in (5, 6, 7, 9, 12, 13, 14, 63, 79):
                        start_offset = self.datablocksOTHER[num3].startOffset + self.datablocksOTHERSubs[num2].startOffset
                        
                        if self.datablocksOTHERSubs[num2].length >= 4:
                            sWidth = struct.unpack('<h', self.fileDatas[start_offset:start_offset+2])[0]
                            sHeight = struct.unpack('<h', self.fileDatas[start_offset+2:start_offset+4])[0]
                            
                            # 根据不同的分类使用不同的处理方法
                            if num3 in (6, 9):  # 面部图像
                                image = self.bmp_maker.makeFaceBMP(
                                    self.fileDatas,
                                    start_offset,
                                    self.datablocksOTHERSubs[num2].length,
                                    ColorPanel(1)
                                )
                                image_path = os.path.join(self.output_dir, f'fdother_face_{subIndex}_{num2:03d}.png')
                            elif num3 == 7:  # 使用特殊调色板的形状
                                image = self.bmp_maker.makeShapBMP(
                                    sWidth, sHeight,
                                    self.fileDatas,
                                    start_offset + 4,
                                    self.datablocksOTHERSubs[num2].length - 4,
                                    ColorPanel(3)
                                )
                                image_path = os.path.join(self.output_dir, f'fdother_shap_{subIndex}_{num2:03d}.png')
                            else:  # 其他类型
                                if 0 < sWidth <= 640 and 0 < sHeight <= 480:  # 合理的尺寸
                                    image = self.bmp_maker.makeBMP(
                                        sWidth, sHeight,
                                        self.fileDatas,
                                        start_offset + 4,
                                        self.datablocksOTHERSubs[num2].length - 4,
                                        ColorPanel(1)
                                    )
                                    image_path = os.path.join(self.output_dir, f'fdother_other_{subIndex}_{num2:03d}.png')
                                else:
                                    continue  # 跳过无效尺寸
                            
                            image.save(image_path)
                            image_count += 1
                            
                except Exception as e:
                    print(f'子索引{subIndex}-{num2}处理失败: {e}')
                    continue
        
        return image_count
                
    def load_fdicon_file(self, file_path):
        """分析FDICON.B24文件 - 人物图标"""
        print("分析FDICON.B24文件...")
        with open(file_path, 'rb') as f:
            self.fileDatas = f.read()
        
        self.AnalysisICON()
        print(f'FDICON分析完成，共{len(self.datablocksICON)}个图标')
        
        # 生成图标图像
        success_count = 0
        for i in range(len(self.datablocksICON)):
            if self.datablocksICON[i] and self.datablocksICON[i].length > 4:
                try:
                    image = self.bmp_maker.makeBMP(
                        24, 24,  # 图标固定大小24x24
                        self.fileDatas,
                        self.datablocksICON[i].startOffset,
                        self.datablocksICON[i].length,
                        ColorPanel(1)
                    )
                    image_path = os.path.join(self.output_dir, f'icon_{i:05d}.png')
                    image.save(image_path)
                    success_count += 1
                except Exception as e:
                    print(f'图标{i}处理失败: {e}')
        print(f'成功提取{success_count}个图标')
                    
    def load_dato_file(self, file_path):
        """分析DATO.DAT文件 - 人物表情"""
        print("分析DATO.DAT文件...")
        with open(file_path, 'rb') as f:
            self.fileDatas = f.read()
        
        self.AnalysisDATO()
        print('DATO分析完成')
        
        # 生成表情图像
        success_count = 0
        for i in range(len(self.dataBlocksDATO)):
            for j in range(4):
                if self.dataBlocksDATO[i][j] and self.dataBlocksDATO[i][j].length > 4:
                    try:
                        image = self.bmp_maker.makeFaceBMP(
                            self.fileDatas,
                            self.dataBlocksDATO[i][j].startOffset,
                            self.dataBlocksDATO[i][j].length,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.output_dir, f'face_{i:04d}_{j}.png')
                        image.save(image_path)
                        success_count += 1
                    except Exception as e:
                        print(f'表情{i}-{j}处理失败: {e}')
        print(f'成功提取{success_count}个表情')
                        
    def load_bg_file(self, file_path):
        """分析BG.DAT文件 - 战斗背景"""
        print("分析BG.DAT文件...")
        with open(file_path, 'rb') as f:
            self.fileDatas = f.read()
        
        self.AnalysisBG()
        print(f'BG分析完成，共{len(self.dataBlocksBG)}个背景')
        
        # 生成背景图像
        success_count = 0
        for i in range(len(self.dataBlocksBG)):
            if self.dataBlocksBG[i] and self.dataBlocksBG[i].length > 4:
                try:
                    image = self.bmp_maker.makeBgBMP(
                        self.fileDatas,
                        self.dataBlocksBG[i].startOffset,
                        self.dataBlocksBG[i].length,
                        ColorPanel(1)
                    )
                    image_path = os.path.join(self.output_dir, f'bg_{i:03d}.png')
                    image.save(image_path)
                    success_count += 1
                except Exception as e:
                    print(f'背景{i}处理失败: {e}')
        print(f'成功提取{success_count}个背景')

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
                self.dataBlocksDATO[num5][num8] = DataBlock(array2[num8], array2[num8+1] - array2[num8])
                num8 += 1
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
            self.dataBlocksBG[num5] = DataBlock(array[num5], array[num5 + 1] - array[num5])
            num5 += 1
        self.dataBlocksBG[num5] = DataBlock(array[num5], len(self.fileDatas) - array[num5])

    def analyze_file(self, file_path):
        """根据文件名自动选择合适的分析方法"""
        file_name = os.path.basename(file_path).lower()
        
        if 'fdother.dat' in file_name:
            print('分析FDOTHER.DAT文件...')
            self.load_fdother_file(file_path)
        elif 'fdicon.b24' in file_name:
            print('分析FDICON.B24文件...')
            self.load_fdicon_file(file_path)
        elif 'dato.dat' in file_name:
            print('分析DATO.DAT文件...')
            self.load_dato_file(file_path)
        elif 'bg.dat' in file_name:
            print('分析BG.DAT文件...')
            self.load_bg_file(file_path)
        else:
            print(f'暂不支持的文件类型: {file_name}')
            print('当前支持的文件类型:')
            print('- FDOTHER.DAT (混合资源)')
            print('- FDICON.B24 (人物图标)')
            print('- DATO.DAT (人物表情)')
            print('- BG.DAT (战斗背景)')
            return False
        return True
        
    def batch_analyze(self, directory):
        """批量分析目录中的所有支持文件"""
        supported_files = ['fdother.dat', 'fdicon.b24', 'dato.dat', 'bg.dat']
        found_files = []
        
        for file in os.listdir(directory):
            if file.lower() in supported_files:
                found_files.append(os.path.join(directory, file))
        
        if not found_files:
            print(f'在目录 {directory} 中未找到支持的文件')
            return
            
        print(f'找到{len(found_files)}个支持的文件:')
        for file in found_files:
            print(f'  - {os.path.basename(file)}')
        
        for file in found_files:
            print(f'\n开始处理: {os.path.basename(file)}')
            if self.analyze_file(file):
                print(f'完成: {os.path.basename(file)}')
            else:
                print(f'失败: {os.path.basename(file)}')

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='炎龙骑士团II资源分析器')
    parser.add_argument('input', help='输入文件或目录路径')
    parser.add_argument('-o', '--output', default='output_images', help='输出目录 (默认: output_images)')
    parser.add_argument('-b', '--batch', action='store_true', help='批量模式：分析目录中的所有文件')
    
    args = parser.parse_args()
    
    analyzer = FD2Analyzer()
    analyzer.output_dir = args.output
    os.makedirs(analyzer.output_dir, exist_ok=True)
    
    if args.batch:
        if os.path.isdir(args.input):
            analyzer.batch_analyze(args.input)
        else:
            print('批量模式需要指定目录路径')
    else:
        if os.path.isfile(args.input):
            if analyzer.analyze_file(args.input):
                print(f'\n处理完成，结果已保存至 {analyzer.output_dir} 目录')
            else:
                print('\n文件处理失败')
        else:
            print('指定的文件不存在')

if __name__ == '__main__':
    main()