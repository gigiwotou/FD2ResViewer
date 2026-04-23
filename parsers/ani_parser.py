"""ANI.DAT文件解析器 - 动画资源"""

from typing import List, Optional
import struct
from .base_parser import BaseParser, DataBlock


class AfmDecoder:
    """AFM (Animation File Manager) 解码器 - 修复版"""

    def __init__(self):
        self.palette_buf = bytearray(768)
        self.pixel_buf = bytearray(64000)

    def decode_pixel_rle(self, data: bytes, pos: int) -> int:
        """命令 0x06: RLE 解码像素"""
        src_pos = pos
        dst_pos = 0

        while src_pos < len(data) and dst_pos < 64000:
            b = data[src_pos]
            src_pos += 1

            if (b & 0xC0) == 0xC0:
                count = b & 0x3F
                if src_pos < len(data):
                    color = data[src_pos]
                    src_pos += 1
                    for i in range(min(count, 64000 - dst_pos)):
                        self.pixel_buf[dst_pos + i] = color
                    dst_pos += count
            else:
                if dst_pos < 64000:
                    self.pixel_buf[dst_pos] = b
                dst_pos += 1

        return src_pos - pos

    def process_frame(self, param: int, frame_data: bytes):
        """处理帧数据"""
        if param == 0 or len(frame_data) == 0:
            return

        data_pos = 0

        for _ in range(param):
            if data_pos >= len(frame_data):
                break

            cmd = frame_data[data_pos]
            data_pos += 1

            if cmd == 0x00:
                if data_pos < len(frame_data):
                    color = frame_data[data_pos]
                    data_pos += 1
                    for i in range(256):
                        self.palette_buf[i * 3] = color
                        self.palette_buf[i * 3 + 1] = color
                        self.palette_buf[i * 3 + 2] = color

            elif cmd == 0x01:
                if data_pos + 768 <= len(frame_data):
                    self.palette_buf[:] = frame_data[data_pos:data_pos + 768]
                    data_pos += 768

            elif cmd == 0x02:
                src_pos = data_pos
                dst_pos = 0
                while dst_pos < 768 and src_pos < len(frame_data):
                    b = frame_data[src_pos]
                    src_pos += 1
                    if (b & 0xC0) == 0xC0:
                        count = b & 0x3F
                        if src_pos < len(frame_data):
                            color = frame_data[src_pos]
                            src_pos += 1
                            for i in range(min(count, 768 - dst_pos)):
                                self.palette_buf[dst_pos + i] = color
                            dst_pos += count
                    else:
                        self.palette_buf[dst_pos] = b
                        dst_pos += 1
                data_pos = src_pos

            elif cmd == 0x04:
                if data_pos < len(frame_data):
                    fill_byte = frame_data[data_pos]
                    data_pos += 1
                    for i in range(64000):
                        self.pixel_buf[i] = fill_byte

            elif cmd == 0x05:
                if data_pos + 64000 <= len(frame_data):
                    self.pixel_buf[:] = frame_data[data_pos:data_pos + 64000]
                    data_pos += 64000

            elif cmd == 0x06:
                data_pos += self.decode_pixel_rle(frame_data, data_pos)

            elif cmd == 0x07:
                count = struct.unpack('<H', frame_data[data_pos:data_pos+2])[0]
                data_pos += 2

                for _ in range(count):
                    if data_pos + 3 > len(frame_data):
                        break
                    offset = struct.unpack('<H', frame_data[data_pos:data_pos+2])[0]
                    color = frame_data[data_pos+2]
                    data_pos += 3

                    if offset < 64000:
                        self.pixel_buf[offset] = color

            elif cmd == 0x08:
                count = struct.unpack('<H', frame_data[data_pos:data_pos+2])[0]
                data_pos += 2

                for _ in range(count):
                    if data_pos + 4 > len(frame_data):
                        break
                    offset = struct.unpack('<H', frame_data[data_pos:data_pos+2])[0]
                    size = frame_data[data_pos+2]
                    color = frame_data[data_pos+3]
                    data_pos += 4

                    for i in range(min(size, 64000 - offset)):
                        self.pixel_buf[offset + i] = color

            elif cmd == 0x09:
                count = struct.unpack('<H', frame_data[data_pos:data_pos+2])[0]
                data_pos += 2

                for _ in range(count):
                    if data_pos + 3 > len(frame_data):
                        break
                    dst = struct.unpack('<H', frame_data[data_pos:data_pos+2])[0]
                    size = frame_data[data_pos+2]
                    data_pos += 3

                    for i in range(min(size, 64000 - dst)):
                        if data_pos + i < len(frame_data):
                            self.pixel_buf[dst + i] = frame_data[data_pos + i]

                    data_pos += size

    def decode_afm(self, data: bytes, afm_offset: int) -> List:
        """解码单个 AFM 资源，返回帧图像列表"""
        self.palette_buf = bytearray(768)
        self.pixel_buf = bytearray(64000)

        frame_count = struct.unpack('<H', data[afm_offset + 165:afm_offset + 167])[0]
        frame_start = afm_offset + 173

        frames = []
        prev_pixel_buf = bytearray(64000)

        pos = frame_start

        for i in range(frame_count):
            if pos + 8 > len(data):
                break

            size = struct.unpack('<H', data[pos:pos+2])[0]
            param = struct.unpack('<H', data[pos+2:pos+4])[0]

            frame_data = data[pos+8:pos+8+size] if size > 0 else b''

            prev_pixel_buf[:] = self.pixel_buf
            self.process_frame(param, frame_data)

            pos += 8 + size

            if self.pixel_buf == prev_pixel_buf:
                continue

            from PIL import Image
            img = Image.new('P', (320, 200))
            img.putdata(list(self.pixel_buf))

            pal = []
            for j in range(256):
                r = min(255, self.palette_buf[j * 3] * 4)
                g = min(255, self.palette_buf[j * 3 + 1] * 4)
                b = min(255, self.palette_buf[j * 3 + 2] * 4)
                pal.extend([r, g, b])

            img.putpalette(pal)
            frames.append(img)

        return frames


