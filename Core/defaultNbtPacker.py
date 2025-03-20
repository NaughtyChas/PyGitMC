#!/usr/bin/env python3
import sys
import os
import json
import nbtlib
from nbtlib import tag

def convert_json_to_nbt_tags(json_data):
    """
    Convert JSON data structure to NBT tags recursively
    """
    if isinstance(json_data, dict):
        return tag.Compound({k: convert_json_to_nbt_tags(v) for k, v in json_data.items()})
    elif isinstance(json_data, list):
        # This is a simplification - in a real app you would need more
        # sophisticated detection of what kind of array it is
        if json_data and all(isinstance(x, int) for x in json_data):
            # Check value ranges to determine appropriate array type
            max_val = max(abs(x) for x in json_data) if json_data else 0
            if max_val <= 127:
                return tag.ByteArray(json_data)
            elif max_val <= 2147483647:
                return tag.IntArray(json_data)
            else:
                return tag.LongArray(json_data)
        return tag.List([convert_json_to_nbt_tags(item) for item in json_data])
    elif isinstance(json_data, bool):
        return tag.Byte(1 if json_data else 0)
    elif isinstance(json_data, int):
        if -128 <= json_data <= 127:
            return tag.Byte(json_data)
        elif -32768 <= json_data <= 32767:
            return tag.Short(json_data)
        elif -2147483648 <= json_data <= 2147483647:
            return tag.Int(json_data)
        else:
            return tag.Long(json_data)
    elif isinstance(json_data, float):
        return tag.Float(json_data)
    elif isinstance(json_data, str):
        return tag.String(json_data)
    elif json_data is None:
        return tag.String("")
    else:
        raise TypeError(f"Unsupported type: {type(json_data)}")

def should_use_gzip(filepath):
    """
    Determine if gzip compression should be used based on the file extension.
    Most Minecraft NBT files use gzip compression, except for a few specific types.
    """
    # Files that don't use gzip compression
    non_gzipped_extensions = ['.mcstructure']
    
    # Check if the file has any of the extensions that don't use gzip
    for ext in non_gzipped_extensions:
        if filepath.endswith(ext):
            return False
    
    # Default to using gzip compression for most NBT files
    return True

def json_to_nbt(json_path, nbt_path, little_endian=False):
    """
    Convert a JSON file back to NBT format
    """
    try:
        # Read JSON file
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Convert JSON to NBT
        nbt_data = convert_json_to_nbt_tags(json_data)
        
        # Create NBT file
        # In nbtlib, File is a dict subclass that represents the root tag
        nbt_file = nbtlib.File(nbt_data)
        
        # Determine if gzip compression should be used
        use_gzip = should_use_gzip(nbt_path)
        
        # Write to file
        byteorder = 'little' if little_endian else 'big'
        nbt_file.save(nbt_path, gzipped=use_gzip, byteorder=byteorder)
        
        compression_info = "with gzip compression" if use_gzip else "uncompressed"
        print(f"Successfully packed {json_path} to {nbt_path} ({compression_info})")
        return True
        
    except Exception as e:
        print(f"Error packing NBT file: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: {} <json_file>".format(sys.argv[0]))
        sys.exit(1)
        
    json_path = sys.argv[1]
    
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        sys.exit(1)
        
    if not json_path.endswith('.json'):
        print("Input file must have .json extension")
        sys.exit(1)
    
    # Generate output filename by removing .json extension
    nbt_path = json_path[:-5]  # Remove .json suffix
    
    # Determine endianness based on file extension
    little_endian = nbt_path.endswith('.mcstructure')
    
    # Convert and save
    if json_to_nbt(json_path, nbt_path, little_endian):
        # Compare file sizes
        original_size = os.path.getsize(nbt_path)
        json_size = os.path.getsize(json_path)
        print(f"Original NBT file size: {original_size:,} bytes")
        print(f"Source JSON file size: {json_size:,} bytes")
        print("Conversion successful!")
    else:
        print("Conversion failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()