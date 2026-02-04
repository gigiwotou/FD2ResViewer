"""FDSHAP.DAT文件解析器 - 形状资源"""

from typing import List, Optional
from .base_parser import BaseParser, DataBlock


class FdShapParser(BaseParser):
    """FDSHAP.DAT文件解析器"""
    
    def __init__(self, main_instance):
        super().__init__()
        self.main = main_instance
        self.datablocks: List[List[Optional[DataBlock]]] = [[None for _ in range(401)] for _ in range(67)]
        self.sub_block_counts: List[int] = [0] * 67
        self.shaps_done: bool = False
    
    def analysis(self) -> List[List[Optional[DataBlock]]]:
        """解析FDSHAP数据结构"""
        if self.main.fileDatas is None:
            return self.main.datablocksFDSHAP
            
        array = [0] * 67
        num = 6
        while num <= 270:
            index = int((num - 6) / 4)
            if num + 4 <= len(self.main.fileDatas):
                array[index] = struct.unpack('<I', self.main.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            if array[num5] + 6 <= len(self.main.fileDatas):
                self.sub_block_counts[num5] = struct.unpack('<h', self.main.fileDatas[array[num5]+4 : array[num5]+6])[0]
            sub_block_count = self.sub_block_counts[num5] - 1
            array2 = [0] * (sub_block_count + 1)
            num9 = 0
            while num9 <= sub_block_count:
                if array[num5] + 10 + num9*4 <= len(self.main.fileDatas):
                    array2[num9] = array[num5] + struct.unpack('<I', self.main.fileDatas[array[num5]+6+num9*4 : array[num5]+10+num9*4])[0]
                num9 += 1

            sub_block_index_max = self.sub_block_counts[num5] - 2
            num9 = 0
            while num9 <= sub_block_index_max:
                if num5 < len(self.main.datablocksFDSHAP) and num9 < len(self.main.datablocksFDSHAP[num5]):
                    self.main.datablocksFDSHAP[num5][num9] = DataBlock(array2[num9], array2[num9+1] - array2[num9])
                num9 += 1
            if num5 < len(self.main.datablocksFDSHAP) and num9 < len(self.main.datablocksFDSHAP[num5]):
                self.main.datablocksFDSHAP[num5][num9] = DataBlock(array2[num9], array[num5+1] - array2[num9])
            num5 += 2

        # 将子块计数复制到main实例
        for i in range(len(self.sub_block_counts)):
            self.main.subBlockCountsFDSHAP[i] = self.sub_block_counts[i]
        
        # 将shaps_done状态也同步到main实例
        self.main.shapsDone = True
        
        self.shaps_done = True
        return self.main.datablocksFDSHAP


# 需要导入struct模块
import struct