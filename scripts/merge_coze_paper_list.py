import json
import ast
import os
import sys

# Add the project root to sys.path to allow imports from data and scripts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.paper_list import paper_list as existing_paper_list
from data.paper_authors import paper_authors as existing_paper_authors
from scripts.get_paper_list import get_new_paper_list

def merge_paper_list():
	new_papers = get_new_paper_list()
	if not new_papers:
		print("No new papers to merge.")
		return

	# Create a set of existing titles for fast lookup to avoid duplicates
	existing_titles = set(p[1] for p in existing_paper_list)
	
	papers_to_add = []
	for p in new_papers:
		if p[1] not in existing_titles:
			papers_to_add.append(p)
	
	if not papers_to_add:
		print("All new papers are already in the list.")
		return

	updated_paper_list = existing_paper_list + papers_to_add
	
	# Write back to data/paper_list.py
	file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'paper_list.py')
	
	with open(file_path, 'w', encoding='utf-8') as f:
		f.write("# Source, Title, conf/journal/book\n")
		f.write("paper_list = [\n")
		for item in updated_paper_list:
			f.write(f"    {repr(item)},\n")
		f.write("]\n")
	
	print(f"Added {len(papers_to_add)} papers to paper_list.py")

def merge_author_list():
	got_authors_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'raw', 'got_authors.txt')
	
	if not os.path.exists(got_authors_path):
		print("raw/got_authors.txt not found.")
		return

	new_authors_data = []
	with open(got_authors_path, 'r', encoding='utf-8') as f:
		for line in f:
			try:
				entry = json.loads(line.strip())
				title = entry['paper_title']
				authors_str = entry['authors']
				
				if authors_str == "failed":
					continue
				
				# Parse the string representation of the list
				# The string is like "[('Name', 'Institute', 'Email'), ...]"
				try:
					authors_list_raw = ast.literal_eval(authors_str)
					formatted_authors = []
					for author_tuple in authors_list_raw:
						# Take name and institute, ignore email/other info
						if len(author_tuple) >= 2:
							name = author_tuple[0]
							institute = author_tuple[1]
							if institute.lower() == "unknown":
								institute = ""
							formatted_authors.append([name, institute])
					
					new_authors_data.append({
						"title": title,
						"authors": formatted_authors
					})
				except Exception as e:
					print(f"Error parsing authors for {title}: {e}")
			except json.JSONDecodeError:
				continue

	if not new_authors_data:
		print("No valid author data found in got_authors.txt")
		return

	# Merge with existing
	existing_titles = set(item['title'] for item in existing_paper_authors)
	
	authors_to_add = []
	for item in new_authors_data:
		if item['title'] not in existing_titles:
			authors_to_add.append(item)
			existing_titles.add(item['title']) # Avoid duplicates within the new batch too if any
	
	if not authors_to_add:
		print("No new author entries to add.")
		return

	updated_paper_authors = authors_to_add + existing_paper_authors

	# Write back to data/paper_authors.py
	file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'paper_authors.py')
	
	with open(file_path, 'w', encoding='utf-8') as f:
		f.write("# Every item in the list should be like:\n")
		f.write("# {\"title\": \"Event-Anything: A great paper\", \"authors\": [['Alice AA', 'Unversity of Alice'], ['Bob BB', 'University of BB; Company of BB']]},\n")
		f.write("# In which the institute field is ';'.join(multiple_institutes) if there are multiple institutes. For authors with unknown institutes, use empty string \"\".\n")
		f.write("paper_authors = [\n")
		for item in updated_paper_authors:
			f.write(f"    {json.dumps(item, ensure_ascii=False)},\n")
		f.write("]\n")

	print(f"Added {len(authors_to_add)} entries to paper_authors.py")

if __name__ == "__main__":
	print("Merging paper list...")
	merge_paper_list()
	print("Merging author list...")
	merge_author_list()