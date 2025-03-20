#!/usr/bin/env python3
import sys
import os
import json
import nbtlib

def read_nbt_file(filepath, little_endian):
    """
    Load an NBT file using nbtlib with the given endianness.
    """
    try:
        # nbtlib.load uses byteorder parameter instead of little_endian
        byteorder = 'little' if little_endian else 'big'
        nbt_file = nbtlib.load(filepath, byteorder=byteorder)
        return nbt_file
    except Exception as e:
        raise e

def nbt_to_json_serializable(nbt_data):
    """
    Convert NBT data to JSON serializable Python objects.
    """
    if isinstance(nbt_data, (nbtlib.tag.Int, nbtlib.tag.Float, nbtlib.tag.Double, 
                            nbtlib.tag.Short, nbtlib.tag.Byte, nbtlib.tag.Long)):
        return nbt_data.real
    elif isinstance(nbt_data, nbtlib.tag.String):
        return str(nbt_data)
    elif isinstance(nbt_data, nbtlib.tag.IntArray):
        return [i for i in nbt_data]
    elif isinstance(nbt_data, nbtlib.tag.ByteArray):
        return [b for b in nbt_data]
    elif isinstance(nbt_data, nbtlib.tag.LongArray):
        return [l for l in nbt_data]
    elif isinstance(nbt_data, nbtlib.tag.List):
        return [nbt_to_json_serializable(item) for item in nbt_data]
    elif isinstance(nbt_data, nbtlib.tag.Compound):
        return {k: nbt_to_json_serializable(v) for k, v in nbt_data.items()}
    elif isinstance(nbt_data, dict):
        return {k: nbt_to_json_serializable(v) for k, v in nbt_data.items()}
    elif isinstance(nbt_data, list):
        return [nbt_to_json_serializable(item) for item in nbt_data]
    else:
        return nbt_data

def save_nbt_to_text(nbt_data, output_path):
    """
    Save the parsed NBT data to a text file in a readable format.
    """
    try:
        # Convert NBT data to JSON-serializable format
        json_compatible_data = nbt_to_json_serializable(nbt_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Convert to JSON with proper indentation
            json_data = json.dumps(json_compatible_data, indent=2)
            f.write(json_data)
        print(f"Parsed data saved to {output_path}")
    except Exception as e:
        print(f"Failed to save parsed data: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: {} <nbt_file>".format(sys.argv[0]))
        sys.exit(1)

    filepath = sys.argv[1]
    
    if not os.path.isfile(filepath):
        print(f"File does not exist: {filepath}")
        sys.exit(1)
    
    # Skip region files which are handled differently.
    if filepath.endswith('.mca'):
        print("Region files (.mca) are not handled by this script.")
        sys.exit(1)
    
    # For files like level.dat (and any non-.mcstructure), little_endian defaults to False,
    # meaning Big Endian parsing is used.
    little_endian = filepath.endswith('.mcstructure')
    
    try:
        nbt_file = read_nbt_file(filepath, little_endian)
        # If initial read is in Big Endian mode (little_endian=False) and the root appears empty,
        # try reading again with little_endian set to True.
        if not little_endian and len(nbt_file) == 0:
            try:
                new_file = read_nbt_file(filepath, True)
                if len(new_file) > 0:
                    little_endian = True
                    nbt_file = new_file
                    print("Re-read with byteorder='little' because the initial read returned an empty root.")
            except Exception as inner_err:
                print("Retry with byteorder='little' failed:", inner_err)
    except Exception as e:
        # If an error occurred, try with the opposite endianness.
        print("Initial parse error:", e)
        try:
            little_endian = not little_endian
            nbt_file = read_nbt_file(filepath, little_endian)
            print("Parsed successfully after switching endianness.")
        except Exception as e2:
            print("Failed to parse the NBT file:", e2)
            sys.exit(1)
    
    print("Parsed NBT file successfully with byteorder =", 'little' if little_endian else 'big')
    print("Root Compound Keys:", list(nbt_file.keys()))
    
    # Generate output filename by appending .txt to the original filename
    output_path = filepath + '.json'
    
    # Save the parsed data to the output file
    save_nbt_to_text(nbt_file, output_path)
    
if __name__ == "__main__":
    main()