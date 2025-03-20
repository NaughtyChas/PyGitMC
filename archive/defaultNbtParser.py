#!/usr/bin/env python3
import sys
import os
import json
import nbtlib
import re

def read_nbt_file(filepath, little_endian):
    """
    Load an NBT file using nbtlib with the given endianness.
    """
    try:
        byteorder = 'little' if little_endian else 'big'
        nbt_file = nbtlib.load(filepath, byteorder=byteorder)
        return nbt_file
    except Exception as e:
        raise e

def convert_nbt_to_special_json(nbt_data):
    """
    Convert NBT data to a format that preserves type information in the exact format required
    """
    if isinstance(nbt_data, nbtlib.tag.Byte):
        return f"{int(nbt_data)}b"
    elif isinstance(nbt_data, nbtlib.tag.Short):
        return f"{int(nbt_data)}s"
    elif isinstance(nbt_data, nbtlib.tag.Int):
        return int(nbt_data)
    elif isinstance(nbt_data, nbtlib.tag.Long):
        return f"{int(nbt_data)}L"
    elif isinstance(nbt_data, nbtlib.tag.Float):
        # Optimize float formatting to remove trailing .0 for whole numbers
        float_val = float(nbt_data)
        if float_val == int(float_val):
            return f"{int(float_val)}f"
        else:
            return f"{float_val}f"
    elif isinstance(nbt_data, nbtlib.tag.Double):
        return float(nbt_data)
    elif isinstance(nbt_data, nbtlib.tag.String):
        return str(nbt_data)
    elif isinstance(nbt_data, nbtlib.tag.ByteArray):
        # No spaces after commas in byte arrays
        return f"[B;{','.join(str(int(b)) for b in nbt_data)}]"
    elif isinstance(nbt_data, nbtlib.tag.IntArray):
        # No spaces after commas in int arrays
        return f"[I;{','.join(str(int(i)) for i in nbt_data)}]"
    elif isinstance(nbt_data, nbtlib.tag.LongArray):
        # No spaces after commas in long arrays
        return f"[L;{','.join(str(int(l)) for l in nbt_data)}]"
    elif isinstance(nbt_data, nbtlib.tag.List):
        return [convert_nbt_to_special_json(item) for item in nbt_data]
    elif isinstance(nbt_data, nbtlib.tag.Compound):
        return {k: convert_nbt_to_special_json(v) for k, v in nbt_data.items()}
    elif isinstance(nbt_data, dict):
        return {k: convert_nbt_to_special_json(v) for k, v in nbt_data.items()}
    elif isinstance(nbt_data, list):
        return [convert_nbt_to_special_json(item) for item in nbt_data]
    else:
        return nbt_data

class NBTEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that preserves the special notation for NBT types
    """
    def encode(self, obj):
        # Handle special NBT types
        if isinstance(obj, str):
            # Check if it's a special NBT type
            if re.match(r'^-?\d+\.?\d*[bsfL]$', obj):
                return obj
            # Check if it's an array notation [B;...], [I;...], [L;...]
            elif obj.startswith('[') and obj[1] in 'BIL' and obj[2] == ';':
                return obj
        return super().encode(obj)

    def iterencode(self, obj, _one_shot=False):
        """
        Override iterencode to handle NBT-specific formatting
        """
        # Special handling for our NBT types
        if isinstance(obj, str):
            if any(obj.endswith(suffix) for suffix in ['b', 's', 'L', 'f']):
                yield obj
                return
            elif obj.startswith('[') and obj[1] in 'BIL' and obj[2] == ';':
                yield obj
                return
            # Normal string
            yield from super().iterencode(obj, _one_shot)
            return
            
        # Let the parent handle everything else
        yield from super().iterencode(obj, _one_shot)

def remove_quotes_from_keys(json_text):
    """
    Post-process JSON text to remove quotes from keys to match NBT format
    Also remove quotes from special NBT type values
    """
    # Remove quotes around keys
    json_text = re.sub(r'"([^"]+)":', r'\1:', json_text)
    
    # Remove quotes around byte, short, long values (e.g., "123b" -> 123b)
    json_text = re.sub(r': "(-?\d+[bsL])"', r': \1', json_text)
    
    # Remove quotes around float values (e.g., "1.23f" -> 1.23f)
    json_text = re.sub(r': "(-?\d+\.?\d*f)"', r': \1', json_text)
    
    # Remove quotes around array notation [B;...], [I;...], [L;...]
    json_text = re.sub(r': "(\[[BIL];[^"]*])"', r': \1', json_text)
    
    # Remove quotes around array values (e.g., "[1,2,3]" -> [1,2,3])
    json_text = re.sub(r'"(-?\d+\.?\d*f)"', r'\1', json_text)
    
    return json_text

def fix_array_spacing(json_text):
    """
    Fix spacing in array notations to match SNBT format
    """
    # Fix spacing in typed arrays [B;...], [I;...], [L;...]
    for array_type in ['B', 'I', 'L']:
        pattern = f'\\[{array_type};(.*?)\\]'
        for match in re.finditer(pattern, json_text):
            array_content = match.group(1)
            # Remove all spaces in array content
            clean_content = re.sub(r'\s+', '', array_content)
            json_text = json_text.replace(f"[{array_type};{array_content}]", f"[{array_type};{clean_content}]")
    
    # Fix spacing in regular arrays
    json_text = re.sub(r'\[\s+', r'[', json_text)  # Remove space after opening bracket
    json_text = re.sub(r'\s+\]', r']', json_text)  # Remove space before closing bracket
    
    return json_text

def save_nbt_to_json(nbt_data, output_path):
    """
    Save the parsed NBT data to a JSON file with the correct SNBT format
    """
    try:
        # Convert the NBT data to our special JSON format
        json_data = convert_nbt_to_special_json(nbt_data)
        
        # First, convert to JSON with standard formatting
        json_str = json.dumps(json_data, cls=NBTEncoder, indent=2, ensure_ascii=False, separators=(',', ': '))
        
        # Post-process to remove quotes from keys and special type values
        formatted_str = remove_quotes_from_keys(json_str)
        
        # Fix array spacings
        formatted_str = fix_array_spacing(formatted_str)
        
        # Further format adjustments to match original exactly
        lines = formatted_str.splitlines()
        formatted_lines = []
        
        # Stack to track the current nesting structure (compound or list)
        context_stack = []
        
        # Process each line
        for i, line in enumerate(lines):
            # Get stripped content and count leading spaces
            content = line.strip()
            leading_spaces = len(line) - len(line.lstrip())
            indent_level = leading_spaces // 2
            
            # Update nesting context
            if content.endswith('{'):
                context_stack.append('compound')
            elif content.endswith('[') and not any(content.startswith(f'[{t};') for t in 'BIL'):
                context_stack.append('list')
            elif content == '}' and context_stack and context_stack[-1] == 'compound':
                context_stack.pop()
            elif content == ']' and context_stack and context_stack[-1] == 'list':
                context_stack.pop()
            
            # Apply spacing rules based on context
            current_context = context_stack[-1] if context_stack else None
            
            # First line special case (no indent)
            if i == 0 and content == '{':
                formatted_lines.append(content)
                continue
                
            # Handle empty objects/arrays
            if (content == '}' or content == ']') and i > 0:
                prev_line = formatted_lines[-1].rstrip()
                if prev_line.endswith('{') or prev_line.endswith('['):
                    # Empty object/array - keep on same line
                    formatted_lines[-1] = f"{prev_line}{content}"
                    continue
            
            # Apply standard indentation
            indent_spaces = indent_level * 2
            
            # Special case for items in lists
            if current_context == 'list' and content.startswith('{'):
                # Objects in lists need consistent spacing
                formatted_lines.append(' ' * indent_spaces + content)
            else:
                formatted_lines.append(' ' * indent_spaces + content)
        
        # Join lines and apply final formatting fixes
        final_output = '\n'.join(formatted_lines)
        
        # Ensure consistent spacing around colons
        final_output = re.sub(r'(\w+)\s*:\s*', r'\1: ', final_output)
        
        # Ensure no spaces between value and type suffix (e.g. "1 b" -> "1b")
        final_output = re.sub(r'(\d+)\s+([bsfL])', r'\1\2', final_output)
        
        # Fix spaces in simple lists (for better readability)
        final_output = re.sub(r',\s+(-?\d+[bsfL]?)', r', \1', final_output)
        
        # Compact small lists on one line if appropriate
        final_output = re.sub(r'\[\s*(-?\d+[bsfL]?),\s*(-?\d+[bsfL]?)\s*\]', r'[\1, \2]', final_output)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_output)
            
        print(f"Parsed data saved to {output_path}")
        return True
    except Exception as e:
        print(f"Failed to save parsed data: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: {} <nbt_file>".format(sys.argv[0]))
        sys.exit(1)

    filepath = sys.argv[1]
    
    if not os.path.isfile(filepath):
        print(f"Error: File does not exist: {filepath}")
        sys.exit(1)
    
    # Skip region files which are handled differently
    if filepath.endswith('.mca'):
        print("Error: Region files (.mca) are not handled by this script.")
        sys.exit(1)
    
    # Default to Big Endian for most Minecraft files
    little_endian = filepath.endswith('.mcstructure')
    
    try:
        nbt_file = read_nbt_file(filepath, little_endian)
        # Try again with the opposite endianness if the file appears to be empty
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
        # If an error occurred, try with the opposite endianness
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
    
    # Generate output filename by appending .json to the original filename
    output_path = filepath + '.json'
    
    # Save the parsed data to the output file
    if not save_nbt_to_json(nbt_file, output_path):
        sys.exit(1)
    
if __name__ == "__main__":
    main()