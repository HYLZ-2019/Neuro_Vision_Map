import json
import os
import sys
import pprint

from scripts.merge_coze_paper_list import merge_paper_list

# Add data directory to path to import paper_authors
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, '..', 'data')
sys.path.append(data_dir)

def get_score(entry):
	"""
	Calculate score for a paper entry.
	0: No authors or empty authors list.
	1: Has authors, but no institute info (all empty strings).
	2: Has authors and at least one institute info.
	"""
	if not entry:
		return 0
	
	authors = entry.get('authors')
	if not authors:
		return 0
	
	# Check if any author has institute info
	has_institute = False
	for author in authors:
		# author is expected to be [name, institute]
		if len(author) > 1 and author[1].strip():
			has_institute = True
			break
	
	if has_institute:
		return 2
	else:
		return 1

def main():
	# Paths
	log_file = os.path.join(current_dir, '..', 'raw', 'ss_ieee_author_log.txt')
	target_file = os.path.join(data_dir, 'paper_authors.py')

	# Load existing papers
	try:
		import data.paper_authors as pa_module
		# Make a deep copy or just use it. Since we are writing to file, modifying the list is fine.
		existing_papers = pa_module.paper_authors
	except ImportError:
		print("Could not import paper_authors. Starting with empty list.")
		existing_papers = []

	# Load new entries from log
	new_entries_map = {}
	if os.path.exists(log_file):
		with open(log_file, 'r', encoding='utf-8') as f:
			for line in f:
				line = line.strip()
				if not line:
					continue
				try:
					data = json.loads(line)
					if 'title' in data:
						# Construct entry strictly with title and authors
						entry = {
							'title': data['title'],
							'authors': data.get('authors', [])
						}
						new_entries_map[data['title']] = entry
				except json.JSONDecodeError:
					pass
	else:
		print(f"Log file not found: {log_file}")
		return

	# Create a map for existing papers to preserve order and allow updates
	# We use a list for the main storage to preserve order.
	# We use a dict to find index by title.
	title_to_index = {p['title']: i for i, p in enumerate(existing_papers)}
	
	updated_count = 0
	added_count = 0

	# Process new entries
	# The prompt implies we iterate over the NEW results and merge them in.
	for title, new_entry in new_entries_map.items():
		new_score = get_score(new_entry)
		
		if title in title_to_index:
			idx = title_to_index[title]
			old_entry = existing_papers[idx]
			old_score = get_score(old_entry)
			
			# Rule: If new >= old, use new.
			if new_score >= old_score:
				# Update
				existing_papers[idx] = new_entry
				updated_count += 1
		else:
			# New paper
			# Rule: "没有条目：0分". 
			# If new_score >= 0 (which is always true), we add it.
			existing_papers.append(new_entry)
			title_to_index[title] = len(existing_papers) - 1
			added_count += 1

	print(f"Updated {updated_count} entries.")
	print(f"Added {added_count} entries.")

	# Write back to paper_authors.py
	header = """# Every item in the list should be like:
# {"title": "Event-Anything: A great paper", "authors": [['Alice AA', 'Unversity of Alice'], ['Bob BB', 'University of BB; Company of BB']]},
# In which the institute field is ';'.join(multiple_institutes) if there are multiple institutes. For authors with unknown institutes, use empty string "".

paper_authors = """
	
	with open(target_file, 'w', encoding='utf-8') as f:
		f.write(header)
		f.write("[\n")
		for i, entry in enumerate(existing_papers):
			f.write("    " + repr(entry))
			if i < len(existing_papers) - 1:
				f.write(",")
			f.write("\n")
		f.write("]\n")

	merge_paper_list()

if __name__ == "__main__":
	main()
