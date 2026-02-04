"""ANI.DAT文件解析器 - 动画资源"""

from typing import List, Optional
import struct
from .base_parser import BaseParser, DataBlock


class AniParser(BaseParser):
    """ANI.DAT文件解析器"""
    
    def __init__(self, main_instance):
        super().__init__()
        self.main = main_instance
        self.datablocks: List[List[Optional[DataBlock]]] = [[None for _ in range(100)] for _ in range(9)]  # ANI文件有9个分段
        self.sub_block_counts: List[int] = [0] * 9  # ANI文件有9个分段
    
    def analysis(self) -> List[List[Optional[DataBlock]]]:
        """分析ANI数据结构
        ANI文件有9个分段，每段包含动画数据
        每个段以"AFM - Animation File Manager..."开头，后面是"Empty Title."，然后是帧数据
        根据分析，30x63动画精灵在每个段的固定偏移位置（0xd0 = 208字节处）
        """
        if self.main.fileDatas is None:
            return self.main.datablocksANI
            
        # 读取9个主要分段的偏移量 (跳过文件头的6字节)
        segment_offsets = []
        for i in range(9):
            offset_bytes = self.main.fileDatas[6 + i*4:6 + (i+1)*4]
            offset = struct.unpack('<I', offset_bytes)[0]
            segment_offsets.append(offset)
        
        # 分析每个段
        for i in range(9):
            start_offset = segment_offsets[i]
            end_offset = segment_offsets[i+1] if i+1 < len(segment_offsets) else len(self.main.fileDatas)
            
            frame_idx = 0
            frames_found = 0
            
            # 检查固定位置是否有有效的30x63帧 (在段内偏移0xd0处)
            fixed_pos = start_offset + 0xd0  # 0xd0 = 208字节
            
            if fixed_pos + 6 <= len(self.main.fileDatas):
                length = struct.unpack('<H', self.main.fileDatas[fixed_pos:fixed_pos+2])[0]
                width = struct.unpack('<H', self.main.fileDatas[fixed_pos+2:fixed_pos+4])[0]
                height = struct.unpack('<H', self.main.fileDatas[fixed_pos+4:fixed_pos+6])[0]
                
                # 检查是否是30x63帧
                if width == 30 and height == 63 and length > 0 and fixed_pos + 6 + length <= end_offset:
                    # 创建数据块，包含帧头和数据
                    frame_size = 6 + length  # 帧头(6字节) + 数据
                    self.main.datablocksANI[i][frame_idx] = DataBlock(fixed_pos, frame_size)
                    frames_found += 1
                    frame_idx += 1
            
            # 同时也搜索其他可能的帧（在Empty Title之后的区域）
            segment_data = self.main.fileDatas[start_offset:end_offset]
            empty_title_pos = segment_data.find(b"Empty Title.")
            
            if empty_title_pos != -1:
                # 从Empty Title之后开始搜索其他帧（但避免重复检测30x63帧的位置）
                current_file_pos = start_offset + empty_title_pos + len(b"Empty Title.")
                
                while current_file_pos < end_offset - 6 and frame_idx < len(self.main.datablocksANI[i]):
                    # 跳过已知的30x63帧位置，避免重复
                    if abs(current_file_pos - (start_offset + 0xd0)) < 10:  # 避免在30x63附近重复搜索
                        current_file_pos += 2
                        continue
                        
                    if current_file_pos + 6 <= len(self.main.fileDatas):
                        length = struct.unpack('<H', self.main.fileDatas[current_file_pos:current_file_pos+2])[0]
                        width = struct.unpack('<H', self.main.fileDatas[current_file_pos+2:current_file_pos+4])[0]
                        height = struct.unpack('<H', self.main.fileDatas[current_file_pos+4:current_file_pos+6])[0]
                        
                        # 检查是否是合理的帧数据
                        if (10 <= width <= 320 and 10 <= height <= 240 and 
                            width * height <= length and  # 长度应至少等于像素数
                            length > 0 and current_file_pos + 6 + length <= end_offset):  # 确保数据不超出段范围
                            
                            # 创建数据块，包含帧头和数据
                            frame_size = 6 + length  # 帧头(6字节) + 数据
                            self.main.datablocksANI[i][frame_idx] = DataBlock(current_file_pos, frame_size)
                            frames_found += 1
                            frame_idx += 1
                            break  # 暂时每个段最多找2个帧，避免解析错误
                            
                    current_file_pos += 2
        
            # 设置找到的帧数量
            self.sub_block_counts[i] = frames_found
            
        # 将子块计数同步到主实例
        for i in range(len(self.sub_block_counts)):
            self.main.subBlockCountsANI[i] = self.sub_block_counts[i]
        
        return self.main.datablocksANI