class AniParser(BaseParser):
    """ANI.DAT文件解析器"""

    def __init__(self, main_instance):
        super().__init__()
        self.main = main_instance
        self.afm_offsets: List[int] = []
        self.decoder = AfmDecoder()

    def find_afm_offsets(self) -> List[int]:
        """找到所有有效的 AFM 偏移量"""
        if self.main.fileDatas is None:
            return []

        afm_offsets = []
        pos = 6

        while pos < len(self.main.fileDatas) - 4:
            offset = struct.unpack('<I', self.main.fileDatas[pos:pos+4])[0]
            if offset == 0:
                break

            if offset < len(self.main.fileDatas) and offset + 167 < len(self.main.fileDatas):
                frame_count = struct.unpack('<H', self.main.fileDatas[offset + 165:offset + 167])[0]
                if frame_count > 0 and frame_count < 1000:
                    afm_offsets.append(offset)

            pos += 4
            if len(afm_offsets) > 20:
                break

        return afm_offsets

    def analysis(self) -> List[List[Optional[DataBlock]]]:
        """分析ANI数据结构"""
        if self.main.fileDatas is None:
            return self.main.datablocksANI

        self.afm_offsets = self.find_afm_offsets()
        return self.main.datablocksANI

    def decode_all_afm(self):
        """解码所有 AFM 动画并返回 GIF 数据"""
        if self.main.fileDatas is None or not self.afm_offsets:
            return {}

        results = {}
        for idx, offset in enumerate(self.afm_offsets):
            try:
                frames = self.decoder.decode_afm(self.main.fileDatas, offset)
                if frames:
                    results[idx] = frames
            except Exception as e:
                print(f"AFM {idx} 解码失败: {e}")
        return results