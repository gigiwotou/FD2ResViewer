"""FDOTHER.DAT文件解析器 - 混合资源"""

import struct
import os
from typing import List, Optional
from .base_parser import BaseParser, DataBlock, ColorPanel, BMPMaker


class FdOtherParser(BaseParser):
    """FDOTHER.DAT文件解析器"""
    
    def __init__(self, main_instance):
        super().__init__()
        self.main = main_instance
        self.datablocks: List[Optional[DataBlock]] = [None] * 104
        self.datablocksSubs: Optional[List[Optional[DataBlock]]] = None
        self.bmp_maker = BMPMaker()
    
    def analysis(self) -> List[Optional[DataBlock]]:
        """分析FDOTHER数据结构"""
        if self.main.fileDatas is None:
            return self.main.datablocksOTHER
            
        array = [0] * 104
        num = 6
        while num <= 418:  # 6 + (104-1)*4 = 418
            index = int((num - 6) / 4)
            if num + 4 <= len(self.main.fileDatas):
                array[index] = struct.unpack('<I', self.main.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            # 确保索引在有效范围内
            if num5 < len(self.main.datablocksOTHER) and num5 + 1 < len(array):
                self.main.datablocksOTHER[num5] = DataBlock(array[num5], array[num5 + 1] - array[num5])
            num5 += 1
        # 处理最后一个数据块
        if num5 < len(self.main.datablocksOTHER) and num5 < len(array) and self.main.fileDatas is not None:
            self.main.datablocksOTHER[num5] = DataBlock(array[num5], len(self.main.fileDatas) - array[num5])

        # 调用AnalysisOtherSubs处理子索引
        for sub_index in range(104):
            self.analysis_subs(sub_index)
            
        return self.main.datablocksOTHER

    def analysis_subs(self, subIndex):
        """分析FDOTHER子数据结构"""
        if subIndex in (1, 14):
            # 添加None检查
            if self.main.datablocksOTHER[subIndex] is None or self.main.fileDatas is None:
                return
            datablock = self.main.datablocksOTHER[subIndex]
            if datablock is None:
                return
            num43 = datablock.startOffset + 6
            sWidth = struct.unpack('<h', self.main.fileDatas[datablock.startOffset : datablock.startOffset+2])[0]
            sHeight = struct.unpack('<h', self.main.fileDatas[datablock.startOffset+2 : datablock.startOffset+4])[0]
            num44 = struct.unpack('<h', self.main.fileDatas[datablock.startOffset+4 : datablock.startOffset+6])[0]
            self.main.datablocksOTHERSubs = [None] * (num44)
            array5 = [0] * num44
            num45 = num44 - 1
            num46 = 0
            while num46 <= num45:
                array5[num46] = struct.unpack('<I', self.main.fileDatas[num43 + num46*4 : num43 + (num46+1)*4])[0]
                num46 += 1

            num48 = num44 - 2
            num46 = 0
            while num46 <= num48:
                if self.main.datablocksOTHERSubs is not None:
                    self.main.datablocksOTHERSubs[num46] = DataBlock(array5[num46], array5[num46+1] - array5[num46])
                num46 += 1
            if self.main.datablocksOTHERSubs is not None:
                self.main.datablocksOTHERSubs[num46] = DataBlock(array5[num46], datablock.length - array5[num46])

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
            if self.main.datablocksOTHER[subIndex] is None or self.main.fileDatas is None:
                return
            datablock = self.main.datablocksOTHER[subIndex]
            if datablock is None:
                return
            startOffset2 = datablock.startOffset
            num34 = int(struct.unpack('<I', self.main.fileDatas[startOffset2:startOffset2+4])[0] / 4)
            array4 = [0] * num34
            self.main.datablocksOTHERSubs = [None] * num34  # type: ignore
            num36 = 0
            while num36 < num34:
                array4[num36] = struct.unpack('<I', self.main.fileDatas[startOffset2 + num36*4 : startOffset2 + (num36+1)*4])[0]
                num36 += 1

            num38 = num34 - 2
            num36 = 0
            while num36 <= num38:
                if self.main.datablocksOTHERSubs is not None:
                    self.main.datablocksOTHERSubs[num36] = DataBlock(array4[num36], array4[num36+1] - array4[num36])
                num36 += 1
            if self.main.datablocksOTHERSubs is not None:
                self.main.datablocksOTHERSubs[num36] = DataBlock(array4[num36], datablock.length - array4[num36])

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
            if self.main.datablocksOTHER[subIndex] is None:
                return
            datablock = self.main.datablocksOTHER[subIndex]
            if datablock is None:
                return
            obj = datablock.length / 32
            array2 = [i*32 for i in range(int(obj))]
            self.main.datablocksOTHERSubs = [None] * len(array2)  # type: ignore
            num17 = 0
            while num17 < len(array2)-1:
                if self.main.datablocksOTHERSubs is not None:
                    self.main.datablocksOTHERSubs[num17] = DataBlock(array2[num17], array2[num17+1] - array2[num17])
                num17 += 1
            if self.main.datablocksOTHERSubs is not None:
                self.main.datablocksOTHERSubs[num17] = DataBlock(array2[num17], datablock.length - array2[num17])

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
            if self.main.datablocksOTHER[subIndex] is None or self.main.fileDatas is None:
                return
            datablock = self.main.datablocksOTHER[subIndex]
            if datablock is None:
                return
            num3 = datablock.startOffset + 4
            # print(f"解析数据段 subIndex：{subIndex}. 起始地址: 0x{datablock.startOffset:X}")
            num4 = struct.unpack('<h', self.main.fileDatas[num3:num3+2])[0]
            # print(f"subIndex: {subIndex}, num4: {num4}")
            array = [0] * num4
            self.main.datablocksOTHERSubs = [None] * num4  # type: ignore
            num6 = 0
            while num6 < num4:
                array[num6] = struct.unpack('<I', self.main.fileDatas[num3+2 + num6*4 : num3+6 + num6*4])[0]
                # print(f"subIndex: {subIndex}, num6: {num6}, array[num6]: {array[num6]}")
                # print(f"subIndex: {subIndex}, num6: {num6}, array[num6]: 0x{datablock.startOffset + array[num6]:X}")
                num6 += 1

            num9 = num4 - 2
            num6 = 0
            while num6 <= num9:
                if self.main.datablocksOTHERSubs is not None:
                    self.main.datablocksOTHERSubs[num6] = DataBlock(array[num6], array[num6+1] - array[num6])
                num6 += 1
            if self.main.datablocksOTHERSubs is not None:
                self.main.datablocksOTHERSubs[num6] = DataBlock(array[num6], datablock.length - array[num6])

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
            if self.main.datablocksOTHER[subIndex] is None or self.main.fileDatas is None:
                return
            datablock = self.main.datablocksOTHER[subIndex]
            if datablock is None:
                return
            num24 = datablock.startOffset + 6
            short_value = struct.unpack('<h', self.main.fileDatas[num24:num24+2])[0]
            num25 = int(round((short_value - 6) / 4.0 - 1.0))
            num25 = max(0, num25)
            array3 = [0] * num25  # 数组长度匹配C#的num25
            self.main.datablocksOTHERSubs = [None] * num25  # type: ignore
            num26 = num25 - 1  # 循环上限保持num25-1，与C#一致
            num27 = 0
            while num27 <= num26:
                array3[num27] = struct.unpack('<I', self.main.fileDatas[num24 + num27*4 : num24 + (num27+1)*4])[0]
                num27 += 1

            num29 = len(array3) - 2  # 修正为Python的len()语法
            num27 = 0
            while num27 <= num29:
                if self.main.datablocksOTHERSubs is not None:
                    self.main.datablocksOTHERSubs[num27] = DataBlock(array3[num27], array3[num27+1] - array3[num27])
                num27 += 1
            if self.main.datablocksOTHERSubs is not None:
                self.main.datablocksOTHERSubs[num27] = DataBlock(array3[num27], datablock.length - array3[num27])

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
            if self.main.datablocksOTHER[subIndex] is None or self.main.fileDatas is None:
                return
            datablock = self.main.datablocksOTHER[subIndex]
            if datablock is None:
                return
            # 调用BMPMaker生成面部图像
            sWidth = struct.unpack('<h', self.main.fileDatas[datablock.startOffset : datablock.startOffset+2])[0]
            sHeight = struct.unpack('<h', self.main.fileDatas[datablock.startOffset+2 : datablock.startOffset+4])[0]
            image = self.bmp_maker.makeFaceBMP(
                self.main.fileDatas,
                datablock.startOffset,
                datablock.length,
                ColorPanel(1)  # 使用灰色调色板
            )
            image_path = os.path.join(self.main.output_dir, f'face_{subIndex}.png')
            image.save(image_path)

        elif subIndex in (11, 16, 17, 46, 47, 56, 59, 60, 61, 62, 69, 70, 71, 72, 73, 74, 75, 97, 98, 100):
            # 添加None检查
            if self.main.datablocksOTHER[subIndex] is None or self.main.fileDatas is None:
                return
            datablock = self.main.datablocksOTHER[subIndex]
            if datablock is None:
                return
            sWidth = struct.unpack('<h', self.main.fileDatas[datablock.startOffset : datablock.startOffset+2])[0]
            sHeight = struct.unpack('<h', self.main.fileDatas[datablock.startOffset+2 : datablock.startOffset+4])[0]
            # 使用资源文件初始化调色板
            # colorpanel = ColorPanel(1)
            if 73 < subIndex < 76:
                colorpanel = ColorPanel(2)
            else:
                colorpanel = ColorPanel(1)
            image = self.bmp_maker.makeShapBMP(
                sWidth, sHeight,
                self.main.fileDatas,
                datablock.startOffset + 4,
                datablock.length - 4,
                colorpanel
            )
            image_path = os.path.join(self.main.output_dir, f'shap_{subIndex}.png')
            image.save(image_path)
        elif subIndex == 55:
            # 添加None检查
            if self.main.datablocksOTHER[subIndex] is None or self.main.fileDatas is None:
                return
            datablock = self.main.datablocksOTHER[subIndex]
            if datablock is None:
                return
            sWidth = struct.unpack('<h', self.main.fileDatas[datablock.startOffset : datablock.startOffset+2])[0]
            sHeight = struct.unpack('<h', self.main.fileDatas[datablock.startOffset+2 : datablock.startOffset+4])[0]
            image = self.bmp_maker.makeBMP(
                sWidth, sHeight,
                self.main.fileDatas,
                datablock.startOffset + 4,
                datablock.length - 4,
                ColorPanel(1)
            )
            image_path = os.path.join(self.main.output_dir, f'other_{subIndex}.png')
            image.save(image_path)
        elif subIndex == 79:
            # 添加None检查
            if self.main.datablocksOTHER[subIndex] is None or self.main.fileDatas is None:
                return
            datablock = self.main.datablocksOTHER[subIndex]
            if datablock is None:
                return
            num3 = datablock.startOffset + 2
            print(f"解析数据段 subIndex：{subIndex}. 起始地址: 0x{datablock.startOffset:X}")
            # 从num3 + 4位置开始读取num4
            num4 = struct.unpack('<h', self.main.fileDatas[num3:num3+2])[0]
            print(f"subIndex: {subIndex}, num4: {num4}")

            array = [0] * num4
            self.main.datablocksOTHERSubs = [None] * num4  # type: ignore
            num6 = 0
            while num6 < num4:
                array[num6] = struct.unpack('<I', self.main.fileDatas[num3+6 + num6*4 : num3+10 + num6*4])[0]
                print(f"subIndex: {subIndex}, num6: {num6}, array[num6]: 0x{datablock.startOffset + array[num6]:X}")
                num6 += 1

            num9 = num4 - 2
            num6 = 0
            while num6 <= num9:
                if self.main.datablocksOTHERSubs is not None:
                    self.main.datablocksOTHERSubs[num6] = DataBlock(array[num6], array[num6+1] - array[num6])
                if self.main.datablocksOTHERSubs is not None and self.main.datablocksOTHERSubs[num6] is not None:
                    datablock_sub = self.main.datablocksOTHERSubs[num6]
                    if datablock_sub is not None:
                        print(f"subIndex: {subIndex}, num6: {num6}, array[num6]: 0x{array[num6]:X}, length: {datablock_sub.length}")
                num6 += 1
        
            if self.main.datablocksOTHERSubs is not None and num6 < len(self.main.datablocksOTHERSubs):
                self.main.datablocksOTHERSubs[num6] = DataBlock(array[num6], datablock.length - array[num6])
          
        else:
            print(f"未解析数据段 subIndex：{subIndex}. 起始地址: 0x{self.main.datablocksOTHER[subIndex].startOffset:X}")

    def analysis_subs_image(self, subIndex):
        """分析FDOTHER子图像数据"""
        if self.main.datablocksOTHERSubs and len(self.main.datablocksOTHERSubs) > 0:
            # Converted from ListBoxSecond_SelectedIndexChanged in MainForm.cs
            num = subIndex
            num3 = num
            # print(f"len:{len(self.datablocksOTHERSubs)}, subIndex:{subIndex}")
            for num2 in range(len(self.main.datablocksOTHERSubs)):
                if num3 == 1 or num3 == 96:
                    # 添加None检查
                    if self.main.datablocksOTHER[num] is None or self.main.datablocksOTHERSubs[num2] is None:
                        continue
                    datablock = self.main.datablocksOTHER[num]
                    datablockSub = self.main.datablocksOTHERSubs[num2]
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
                        if datablock is not None and self.main.fileDatas is not None:
                            sWidth = struct.unpack('<h', self.main.fileDatas[datablock.startOffset : datablock.startOffset+2])[0]
                            sHeight = struct.unpack('<h', self.main.fileDatas[datablock.startOffset+2 : datablock.startOffset+4])[0]
                    # print(f"subIndex: {subIndex}, num2: {num2:03d}, start_offset: {start_offset}, sWidth: {sWidth}, sHeight: {sHeight}")

                    # 生成形状图像                
                    image = self.bmp_maker.makeShapBMP(
                        sWidth, sHeight,
                        self.main.fileDatas,
                        start_offset,
                        datablockSub.length,
                        ColorPanel(1)
                    )
                    image_path = os.path.join(self.main.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                    image.save(image_path)
 
                if num3 == 2:
                    # 添加None检查
                    if self.main.datablocksOTHER[num] is None or self.main.datablocksOTHERSubs[num2] is None:
                        continue
                    datablock = self.main.datablocksOTHER[num]
                    datablockSub = self.main.datablocksOTHERSubs[num2]
                    if datablock is None or datablockSub is None:
                        continue
                    start_offset = datablock.startOffset + datablockSub.startOffset
                    
                    sWidth = 0  # 默认值
                    sHeight = 0  # 默认值
                    if self.main.fileDatas is not None and start_offset + 2 <= len(self.main.fileDatas) and start_offset + 4 <= len(self.main.fileDatas):
                        sWidth = struct.unpack('<h', self.main.fileDatas[start_offset:start_offset+2])[0]
                        sHeight = struct.unpack('<h', self.main.fileDatas[start_offset+2:start_offset+4])[0]

                    data_offset = start_offset + 4
                    
                    # 生成其他类型图像                      
                    image = self.bmp_maker.makeBMP(
                        sWidth, sHeight,
                        self.main.fileDatas,
                        data_offset,
                        datablockSub.length - 4,
                        ColorPanel(1)
                    )
                    image_path = os.path.join(self.main.output_dir, f'other_{subIndex}_{num2:03d}.png')
                    image.save(image_path)
                    

                if num3 == 4:
                    # 添加None检查
                    if self.main.datablocksOTHER[num3] is None or self.main.datablocksOTHERSubs[num2] is None:
                        continue
                    datablock = self.main.datablocksOTHER[num3]
                    datablockSub = self.main.datablocksOTHERSubs[num2]
                    if datablock is None or datablockSub is None:
                        continue
                    data_offset = datablock.startOffset + datablockSub.startOffset
                    
                    # 生成字体图像                
                    image = self.bmp_maker.makeFontBMP(
                        self.main.fileDatas,
                        data_offset,
                        datablockSub.length
                    )
                    image_path = os.path.join(self.main.output_dir, f'font_{subIndex}_{num2:03d}.png')
                    image.save(image_path)
                   
                if num3 == 5:
                    # 添加None检查
                    if self.main.datablocksOTHER[num3] is None or self.main.datablocksOTHERSubs[num2] is None:
                        continue
                    datablock = self.main.datablocksOTHER[num3]
                    datablockSub = self.main.datablocksOTHERSubs[num2]
                    if datablock is None or datablockSub is None:
                        continue
                    start_offset = datablock.startOffset + datablockSub.startOffset

                    sWidth = 0  # 默认值
                    sHeight = 0  # 默认值
                    if self.main.fileDatas is not None and start_offset + 2 <= len(self.main.fileDatas) and start_offset + 4 <= len(self.main.fileDatas):
                        sWidth = struct.unpack('<h', self.main.fileDatas[start_offset:start_offset+2])[0]
                        sHeight = struct.unpack('<h', self.main.fileDatas[start_offset+2:start_offset+4])[0]

                    # print(f"subIndex: {subIndex}, num2: {num2:03d}, start_offset: {start_offset}, sWidth: {sWidth}, sHeight: {sHeight}, data_offset: {start_offset}")
                    if num2 < 20:
                        data_offset = start_offset + 4
                        # 生成其他类型图像                    
                        image = self.bmp_maker.makeBMP(
                            sWidth, sHeight,
                            self.main.fileDatas,
                            data_offset,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.main.output_dir, f'other_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 < 23:
                        data_offset = start_offset
                        if self.main.fileDatas is not None and data_offset + 4 <= len(self.main.fileDatas):
                            sWidth = struct.unpack('<h', self.main.fileDatas[data_offset:data_offset+2])[0]
                            sHeight = struct.unpack('<h', self.main.fileDatas[data_offset+2:data_offset+4])[0]
                        # 生成面部图像                
                        image = self.bmp_maker.makeFaceBMP(
                            self.main.fileDatas,
                            data_offset,
                            datablockSub.length,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.main.output_dir, f'face_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 < 31:
                        data_offset = start_offset + 4
                        # 生成其他类型图像                    
                        image = self.bmp_maker.makeBMP(
                            sWidth, sHeight,
                            self.main.fileDatas,
                            data_offset,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.main.output_dir, f'other_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 < 53:
                        image = self.bmp_maker.makeShapBMP(
                            sWidth, sHeight,
                            self.main.fileDatas,
                            start_offset + 4,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.main.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 < 64 and num2 != 59:
                        data_offset = start_offset + 4
                        # 生成其他类型图像                    
                        image = self.bmp_maker.makeBMP(
                            sWidth, sHeight,
                            self.main.fileDatas,
                            data_offset,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.main.output_dir, f'other_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 != 59:
                        if num2 < 119 and num2 != 93:
                            data_offset = start_offset
                            if self.main.fileDatas is not None and data_offset + 4 <= len(self.main.fileDatas):
                                sWidth = struct.unpack('<h', self.main.fileDatas[data_offset:data_offset+2])[0]
                                sHeight = struct.unpack('<h', self.main.fileDatas[data_offset+2:data_offset+4])[0]
                            # 生成面部图像                
                            image = self.bmp_maker.makeFaceBMP(
                                self.main.fileDatas,
                                data_offset,
                                datablockSub.length,
                                ColorPanel(1)
                            )
                            image_path = os.path.join(self.main.output_dir, f'face_{subIndex}_{num2:03d}.png')
                            image.save(image_path)
                        else:
                            image = self.bmp_maker.makeShapBMP(
                            sWidth, sHeight,
                            self.main.fileDatas,
                            start_offset + 4,
                            datablockSub.length - 4,
                            ColorPanel(1)
                            )
                            image_path = os.path.join(self.main.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                            image.save(image_path)

                if num3 == 7:
                    # 添加None检查
                    if self.main.datablocksOTHER[num] is None or self.main.datablocksOTHERSubs[num2] is None:
                        continue
                    datablock = self.main.datablocksOTHER[num]
                    datablockSub = self.main.datablocksOTHERSubs[num2]
                    if datablock is None or datablockSub is None:
                        continue
                    start_offset = datablock.startOffset + datablockSub.startOffset
                    sWidth = 0  # 默认值
                    sHeight = 0  # 默认值
                    if self.main.fileDatas is not None and start_offset + 2 <= len(self.main.fileDatas) and start_offset + 4 <= len(self.main.fileDatas):
                        sWidth = struct.unpack('<h', self.main.fileDatas[start_offset:start_offset+2])[0]
                        sHeight = struct.unpack('<h', self.main.fileDatas[start_offset+2:start_offset+4])[0]
                    color_panel = ColorPanel(3)  # Create new color panel with ID 3
                    data_offset = start_offset + 4
                    # print(f"subIndex: {subIndex}, num2: {num2:03d}, start_offset: {start_offset}, sWidth: {sWidth}, sHeight: {sHeight}, data_offset: {data_offset}")
                    # 生成形状图像                
                    image = self.bmp_maker.makeShapBMP(
                        sWidth, sHeight,
                        self.main.fileDatas,
                        data_offset,
                        datablockSub.length - 4,
                        color_panel
                    )
                    image_path = os.path.join(self.main.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                    image.save(image_path)

                if num3 in (6, 9):
                    # 添加None检查
                    if self.main.datablocksOTHER[num3] is None or self.main.datablocksOTHERSubs[num2] is None:
                        continue
                    datablock = self.main.datablocksOTHER[num3]
                    datablockSub = self.main.datablocksOTHERSubs[num2]
                    if datablock is None or datablockSub is None:
                        continue
                    start_offset = datablock.startOffset + datablockSub.startOffset
                    sWidth = 0  # 默认值
                    sHeight = 0  # 默认值
                    if self.main.fileDatas is not None and start_offset + 2 <= len(self.main.fileDatas) and start_offset + 4 <= len(self.main.fileDatas):
                        sWidth = struct.unpack('<h', self.main.fileDatas[start_offset:start_offset+2])[0]
                        sHeight = struct.unpack('<h', self.main.fileDatas[start_offset+2:start_offset+4])[0]
                    data_offset = start_offset
                    if self.main.fileDatas is not None and data_offset + 2 <= len(self.main.fileDatas) and data_offset + 4 <= len(self.main.fileDatas):
                        sWidth = struct.unpack('<h', self.main.fileDatas[data_offset:data_offset+2])[0]
                        sHeight = struct.unpack('<h', self.main.fileDatas[data_offset+2:data_offset+4])[0]
                
                    # 生成面部图像                
                    image = self.bmp_maker.makeFaceBMP(
                        self.main.fileDatas,
                        data_offset,
                        datablockSub.length,
                        ColorPanel(1)
                    )
                    image_path = os.path.join(self.main.output_dir, f'face_{subIndex}_{num2:03d}.png')
                    image.save(image_path)
                   


                if num3 in (12, 63):
                    # 添加None检查
                    if self.main.datablocksOTHER[num3] is None or self.main.datablocksOTHERSubs[num2] is None:
                        continue
                    datablock = self.main.datablocksOTHER[num3]
                    datablockSub = self.main.datablocksOTHERSubs[num2]
                    if datablock is None or datablockSub is None:
                        continue
                    start_offset = datablock.startOffset + datablockSub.startOffset
                    sWidth = 0  # 默认值
                    sHeight = 0  # 默认值
                    if self.main.fileDatas is not None and start_offset + 2 <= len(self.main.fileDatas) and start_offset + 4 <= len(self.main.fileDatas):
                        sWidth = struct.unpack('<h', self.main.fileDatas[start_offset:start_offset+2])[0]
                        sHeight = struct.unpack('<h', self.main.fileDatas[start_offset+2:start_offset+4])[0]
                    
                    if num2 == 0 or (num2 >= 23 and num2 <= 29):
                        data_offset = start_offset + 4
                        # 生成形状图像                      
                        image = self.bmp_maker.makeShapBMP(
                            sWidth, sHeight,
                            self.main.fileDatas,
                            data_offset,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.main.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 == 1 or num2 == 2 or (num2 >= 11 and num2 < 22):
                        data_offset = start_offset
                        if self.main.fileDatas is not None and data_offset + 2 <= len(self.main.fileDatas) and data_offset + 4 <= len(self.main.fileDatas):
                            sWidth = struct.unpack('<h', self.main.fileDatas[data_offset:data_offset+2])[0]
                            sHeight = struct.unpack('<h', self.main.fileDatas[data_offset+2:data_offset+4])[0]
                        # 生成面部图像                    
                        image = self.bmp_maker.makeFaceBMP(
                            self.main.fileDatas,
                            data_offset,
                            datablockSub.length,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.main.output_dir, f'face_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    else:
                        data_offset = start_offset + 4
                        # 生成其他类型图像                    
                        image = self.bmp_maker.makeBMP(
                            sWidth, sHeight,
                            self.main.fileDatas,
                            data_offset,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.main.output_dir, f'other_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    


                if num3 == 13:
                    # 添加None检查
                    if self.main.datablocksOTHER[num3] is None or self.main.datablocksOTHERSubs[num2] is None:
                        continue
                    datablock = self.main.datablocksOTHER[num3]
                    datablockSub = self.main.datablocksOTHERSubs[num2]
                    if datablock is None or datablockSub is None:
                        continue
                    start_offset = datablock.startOffset + datablockSub.startOffset
                    sWidth = 0  # 默认值
                    sHeight = 0  # 默认值
                    if self.main.fileDatas is not None and start_offset + 2 <= len(self.main.fileDatas) and start_offset + 4 <= len(self.main.fileDatas):
                        sWidth = struct.unpack('<h', self.main.fileDatas[start_offset:start_offset+2])[0]
                        sHeight = struct.unpack('<h', self.main.fileDatas[start_offset+2:start_offset+4])[0]
                    
                    if num2 == 0:
                        data_offset = start_offset + 4
                        # 生成形状图像                      
                        image = self.bmp_maker.makeShapBMP(
                            sWidth, sHeight,
                            self.main.fileDatas,
                            data_offset,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.main.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 == 1 or num2 == 2 or num2 >= 11:
                        data_offset = start_offset
                        if self.main.fileDatas is not None and data_offset + 2 <= len(self.main.fileDatas) and data_offset + 4 <= len(self.main.fileDatas):
                            sWidth = struct.unpack('<h', self.main.fileDatas[data_offset:data_offset+2])[0]
                            sHeight = struct.unpack('<h', self.main.fileDatas[data_offset+2:data_offset+4])[0]
                        # 生成面部图像                    
                        image = self.bmp_maker.makeFaceBMP(
                            self.main.fileDatas,
                            data_offset,
                            datablockSub.length,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.main.output_dir, f'face_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    else:
                        data_offset = start_offset + 4
                        # 生成其他类型图像                    
                        image = self.bmp_maker.makeBMP(
                            sWidth, sHeight,
                            self.main.fileDatas,
                            data_offset,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.main.output_dir, f'other_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    


                if num3 == 14:
                    # 添加None检查
                    if self.main.datablocksOTHER[num] is None or self.main.datablocksOTHERSubs[num2] is None:
                        continue
                    datablock = self.main.datablocksOTHER[num]
                    datablockSub = self.main.datablocksOTHERSubs[num2]
                    if datablock is None or datablockSub is None:
                        continue
                    start_offset = datablock.startOffset + datablockSub.startOffset
                    sWidth = 0  # 默认值
                    sHeight = 0  # 默认值
                    if self.main.fileDatas is not None and start_offset + 2 <= len(self.main.fileDatas) and start_offset + 4 <= len(self.main.fileDatas):
                        sWidth = struct.unpack('<h', self.main.fileDatas[start_offset:start_offset+2])[0]
                        sHeight = struct.unpack('<h', self.main.fileDatas[start_offset+2:start_offset+4])[0]
                    
                    if num2 == 0 or num2 >= 23:
                        data_offset = start_offset + 4
                        # 生成形状图像                    
                        image = self.bmp_maker.makeShapBMP(
                            sWidth, sHeight,
                            self.main.fileDatas,
                            data_offset,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.main.output_dir, f'shap_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    elif num2 == 1 or num2 == 2 or (num2 >= 11 and num2 < 23):
                        data_offset = start_offset
                        if self.main.fileDatas is not None and data_offset + 2 <= len(self.main.fileDatas) and data_offset + 4 <= len(self.main.fileDatas):
                            sWidth = struct.unpack('<h', self.main.fileDatas[data_offset:data_offset+2])[0]
                            sHeight = struct.unpack('<h', self.main.fileDatas[data_offset+2:data_offset+4])[0]
                        # 生成面部图像                    
                        image = self.bmp_maker.makeFaceBMP(
                            self.main.fileDatas,
                            data_offset,
                            datablockSub.length,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.main.output_dir, f'face_{subIndex}_{num2:03d}.png')
                        image.save(image_path)
                    else:
                        data_offset = start_offset + 4
                        # 生成其他类型图像                    
                        image = self.bmp_maker.makeBMP(
                            sWidth, sHeight,
                            self.main.fileDatas,
                            data_offset,
                            datablockSub.length - 4,
                            ColorPanel(1)
                        )
                        image_path = os.path.join(self.main.output_dir, f'other_{subIndex}_{num2:03d}.png')
                        image.save(image_path)

                # if num3 == 79:
                #     # 添加None检查
                #     if self.main.datablocksOTHER[num3] is None or self.main.datablocksOTHERSubs[num2] is None:
                #         continue
                #     datablock = self.main.datablocksOTHER[num3]
                #     datablockSub = self.main.datablocksOTHERSubs[num2]
                #     if datablock is None or datablockSub is None:
                #         continue
                #     start_offset = datablock.startOffset + datablockSub.startOffset

                #     sWidth = 0 
                #     sHeight = 0  
                #     if self.main.fileDatas is not None and start_offset + 2 <= len(self.main.fileDatas) and start_offset + 4 <= len(self.main.fileDatas):
                #         sWidth = struct.unpack('<h', self.main.fileDatas[start_offset:start_offset+2])[0]
                #         sHeight = struct.unpack('<h', self.main.fileDatas[start_offset+2:start_offset+4])[0]

                #     # print(f"subIndex: {subIndex}, num2: {num2:03d}, start_offset: {start_offset}, sWidth: {sWidth}, sHeight: {sHeight}, data_offset: {start_offset}")
                    
                #     data_offset = start_offset + 4
                #     # 生成其他类型图像                    
                #     image = self.bmp_maker.makeBMP(
                #         sWidth, sHeight,
                #         self.main.fileDatas,
                #         data_offset,
                #         datablockSub.length - 4,
                #         ColorPanel(1)
                #     )
                #     image_path = os.path.join(self.main.output_dir, f'other_{subIndex}_{num2:03d}.png')
                #     image.save(image_path)