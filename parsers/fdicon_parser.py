"""FDICON.B24文件解析器 - 人物图标"""

from typing import List, Optional
from .base_parser import BaseParser, DataBlock


class FdIconParser(BaseParser):
    """FDICON.B24文件解析器"""
    
    def __init__(self, main_instance):
        super().__init__()
        self.main = main_instance
        self.datablocks: List[Optional[DataBlock]] = [None] * 1681
    
    def analysis(self) -> List[Optional[DataBlock]]:
        """解析FDICON数据结构"""
        if self.main.fileDatas is None:
            return self.main.datablocksICON
            
        array = [0] * 1681
        num = 6
        while num <= 6726:
            index = int((num - 6) / 4)
            # 确保索引在有效范围内
            if index < len(array) and num + 4 <= len(self.main.fileDatas):
                array[index] = struct.unpack('<I', self.main.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            # 确保索引在有效范围内
            if num5 < len(self.main.datablocksICON):
                self.main.datablocksICON[num5] = DataBlock(array[num5], array[num5 + 1] - array[num5])
            num5 += 1
        # 处理最后一个数据块
        if num5 < len(self.main.datablocksICON) and num5 < len(array) and self.main.fileDatas is not None:
            self.main.datablocksICON[num5] = DataBlock(array[num5], len(self.main.fileDatas) - array[num5])
            
        return self.main.datablocksICON


# 需要导入struct模块
import struct