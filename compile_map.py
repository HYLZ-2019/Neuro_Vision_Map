import json
import re
from data.paper_list import paper_list
from data.paper_authors import paper_authors
from data.institutes_alias_to_name import get_inst_name
from data.institute_info import institute_info
from data.research_groups import research_groups

def make_map():
	paper_info_list = []
	# Each item in paper_info_list is: [title, year(2025), source(CVPR), [list of related institutes]]

	authors_of_institute = {}
	# key: institute name
	# value: set of author names

	paper_title_to_authors = {}
	for paper in paper_authors:
		paper_title_to_authors[paper['title']] = paper['authors']

	papers_per_author = {}

	for paper in paper_list:
		year_source = paper[0]
		title = paper[1]
		# Find digits such as '2025' in year_source; parse it out. Strip the remaining part to be the source.
		year_match = re.search(r'20\d{2}', year_source)
		if year_match:
			year = year_match.group(0)
			source = year_source.replace(year_match.group(0), '').strip()
		else:
			year = "unknown"
			source = year_source.strip()
		if title in paper_title_to_authors:
			authors = paper_title_to_authors[title]
		else:
			print("Warning: paper title not found in paper_authors:", title)
			authors = []
		
		related_institutes = set()
		for author, institute in authors:
			papers_per_author[author] = papers_per_author.get(author, 0) + 1
			if institute != "" and institute.lower() != "unknown":
				# Some authors may have multiple institutes separated by ';'
				multiple_insts = [inst.strip() for inst in institute.split(';') if inst.strip()]
				for inst in multiple_insts:
					if inst in get_inst_name:				
						standard_inst_name = get_inst_name[inst]
					else:
						standard_inst_name = inst
					related_institutes.add(standard_inst_name)
					if standard_inst_name not in authors_of_institute:
						authors_of_institute[standard_inst_name] = set()
					authors_of_institute[standard_inst_name].add(author)
		related_institutes = list(related_institutes)
		paper_info_list.append([title, year, source, related_institutes])

	# Count how many papers were in each source; for sources with papers < 10, change the source to "others"
	source_count = {}
	for paper in paper_info_list:
		source = paper[2]
		if source not in source_count:
			source_count[source] = 0
		source_count[source] += 1
	for paper in paper_info_list:
		source = paper[2]
		if source_count[source] < 10 or source == "":
			paper[2] = "others"
	
	# Convert authors_of_institute sets to lists
	for inst in authors_of_institute:
		authors_of_institute[inst] = list(authors_of_institute[inst])
		# Sort them by number of papers they authored (descending)
		authors_of_institute[inst].sort(key=lambda author: papers_per_author.get(author, 0), reverse=True)

	return paper_info_list, authors_of_institute, institute_info, research_groups


def inject_data_to_template(template_name="template_map.html", output_name="result_map.html"):
	"""Read template file and inject data"""
	paper_info_list, authors_of_institute, institute_info, research_groups = make_map()
	
	# Read template file
	template_path = f"templates/{template_name}"
	try:
		with open(template_path, 'r', encoding='utf-8') as f:
			template_content = f.read()
	except FileNotFoundError:
		print(f"Error: Template file '{template_path}' not found")
		return False
	
	# Read CSS file
	css_path = "templates/map_style.css"
	try:
		with open(css_path, 'r', encoding='utf-8') as f:
			css_content = f.read()
	except FileNotFoundError:
		print(f"Error: CSS file '{css_path}' not found")
		return False
	
	# Replace external CSS link with inline style
	css_link = '<link rel="stylesheet" type="text/css" href="../map_style.css">'
	inline_css = f'<style>\n{css_content}\n</style>'
	template_content = template_content.replace(css_link, inline_css)
	
	# Convert data to JSON strings
	paper_info_json = json.dumps(paper_info_list, ensure_ascii=False, separators=(',', ':'))
	authors_of_institute_json = json.dumps(authors_of_institute, ensure_ascii=False, separators=(',', ':'))
	institute_info_json = json.dumps(institute_info, ensure_ascii=False, separators=(',', ':'))
	research_groups_json = json.dumps(research_groups, ensure_ascii=False, separators=(',', ':'))
	
	# Replace placeholders with actual data
	html_content = template_content.replace('[[INJECT_PAPER_INFO_LIST_HERE]]', paper_info_json)
	html_content = html_content.replace('[[INJECT_AUTHORS_OF_INSTITUTE_HERE]]', authors_of_institute_json)
	html_content = html_content.replace('[[INJECT_INSTITUTE_INFO_HERE]]', institute_info_json)
	html_content = html_content.replace('[[INJECT_RESEARCH_GROUPS_HERE]]', research_groups_json)
	
	# Write result to output file
	try:
		with open(output_name, 'w', encoding='utf-8') as f:
			f.write(html_content)
		print(f"Successfully generated '{output_name}'")
		return True
	except Exception as e:
		print(f"Error writing output file: {e}")
		return False


if __name__ == "__main__":
	inject_data_to_template("template_map.html", "result_map.html")