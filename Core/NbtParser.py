import struct
import gzip
import sys
import os
from enum import IntEnum
from typing import BinaryIO, Dict, List, Any, Tuple, Union


class TagType(IntEnum):
    """NBT标签类型枚举"""
    TAG_End = 0
    TAG_Byte = 1
    TAG_Short = 2
    TAG_Int = 3
    TAG_Long = 4
    TAG_Float = 5
    TAG_Double = 6
    TAG_Byte_Array = 7
    TAG_String = 8
    TAG_List = 9
    TAG_Compound = 10
    TAG_Int_Array = 11
    TAG_Long_Array = 12


class NBTParser:
    """解析NBT文件并转换为SNBT格式的解析器"""
    
    def __init__(self, file_path: str, pretty_print=True):
        self.file_path = file_path
        self.pretty_print = pretty_print
        
    def parse(self) -> str:
        """解析NBT文件并返回SNBT格式字符串"""
        try:
            # 判断是否为gzip压缩文件
            with open(self.file_path, 'rb') as f:
                magic = f.read(2)
                f.seek(0)
                
                if magic == b'\x1f\x8b':  # gzip magic number
                    with gzip.open(f, 'rb') as gz_file:
                        return self._parse_nbt(gz_file)[1]
                else:
                    return self._parse_nbt(f)[1]
        except Exception as e:
            return f"解析错误: {str(e)}"
    
    def _parse_nbt(self, file: BinaryIO) -> Tuple[int, str]:
        """解析NBT数据并返回SNBT格式"""
        tag_type = self._read_byte(file)
        
        if tag_type == TagType.TAG_End:
            return tag_type, ""
            
        name_length = self._read_short(file)
        name = file.read(name_length).decode('utf-8')
        
        value = self._read_tag_value(file, tag_type, indent=0)
        
        # 如果是根复合标签，则直接返回其值，否则返回名称和值
        if name:
            return tag_type, f'{value}'
        else:
            return tag_type, f'{value}'
    
    def _read_tag_value(self, file: BinaryIO, tag_type: int, indent: int = 0) -> str:
        """根据标签类型读取并转换为SNBT格式"""
        if tag_type == TagType.TAG_End:
            return ""
        
        elif tag_type == TagType.TAG_Byte:
            value = self._read_byte(file)
            return f"{value}b"
        
        elif tag_type == TagType.TAG_Short:
            value = self._read_short(file)
            return f"{value}s"
        
        elif tag_type == TagType.TAG_Int:
            value = self._read_int(file)
            return f"{value}"
        
        elif tag_type == TagType.TAG_Long:
            value = self._read_long(file)
            return f"{value}L"
        
        elif tag_type == TagType.TAG_Float:
            value = self._read_float(file)
            # 如果是整数值，移除小数部分
            if value == int(value):
                return f"{int(value)}f"
            return f"{value}f"
        
        elif tag_type == TagType.TAG_Double:
            value = self._read_double(file)
            # 双精度数不添加后缀
            return f"{value}"
        
        elif tag_type == TagType.TAG_Byte_Array:
            length = self._read_int(file)
            values = [self._read_byte(file) for _ in range(length)]
            return f"[B;{','.join(f'{v}b' for v in values)}]"
        
        elif tag_type == TagType.TAG_String:
            length = self._read_short(file)
            value = file.read(length).decode('utf-8')
            # 转义特殊字符
            value = value.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{value}"'
        
        elif tag_type == TagType.TAG_List:
            list_type = self._read_byte(file)
            length = self._read_int(file)
            
            if length == 0:
                return "[]"
            
            if not self.pretty_print:
                items = []
                for _ in range(length):
                    items.append(self._read_tag_value(file, list_type, indent + 1))
                return f"[{','.join(items)}]"
            else:
                next_indent = indent + 2
                indent_str = ' ' * next_indent
                items = []
                for _ in range(length):
                    items.append(f"{indent_str}{self._read_tag_value(file, list_type, next_indent)}")
                
                # 添加缩进和换行
                return "[\n" + ",\n".join(items) + "\n" + (' ' * indent) + "]"
        
        elif tag_type == TagType.TAG_Compound:
            if not self.pretty_print:
                result = []
                
                while True:
                    child_type = self._read_byte(file)
                    if child_type == TagType.TAG_End:
                        break
                    
                    name_length = self._read_short(file)
                    name = file.read(name_length).decode('utf-8')
                    # 转义特殊字符
                    name = name.replace('\\', '\\\\').replace('"', '\\"')
                    
                    value = self._read_tag_value(file, child_type, indent + 1)
                    result.append(f'{name}:{value}')
                
                return f"{{{','.join(result)}}}"
            else:
                next_indent = indent + 2
                indent_str = ' ' * next_indent
                result = []
                
                while True:
                    child_type = self._read_byte(file)
                    if child_type == TagType.TAG_End:
                        break
                    
                    name_length = self._read_short(file)
                    name = file.read(name_length).decode('utf-8')
                    # 转义特殊字符
                    name = name.replace('\\', '\\\\').replace('"', '\\"')
                    
                    value = self._read_tag_value(file, child_type, next_indent)
                    result.append(f'{indent_str}{name}: {value}')
                
                if not result:
                    return "{}"
                
                # 添加缩进和换行
                return "{\n" + ",\n".join(result) + "\n" + (' ' * indent) + "}"
        
        elif tag_type == TagType.TAG_Int_Array:
            length = self._read_int(file)
            values = [self._read_int(file) for _ in range(length)]
            return f"[I;{','.join(str(v) for v in values)}]"
        
        elif tag_type == TagType.TAG_Long_Array:
            length = self._read_int(file)
            values = [self._read_long(file) for _ in range(length)]
            return f"[L;{','.join(f'{v}L' for v in values)}]"
        
        else:
            raise ValueError(f"未知标签类型: {tag_type}")
    
    def _read_byte(self, file: BinaryIO) -> int:
        return struct.unpack(">b", file.read(1))[0]
    
    def _read_short(self, file: BinaryIO) -> int:
        return struct.unpack(">h", file.read(2))[0]
    
    def _read_int(self, file: BinaryIO) -> int:
        return struct.unpack(">i", file.read(4))[0]
    
    def _read_long(self, file: BinaryIO) -> int:
        return struct.unpack(">q", file.read(8))[0]
    
    def _read_float(self, file: BinaryIO) -> float:
        return struct.unpack(">f", file.read(4))[0]
    
    def _read_double(self, file: BinaryIO) -> float:
        return struct.unpack(">d", file.read(8))[0]


def main():
    """主函数，处理命令行参数并执行转换"""
    if len(sys.argv) < 2:
        print("用法: python NbtParser.py <nbt文件路径> [输出文件路径] [--no-pretty-print]")
        return
    
    input_file = sys.argv[1]
    pretty_print = True
    output_file = None
    
    # 处理参数
    for arg in sys.argv[2:]:
        if arg == "--no-pretty-print":
            pretty_print = False
        elif not output_file:  # 第一个非选项参数作为输出文件
            output_file = arg
    
    # 如果没有指定输出文件名
    if not output_file:
        # 默认输出文件名为输入文件名加上.snbt扩展名
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}.snbt"
    
    parser = NBTParser(input_file, pretty_print=pretty_print)
    snbt_data = parser.parse()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(snbt_data)
    
    print(f"转换完成！SNBT数据已保存至 {output_file}")


if __name__ == "__main__":
    main()