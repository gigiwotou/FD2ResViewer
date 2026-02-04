"""FIGANI.DAT文件解析器 - 战斗动作序列"""

from typing import List, Optional
import struct
from .base_parser import BaseParser, DataBlock


class FigAniParser(BaseParser):
    """FIGANI.DAT文件解析器"""
    
    def __init__(self, main_instance):
        super().__init__()
        self.main = main_instance
        self.datablocks: List[List[Optional[DataBlock]]] = [[None for _ in range(41)] for _ in range(409)]
        self.sub_block_counts: List[int] = [0] * 409
    
    def analysis(self) -> List[List[Optional[DataBlock]]]:
        """分析FIGANI数据结构
        对应C#版本的AnalysisFIGANI方法
        """
        # 创建一个大小为409的数组来存储偏移量
        array = [0] * 409
        num = 6
        
        # 确保self.main.fileDatas不为None
        if self.main.fileDatas is None:
            return self.main.datablocksFIGANI
        
        # 读取偏移量数据
        while num <= 1638:
            # 与C#版本保持一致：使用四舍五入计算索引
            index = int(round((num - 6) / 4.0))
            # 确保索引在有效范围内
            if index < len(array) and num + 4 <= len(self.main.fileDatas):
                array[index] = struct.unpack('<I', self.main.fileDatas[num:num+4])[0]
            num += 4
        
        # 用于存储子块偏移量的数组
        array2 = [0] * 41
        num4 = len(array) - 2  # 对应C#中的array.Length - 2
        num5 = 0
        
        # 处理每个FIGANI块
        while num5 <= num4:
            # 读取子块数量
            if array[num5] + 1 <= len(self.main.fileDatas):
                self.sub_block_counts[num5] = self.main.fileDatas[array[num5]]
            else:
                self.sub_block_counts[num5] = 0
                num5 += 1
                continue
            
            num8 = self.sub_block_counts[num5] - 1
            num9 = 0
            
            # 读取子块偏移量
            while num9 <= num8:
                if array[num5] + 8 + num9 * 4 + 4 <= len(self.main.fileDatas) and num9 < len(array2):
                    array2[num9] = array[num5] + struct.unpack('<I', self.main.fileDatas[array[num5] + 8 + num9 * 4 : array[num5] + 8 + (num9+1)*4])[0]
                num9 += 1
            
            # 创建DataBlock对象
            num11 = self.sub_block_counts[num5] - 2
            num9 = 0
            
            while num9 <= num11:
                if num9 + 1 < len(array2):
                    self.main.datablocksFIGANI[num5][num9] = DataBlock(array2[num9], array2[num9 + 1] - array2[num9])
                num9 += 1
            
            # 处理最后一个子块
            if num9 < len(array2) and num5 + 1 < len(array):
                self.main.datablocksFIGANI[num5][num9] = DataBlock(array2[num9], array[num5 + 1] - array2[num9])
            
            num5 += 1
        
        # 将子块计数同步到主实例
        for i in range(len(self.sub_block_counts)):
            self.main.subBlockCountsFIGANI[i] = self.sub_block_counts[i]
        
        return self.main.datablocksFIGANI


# 需要导入struct模块
import struct