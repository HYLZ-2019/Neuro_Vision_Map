import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from data.institute_info import institute_info
from data.institutes_alias_to_name import get_inst_name
import json

def main():
    missing_count = 0
    # Collect all unique target names from the alias map
    target_names = set(get_inst_name.values())
    
    for name in target_names:
        if name not in institute_info:
            print(f"Adding missing institute: {name}")
            institute_info[name] = {'lat': 0, 'lon': 0, 'country': 'unknown'}
            missing_count += 1
            
    if missing_count == 0:
        print("No missing institutes found.")
        return

    print(f"Total missing institutes added: {missing_count}")

    # Write back to data/institute_info.py
    file_path = os.path.join(project_root, 'data', 'institute_info.py')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("# Institute information including latitude, longitude, country, etc.\n")
        f.write("institute_info = {\n")
        # Write keys in insertion order (existing first, then new ones)
        for key, val in institute_info.items():
            f.write(f"    {repr(key)}: {repr(val)},\n")
        f.write("}\n")
    
    print(f"Successfully updated {file_path}")

if __name__ == "__main__":
    main()
