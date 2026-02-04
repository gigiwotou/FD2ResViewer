"""DATO.DAT文件解析器 - 人物表情"""

from typing import List, Optional
from .base_parser import BaseParser, DataBlock


class DatoParser(BaseParser):
    """DATO.DAT文件解析器"""
    
    def __init__(self, main_instance):
        super().__init__()
        self.main = main_instance
        self.datablocks: List[List[Optional[DataBlock]]] = [[None for _ in range(4)] for _ in range(137)]
    
    def analysis(self) -> List[List[Optional[DataBlock]]]:
        """解析DATO数据结构"""
        if self.main.fileDatas is None:
            return self.main.datablocksDATO
            
        array = [0] * 137
        num = 6
        while num <= 550:
            index = int((num - 6) / 4)
            if num + 4 <= len(self.main.fileDatas):
                array[index] = struct.unpack('<I', self.main.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            array2 = [0] * 4
            num8 = 0
            while num8 <= 3:
                if array[num5] + (num8+1)*4 <= len(self.main.fileDatas):
                    array2[num8] = array[num5] + struct.unpack('<I', self.main.fileDatas[array[num5] + num8*4 : array[num5] + (num8+1)*4])[0]
                num8 += 1

            num8 = 0
            while num8 <= 2:
                # 确保不会越界
                if num5 < len(self.main.datablocksDATO) and num8 < len(self.main.datablocksDATO[num5]):
                    self.main.datablocksDATO[num5][num8] = DataBlock(array2[num8], array2[num8+1] - array2[num8])
                num8 += 1
            # 处理最后一个数据块
            if num5 < len(self.main.datablocksDATO) and num8 < len(self.main.datablocksDATO[num5]):
                self.main.datablocksDATO[num5][num8] = DataBlock(array2[num8], array[num5+1] - array2[num8])
            num5 += 1

        return self.main.datablocksDATO


# 需要导入struct模块
import struct