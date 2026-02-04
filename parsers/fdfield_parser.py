"""FDFIELD.DAT文件解析器 - 地图资源"""

import struct
from typing import List, Optional
from .base_parser import BaseParser, DataBlock


class FdFieldParser(BaseParser):
    """FDFIELD.DAT文件解析器"""
    
    def __init__(self, main_instance):
        super().__init__()
        self.main = main_instance
        self.datablocks: List[Optional[DataBlock]] = [None] * 100
    
    def analysis(self) -> List[Optional[DataBlock]]:
        """分析FDFIELD数据结构"""
        if self.main.fileDatas is None:
            return self.datablocks
            
        array = [0] * 100
        num = 6
        while num <= 402:
            index = int((num - 6) / 4)
            if index < len(array) and num + 4 <= len(self.main.fileDatas):
                array[index] = struct.unpack('<I', self.main.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            if num5 < len(self.main.datablocksFDFIELD) and num5 + 1 < len(array):
                self.main.datablocksFDFIELD[num5] = DataBlock(array[num5], array[num5 + 1] - array[num5])
            num5 += 1
        # 处理最后一个数据块
        if num5 < len(self.main.datablocksFDFIELD) and num5 < len(array) and self.main.fileDatas is not None:
            self.main.datablocksFDFIELD[num5] = DataBlock(array[num5], len(self.main.fileDatas) - array[num5])
            
        return self.main.datablocksFDFIELD