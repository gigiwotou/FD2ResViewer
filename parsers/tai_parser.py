"""TAI.DAT文件解析器 - 战斗动作图像"""

from typing import List, Optional
from .base_parser import BaseParser, DataBlock


class TaiParser(BaseParser):
    """TAI.DAT文件解析器"""
    
    def __init__(self, main_instance):
        super().__init__()
        self.main = main_instance
        self.datablocks: List[Optional[DataBlock]] = [None] * 57
    
    def analysis(self) -> List[Optional[DataBlock]]:
        """解析TAI数据结构（专用）"""
        if self.main.fileDatas is None:
            return self.main.datablocksTAI
            
        array = [0] * 57
        num = 6
        while num <= 230:
            index = int((num - 6) / 4)
            if num + 4 <= len(self.main.fileDatas):
                array[index] = struct.unpack('<I', self.main.fileDatas[num:num+4])[0]
            num += 4

        num4 = len(array) - 2
        num5 = 0
        while num5 <= num4:
            # 确保不会越界
            if num5 < len(self.main.datablocksTAI):
                self.main.datablocksTAI[num5] = DataBlock(array[num5], array[num5 + 1] - array[num5])
            num5 += 1
        # 处理最后一个数据块
        if num5 < len(self.main.datablocksTAI):
            self.main.datablocksTAI[num5] = DataBlock(array[num5], len(self.main.fileDatas) - array[num5])
            
        return self.main.datablocksTAI


# 需要导入struct模块
import struct