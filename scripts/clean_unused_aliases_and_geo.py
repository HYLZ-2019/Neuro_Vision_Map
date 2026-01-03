import sys
import os
import re

# Add parent directory to sys.path to allow importing from data
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from data.paper_authors import paper_authors
from data.institutes_alias_to_name import get_inst_name

def clean_unused_aliases():
    # 1. Identify unused aliases
    unused_aliases = set(get_inst_name.keys())
    
    print(f"Total aliases before cleaning: {len(unused_aliases)}")

    for paper in paper_authors:
        for author, institute in paper['authors']:
            if institute != "" and institute.lower() != "unknown":
                # Some authors may have multiple institutes separated by ';'
                multiple_insts = [inst.strip() for inst in institute.split(';') if inst.strip()]
                for inst in multiple_insts:
                    if inst in get_inst_name:
                        # This alias is used
                        if inst in unused_aliases:
                            unused_aliases.remove(inst)

    print(f"Number of unused aliases to remove: {len(unused_aliases)}")

    # 2. Read the file and filter lines
    file_path = os.path.join(parent_dir, "data", "institutes_alias_to_name.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    # Regex to match lines like: "Alias": "Name", or 'Alias': 'Name',
    # It handles optional comma and comments at the end
    alias_pattern = re.compile(r'^\s*(["\'])(.+?)\1\s*:\s*(["\'])(.+?)\3,?\s*(#.*)?$')
    
    removed_count = 0
    
    for line in lines:
        match = alias_pattern.match(line)
        if match:
            alias = match.group(2)
            if alias in unused_aliases:
                removed_count += 1
                continue # Skip this line
        
        new_lines.append(line)

    print(f"Removed {removed_count} lines.")

    # 3. Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"Successfully updated {file_path}")

    # 4. Clean institute_info.py
    # Calculate used target names
    used_targets = set()
    for alias in get_inst_name:
        if alias not in unused_aliases:
            used_targets.add(get_inst_name[alias])
            
    print(f"Total used institute targets: {len(used_targets)}")
    
    info_file_path = os.path.join(parent_dir, "data", "institute_info.py")
    with open(info_file_path, 'r', encoding='utf-8') as f:
        info_lines = f.readlines()
        
    new_info_lines = []
    # Regex for institute_info lines: "Name": { ... },
    # Matches start of line, quote, name, quote, colon, anything
    # We use a slightly loose regex to capture the key
    info_pattern = re.compile(r'^\s*(["\'])(.+?)\1\s*:\s*\{')
    
    removed_info_count = 0
    for line in info_lines:
        match = info_pattern.match(line)
        if match:
            name = match.group(2)
            # If the name is not in used_targets, we remove it
            if name not in used_targets:
                removed_info_count += 1
                continue
        new_info_lines.append(line)
        
    print(f"Removed {removed_info_count} lines from institute_info.py")
    
    with open(info_file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_info_lines)
        
    print(f"Successfully updated {info_file_path}")

if __name__ == "__main__":
    clean_unused_aliases()
