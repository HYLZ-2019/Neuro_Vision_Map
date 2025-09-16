import json
import os
import csv
import re
from data.institutes_alias_to_name import get_inst_name

def convert_paper_list():

	csv_path = os.path.join(os.path.dirname(__file__), '../data/paper_list.csv')
	py_path = os.path.join(os.path.dirname(__file__), '../data/paper_list.py')

	with open(csv_path, 'r', encoding='utf-8') as f:
		reader = csv.reader(f)
		rows = list(reader)

	# 跳过表头
	data_rows = rows[1:]

	with open(py_path, 'w', encoding='utf-8') as f:
		f.write('# Source, Title, conf/journal/book\n')
		f.write('paper_list = [\n')
		for row in data_rows:
			# 转义双引号
			row_escaped = [str(item).replace('"', '\"') for item in row]
			f.write(f'    {row_escaped},\n')
		f.write(']\n')

def convert_paper_authors():
	'''
	data/got_info.txt里的每一行类似于：
	{"title": "ESVO2: Direct Visual-Inertial Odometry with Stereo Event Cameras", "info": [["Junkai Niu", "unknown", "unknown"], ["Sheng Zhong", "unknown", "unknown"], ["Xiuyuan Lu", "unknown", "unknown"], ["Shaojie Shen", "unknown", "unknown"], ["Guillermo Gallego", "unknown", "unknown"], ["Yi Zhou", "unknown", "unknown"]]}
	其中info里的每个元素是一个作者信息，三个字段分别是姓名、机构、邮箱。
	产生data/paper_authors.py，内容类似于：
	paper_authors = [
	{"title": "ESVO2: Direct Visual-Inertial Odometry with Stereo Event Cameras", "authors": [["Junkai Niu", "institute_1"], ["Sheng Zhong", "institute_2"], ...]},
	...
	]
	'''

	txt_path = os.path.join(os.path.dirname(__file__), '../data/got_info.txt')
	py_path = os.path.join(os.path.dirname(__file__), '../data/paper_authors.py')

	# 读取所有行并解析JSON
	paper_authors = []
	institute_map = {}  # 用于映射机构名称到编号
	institute_counter = 1

	with open(txt_path, 'r', encoding='utf-8') as f:
		for line in f:
			line = line.strip()
			if not line:
				continue
			
			try:
				data = json.loads(line)
				title = data.get('title', '')
				info = data.get('info', [])
				authors = []
				for inf in info:
					name = inf[0]
					institute = inf[1]
					if institute is None or institute.lower() == "unknown":
						institute = ""
					authors.append([name, institute])
				paper_authors.append({
					"title": title,
					"authors": authors
				})
			except json.JSONDecodeError:
				print(f"Warning: Could not parse line: {line[:100]}...")
				continue

	# 写入Python文件
	with open(py_path, 'w', encoding='utf-8') as f:
		
		f.write('''# Every item in the list should be like:
# {"title": "Event-Anything: A great paper", "authors": [['Alice AA', 'Unversity of Alice'], ['Bob BB', 'University of BB; Company of BB']]},
# In which the institute field is ';'.join(multiple_institutes) if there are multiple institutes. For authors with unknown institutes, use empty string "".\n''')
		
		f.write('paper_authors = [\n')
		for paper in paper_authors:
			# 转义标题中的引号和其他特殊字符
			title_escaped = paper["title"].replace('"', '\\"')
			# 转义作者名和机构中的引号
			authors_escaped = []
			for author, institute in paper["authors"]:
				author_escaped = author.replace('"', '\\"')
				institute_escaped = institute.replace('"', '\\"')
				authors_escaped.append([author_escaped, institute_escaped])
			f.write(f'    {{"title": "{title_escaped}", "authors": {authors_escaped}}},\n')
		f.write(']\n')

def convert_institute_info():
	old_info_path = os.path.join(os.path.dirname(__file__), '../data/locations_manual.txt')
	# 里面的每一行类似于
	# "Aalborg University 🇩🇰": {'lat': 57.0298, 'lon': 9.9207, 'country': 'Denmark'},
	# 除了lat、lon、country，可能还有一些其他的key。
	old_info_dict = {}
	with open(old_info_path, 'r', encoding='utf-8') as f:
		lines = f.readlines()
		for line in lines:
			line = line.strip()
			if not line or line.startswith('#'):
				continue
			# 使用正则表达式提取机构名称和信息字典
			match = re.match(r'"(.+?)":\s*(\{.+\}),?', line)
			if match:
				institute_name = match.group(1)
				info_str = match.group(2)
				try:
					info_dict = eval(info_str)  # 小心使用eval，确保输入可信
					old_info_dict[institute_name] = info_dict
				except Exception as e:
					print(f"Error parsing line: {line}\n{e}")
					continue
	# 生成新的institute_info.py
	new_info_path = os.path.join(os.path.dirname(__file__), '../data/institute_info.py')

	# 只对get_inst_name.values()中的机构NEW_NAME进行处理；在old_info_dict.keys()里找到一个key OLD_KEY，使得OLD_KEY包含NEW_NAME。
	new_info_dict = {}
	for new_name in set(get_inst_name.values()):
		found = False
		for old_key in old_info_dict.keys():
			if new_name in old_key:
				found = True
				info = old_info_dict[old_key]
				# 只保留lat, lon, country字段
				info = {k: v for k, v in info.items() if k in ['lat', 'lon', 'country']}
				new_info_dict[new_name] = info
				break
		if not found:
			print(f"Warning: Could not find institute info for '{new_name}' in old data.")
	# 写入新的institute_info.py
	with open(new_info_path, 'w', encoding='utf-8') as f:
		f.write('# Institute information including latitude, longitude, country, etc.\n')
		f.write('# Original data source is based on LLMs: please fix manually if there are errors.\n')
		f.write('institute_info = {\n')
		for inst_name, info in new_info_dict.items():
			inst_name_escaped = inst_name.replace('"', '\\"')
			f.write(f'    "{inst_name_escaped}": {info},\n')
		f.write('}\n')

def convert_research_groups():
	# Data source: data/neuropac.json
	with open(os.path.join(os.path.dirname(__file__), '../data/neuropac.json'), 'r', encoding='utf-8') as f:
		data = json.load(f)
	new_data = []
	for group in data:
		new_group = {
			"lat": group.get("latitude", None),
			"lon": group.get("longitude", None),
			"group_name": group["properties"].get("Group", ""),
			"institute": group["properties"].get("Organisation", ""),
			"image_url": group["properties"].get("Image URL", None),
			"url": group["properties"].get("URL", None),
			"country": group["properties"].get("Country", None),
			"city": group["properties"].get("City", None),
			"focus": group["properties"].get("Focus", None),
			"purpose": group["properties"].get("Purpose", None),
		}
		# Pop all keys that have value None
		new_group = {k: v for k, v in new_group.items() if v is not None}
		new_data.append(new_group)

	# Write new_data list to data/research_groups.py
	py_path = os.path.join(os.path.dirname(__file__), '../data/research_groups.py')
	with open(py_path, 'w', encoding='utf-8') as f:
		f.write('# Research group information.\n')
		f.write('research_groups = [\n')
		for group in new_data:
			f.write(f'    {group},\n')
		f.write(']\n')

if __name__ == "__main__":
    #convert_paper_list()
	#convert_paper_authors()
	#convert_institute_info()
	convert_research_groups()