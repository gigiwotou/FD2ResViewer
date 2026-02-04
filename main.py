import io
import os
import struct
from PIL import Image
import sys
from typing import Any, Optional

# 对应C#的DataBlock类
from PIL import ImageColor

from parsers.base_parser import BaseParser, BaseImageParser, DataBlock, Color, ColorPanel, BMPMaker
from parsers.fdfield_parser import FdFieldParser
from parsers.fdother_parser import FdOtherParser
from parsers.fdicon_parser import FdIconParser
from parsers.fdshap_parser import FdShapParser
from parsers.fdtxt_parser import FdTxtParser
from parsers.dato_parser import DatoParser
from parsers.bg_parser import BgParser
from parsers.tai_parser import TaiParser
from parsers.figani_parser import FigAniParser
from parsers.ani_parser import AniParser

import os
import struct
from PIL import Image

class Main:
    """FD2资源分析主类"""

    def __init__(self):
        self.fileDatas = None
        self.output_dir = 'output_images'
        
        # 初始化实例变量（不是类变量）
        # 统一变量命名规则：使用驼峰命名法，并在变量名中表明类型
        self.datablocksICON = [None] * 1681  # List[Optional[DataBlock]]
        self.datablocksBG = [None] * 57  # List[Optional[DataBlock]]
        self.datablocksTAI = [None] * 57  # List[Optional[DataBlock]]
        self.datablocksDATO = [[None for _ in range(4)] for _ in range(137)]  # List[List[Optional[DataBlock]]]
        self.datablocksFDFIELD = [None] * 100  # List[Optional[DataBlock]]
        self.datablocksOTHER = [None] * 104  # List[Optional[DataBlock]]
        self.datablocksOTHERSubs = None  # Optional[List[Optional[DataBlock]]]
        self.datablocksFDSHAP = [[None for _ in range(401)] for _ in range(67)]  # List[List[Optional[DataBlock]]]
        self.subBlockCountsFDSHAP = [0] * 67  # List[int]
        self.datablocksTXT = [[None for _ in range(701)] for _ in range(35)]  # List[List[Optional[DataBlock]]]
        self.subBlockCountsTXT = [0] * 35  # List[int]
        self.datablocksFIGANI = [[None for _ in range(41)] for _ in range(409)]  # List[List[Optional[DataBlock]]]
        self.subBlockCountsFIGANI = [0] * 409  # List[int]
        self.datablocksANI = [[None for _ in range(100)] for _ in range(9)]  # List[List[Optional[DataBlock]]] - ANI文件有9个分段
        self.subBlockCountsANI = [0] * 9  # List[int] - ANI文件有9个分段
        self.shapsDone = False  # bool
        self.shaps = [None] * 401  # 用于存储图块图像的数组
        
        # 文件数据变量
        self.fileDatasBG = None  # Optional[bytes]
        self.fileDatasDATO = None  # Optional[bytes]
        self.fileDatasFDFIELD = None  # Optional[bytes]
        self.fileDatasOTHER = None  # Optional[bytes]
        self.fileDatasFDSHAP = None  # Optional[bytes]
        self.fileDatasTXT = None  # Optional[bytes]
        self.fileDatasFIGANI = None  # Optional[bytes]
        self.fileDatasFD2 = None  # Optional[bytes]
        
        os.makedirs(self.output_dir, exist_ok=True)

        # 初始化解析器实例
        self.fdfield_parser = FdFieldParser(self)
        self.fdother_parser = FdOtherParser(self)
        self.fdicon_parser = FdIconParser(self)
        self.fdshap_parser = FdShapParser(self)
        self.fdtxt_parser = FdTxtParser(self)
        self.dato_parser = DatoParser(self)
        self.bg_parser = BgParser(self)
        self.tai_parser = TaiParser(self)
        self.figani_parser = FigAniParser(self)
        self.ani_parser = AniParser(self)
        
        # 初始化BMP Maker实例
        self.bmp_maker = BMPMaker()

    def AnalysisFDFIELD(self):
        """分析FDFIELD数据结构"""
        return self.fdfield_parser.analysis()

    def AnalysisOTHER(self):
        """分析FDOTHER数据结构"""
        return self.fdother_parser.analysis()
    
    def AnalysisOtherSubs(self, subIndex):
        """分析FDOTHER子数据结构"""
        return self.fdother_parser.analysis_subs(subIndex)

    def AnalysisOtherSubsImage(self, subIndex):
        """分析FDOTHER子项图像 - 委托给FdOtherParser"""
        return self.fdother_parser.analysis_subs_image(subIndex)

    def AnalysisICON(self):
        """分析FDICON数据结构"""
        return self.fdicon_parser.analysis()

    def AnalysisFDSHAP(self):
        """分析FDSHAP数据结构"""
        return self.fdshap_parser.analysis()

    def AnalysisTXT(self):
        """分析FDTXT数据结构"""
        return self.fdtxt_parser.analysis()

    def AnalysisDATO(self):
        """分析DATO数据结构"""
        return self.dato_parser.analysis()

    def AnalysisBG(self):
        """分析BG数据结构"""
        return self.bg_parser.analysis()

    def AnalysisTAI(self):
        """分析TAI数据结构"""
        return self.tai_parser.analysis()

    def AnalysisFIGANI(self):
        """分析FIGANI数据结构"""
        return self.figani_parser.analysis()

    def AnalysisANI(self):
        """分析ANI数据结构"""
        return self.ani_parser.analysis()

