from data.paper_authors import paper_authors
from data.institutes_alias_to_name import get_inst_name as institutes_alias_to_name
import os

all_author_insts = set()
for paper in paper_authors:
	for author in paper['authors']:
		inst = author[1].strip()
		if inst:
			insts = [s.strip() for s in inst.split(';') if s.strip()]
			for i in insts:
				all_author_insts.add(i)

all_mapped_insts = set(institutes_alias_to_name.keys()) | set(institutes_alias_to_name.values())

unmapped_insts = sorted(list(all_author_insts - all_mapped_insts))

if unmapped_insts:
    print(f"Found {len(unmapped_insts)} unmapped institutes.")
    file_path = os.path.join('data', 'institutes_alias_to_name.py')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the closing brace
    closing_brace_index = -1
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == '}':
            closing_brace_index = i
            break
            
    if closing_brace_index != -1:
        # Check if the previous non-empty line has a comma
        prev_index = closing_brace_index - 1
        while prev_index >= 0 and not lines[prev_index].strip():
            prev_index -= 1
            
        if prev_index >= 0:
            last_content_line = lines[prev_index].rstrip()
            if not last_content_line.endswith(','):
                lines[prev_index] = last_content_line + ",\n"
        
        new_lines = []
        for inst in unmapped_insts:
            safe_inst = inst.replace('"', '\\"')
            new_lines.append(f'    "{safe_inst}": "TODO",\n')
            
        lines[closing_brace_index:closing_brace_index] = new_lines
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("Updated data/institutes_alias_to_name.py")
    else:
        print("Could not find closing brace in data/institutes_alias_to_name.py")
else:
    print("No unmapped institutes found.")
