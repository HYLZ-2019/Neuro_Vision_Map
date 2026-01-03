import sys
import os

# Add parent directory to path to allow importing from data
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data import paper_authors as paper_authors_module
from data import paper_list as paper_list_module
from data import institute_info as institute_info_module
from data import institutes_alias_to_name as institutes_alias_to_name_module
from data import research_groups as research_groups_module

def get_header(file_path):
    header_lines = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith('#') or stripped == '':
                header_lines.append(line)
            else:
                break
    # Remove trailing empty lines
    while header_lines and header_lines[-1].strip() == '':
        header_lines.pop()
    return "".join(header_lines)

def write_file(file_path, variable_name, data, header):
    with open(file_path, 'w', encoding='utf-8') as f:
        if header:
            f.write(header)
            f.write('\n\n')
        
        if isinstance(data, list):
            f.write(f"{variable_name} = [\n")
            for item in data:
                f.write(f"    {repr(item)},\n")
            f.write("]\n")
        elif isinstance(data, dict):
            f.write(f"{variable_name} = {{\n")
            for key in data:
                f.write(f"    {repr(key)}: {repr(data[key])},\n")
            f.write("}\n")

def reformat_paper_authors():
    file_path = os.path.join(os.path.dirname(__file__), '../data/paper_authors.py')
    header = get_header(file_path)
    data = paper_authors_module.paper_authors
    write_file(file_path, 'paper_authors', data, header)
    print(f"Reformatted {file_path}")

def reformat_paper_list():
    file_path = os.path.join(os.path.dirname(__file__), '../data/paper_list.py')
    header = get_header(file_path)
    data = paper_list_module.paper_list
    write_file(file_path, 'paper_list', data, header)
    print(f"Reformatted {file_path}")

def reformat_institute_info():
    file_path = os.path.join(os.path.dirname(__file__), '../data/institute_info.py')
    header = get_header(file_path)
    data = institute_info_module.institute_info
    write_file(file_path, 'institute_info', data, header)
    print(f"Reformatted {file_path}")

def reformat_institutes_alias_to_name():
    file_path = os.path.join(os.path.dirname(__file__), '../data/institutes_alias_to_name.py')
    header = get_header(file_path)
    data = institutes_alias_to_name_module.get_inst_name
    write_file(file_path, 'get_inst_name', data, header)
    print(f"Reformatted {file_path}")

def reformat_research_groups():
    file_path = os.path.join(os.path.dirname(__file__), '../data/research_groups.py')
    header = get_header(file_path)
    data = research_groups_module.research_groups
    write_file(file_path, 'research_groups', data, header)
    print(f"Reformatted {file_path}")

if __name__ == '__main__':
    reformat_paper_authors()
    reformat_paper_list()
    reformat_institute_info()
    reformat_institutes_alias_to_name()
    reformat_research_groups()
