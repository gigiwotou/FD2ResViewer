import struct
import argparse

def search_width_height(file_path, target_width, target_height, start_offset=0):
    """
    在二进制文件中搜索指定宽高的地址位置
    :param file_path: 二进制文件路径
    :param target_width: 目标宽度
    :param target_height: 目标高度
    :return: 匹配的地址列表
    """
    matches = []
    
    with open(file_path, 'rb') as f:
        data = f.read()
        
    # 遍历文件内容，从起点偏移开始，每次检查4字节（2字节宽度 + 2字节高度）
    for i in range(start_offset, len(data) - 3):
        # 读取2字节小端序宽度
        width = struct.unpack('<h', data[i:i+2])[0]
        # 读取接下来的2字节小端序高度
        height = struct.unpack('<h', data[i+2:i+4])[0]
        
        # 检查是否匹配目标宽高
        if width == target_width and height == target_height:
            # 同时存储原始地址和相对于起点偏移的偏移量
            matches.append( (i, i - start_offset) )
    
    return matches

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='在二进制文件中搜索指定宽高的地址位置')
    parser.add_argument('file_path', help='二进制文件路径')
    parser.add_argument('width', type=int, help='目标宽度')
    parser.add_argument('height', type=int, help='目标高度')
    # 自定义类型转换器，支持十进制和十六进制输入
    def auto_int(x):
        return int(x, 0)
    
    parser.add_argument('-s', '--start-offset', type=auto_int, default=0, help='搜索的起点偏移（支持十进制和十六进制，默认为0）')
    
    args = parser.parse_args()
    
    matches = search_width_height(args.file_path, args.width, args.height, args.start_offset)
    
    if matches:
        print(f'找到 {len(matches)} 处匹配:')
        for orig_addr, rel_offset in matches:
            print(f'原始地址: 0x{orig_addr:X} (十进制: {orig_addr})，相对偏移: 0x{rel_offset:X} (十进制: {rel_offset})')
    else:
        print('未找到匹配的宽高数据')