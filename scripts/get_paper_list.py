from data.paper_list import paper_list
import csv

def get_raw_paper_list(csv_file):
	# 对于csv文件里的每一行，尝试parse第一列和第二列。如果第一列类似于TVLSI 2025或者Nature Comput Sci 2025，也就是说.split(" ")[-1]是4位数字，那么就把第一列作为source，第二列作为paper title. 返回一个list of tuples (source, title)
	raw_paper_list = []
	with open(csv_file, "r", encoding="utf-8") as f:
		for line in f:
			parts = next(csv.reader([line.strip()]))
			if len(parts) < 2:
				continue
			source_candidate = parts[0].strip()
			title = parts[1].strip() # "c" or "j"
			if len(parts) > 4:
				c_or_j = parts[4].strip()
			else:
				c_or_j = ""

			if len(source_candidate.split(" ")) >= 2 and source_candidate.split(" ")[-1].isdigit() and len(source_candidate.split(" ")[-1]) == 4:
				source = source_candidate
				raw_paper_list.append((source, title, c_or_j))
	return raw_paper_list

def get_new_paper_list():
	raw_paper_list = get_raw_paper_list("raw/paper_list_2026_01_02.csv")
	already_in_data = set((source, title) for source, title, _ in paper_list)
	new_papers = []
	for source, title, c_or_j in raw_paper_list:
		if (source, title) not in already_in_data:
			new_papers.append((source, title, c_or_j))
	return new_papers


if __name__ == "__main__":
	new_papers = get_new_paper_list()
	print(f"Found {len(new_papers)} new papers.")