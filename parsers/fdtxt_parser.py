"""FDTXT.DAT文件解析器 - 文本资源"""

from typing import List, Optional
from .base_parser import BaseParser, DataBlock


class FdTxtParser(BaseParser):
    """FDTXT.DAT文件解析器"""
    
    def __init__(self, main_instance):
        super().__init__()
        self.main = main_instance
        self.datablocks: List[List[Optional[DataBlock]]] = [[None for _ in range(701)] for _ in range(35)]
        self.sub_block_counts: List[int] = [0] * 35
    
    def analysis(self) -> List[List[Optional[DataBlock]]]:
        """解析FDTXT数据结构"""
        if self.main.fileDatas is None:
            return self.main.datablocksTXT
            
        array = [0] * 35
        num = 6
        while num <= 142:
            index = int((num - 6) / 4)
            if num + 4 <= len(self.main.fileDatas):
                array[index] = struct.unpack('<I', self.main.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        main_block_index = 0
        while main_block_index <= num4:
            if array[main_block_index] + 2 <= len(self.main.fileDatas):
                self.sub_block_counts[main_block_index] = int(struct.unpack('<h', self.main.fileDatas[array[main_block_index]:array[main_block_index]+2])[0] / 2)
            sub_block_count = self.sub_block_counts[main_block_index] - 1
            array2 = [0] * (sub_block_count + 1)
            sub_block_index = 0
            while sub_block_index <= sub_block_count:
                if array[main_block_index] + (sub_block_index+1)*2 <= len(self.main.fileDatas):
                    array2[sub_block_index] = array[main_block_index] + struct.unpack('<h', self.main.fileDatas[array[main_block_index] + sub_block_index*2 : array[main_block_index] + (sub_block_index+1)*2])[0]
                sub_block_index += 1

            sub_block_index_max = self.sub_block_counts[main_block_index] - 2
            sub_block_index = 0
            while sub_block_index <= sub_block_index_max:
                # 确保不会越界
                if main_block_index < len(self.main.datablocksTXT) and sub_block_index < len(self.main.datablocksTXT[main_block_index]):
                    self.main.datablocksTXT[main_block_index][sub_block_index] = DataBlock(array2[sub_block_index], array2[sub_block_index+1] - array2[sub_block_index])
                sub_block_index += 1
            # 处理最后一个数据块
            if main_block_index < len(self.main.datablocksTXT) and sub_block_index < len(self.main.datablocksTXT[main_block_index]):
                self.main.datablocksTXT[main_block_index][sub_block_index] = DataBlock(array2[sub_block_index], array[main_block_index+1] - array2[sub_block_index])
            main_block_index += 1

        # 将子块计数复制到main实例
        for i in range(len(self.sub_block_counts)):
            self.main.subBlockCountsTXT[i] = self.sub_block_counts[i]
        
        return self.main.datablocksTXT


# 需要导入struct模块
import struct