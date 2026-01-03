import http.client
import json
import urllib.request
import os
import tqdm
from time import sleep
from scripts.get_paper_list import get_raw_paper_list
from secrets import METASO_API_KEY
from secrets import SEMANTIC_SCHOLAR_API_KEY
import requests
import concurrent.futures

def isascii(c):
	return 0 <= ord(c) <= 127

def get_doi_from_title_metaso(paper_title):
	conn = http.client.HTTPSConnection("metaso.cn")
	payload = json.dumps({"q": paper_title, "scope": "scholar", "includeSummary": False, "size": "1", "conciseSnippet": False})
	headers = {
	'Authorization': f'Bearer {METASO_API_KEY}',
	'Accept': 'application/json',
	'Content-Type': 'application/json'
	}
	conn.request("POST", "/api/v1/search", payload, headers)
	res = conn.getresponse()
	data = res.read()
	doi_link = json.loads(data.decode("utf-8"))["scholars"][0]["link"]
	return doi_link
	# The results is:
	# {"credits":3,"searchParameters":{"q":"all-in-focus imaging from event focal stacks","scope":"scholar","size":1,"searchFile":false,"includeSummary":false,"conciseSnippet":false,"format":"chat_completions"},"scholars":[{"title":"All-in-Focus Imaging from Event Focal Stack","link":"https://doi.org/10.1109/CVPR52729.2023.01666","score":"high","snippet":"Traditional focal stack methods require multiple shots ... show superior performance over state-of-the-art methods.","position":1,"authors":["Hanyue Lou","Minggui Teng","Yixin Yang","Boxin Shi"],"date":"2023-06-01"}],"total":87}

def get_doi_from_title_semantic(paper_title):
	rsp = requests.get(
		'https://api.semanticscholar.org/graph/v1/paper/search/match', 
		headers = {'X-API-KEY': SEMANTIC_SCHOLAR_API_KEY},
		params=
		{'query': paper_title})
	rsp.raise_for_status()
	results = rsp.json()
	#print(results)
	# results: {'data': [{'paperId': 'c290668633375f626f9ae229dee374f6ec9c2031', 'title': 'All-in-Focus Imaging from Event Focal Stack', 'matchScore': 229.76996}]}
	# Get the paperId for externalIds query
	paper_id = results['data'][0]['paperId']
	# Now get the full paper details including DOI
	sleep(1)

	rsp = requests.get(
		f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}', 
		headers = {'X-API-KEY': SEMANTIC_SCHOLAR_API_KEY},
		params=
		{'fields': 'title,authors,externalIds'}
	)
	rsp.raise_for_status()
	results = rsp.json()
	#print(results)
	# {'paperId': 'c290668633375f626f9ae229dee374f6ec9c2031', 'externalIds': {'DBLP': 'conf/cvpr/LouTYS23', 'DOI': '10.1109/CVPR52729.2023.01666', 'CorpusId': 261081657}, 'title': 'All-in-Focus Imaging from Event Focal Stack', 'authors': [{'authorId': '2190824470', 'name': 'Hanyue Lou'}, {'authorId': '1557343782', 'name': 'Minggui Teng'}, {'authorId': '153690258', 'name': 'Yixin Yang'}, {'authorId': '35580784', 'name': 'Boxin Shi'}]}
	# sleep(1) # Other part is slow enough
	return "https://doi.org/" + results['externalIds']['DOI']

def doi_to_html_text(doi_link):
	# Extract the doi link and get the corresponding page (will jump to the publisher site)
	# Use urllib to handle the full URL and follow redirects (DOI links usually redirect)
	# A User-Agent is often required to avoid being blocked by publisher sites
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'Accept-Language': 'en-US,en;q=0.9',
		'Connection': 'keep-alive',
		'Upgrade-Insecure-Requests': '1',
	}
	req = urllib.request.Request(doi_link, headers=headers)
	with urllib.request.urlopen(req) as response:
		data = response.read()

	return data.decode('utf-8', errors='ignore')

def get_authors_from_html(html_text):
	# 检查是否是ieeexplore.ieee.org
	# if "ieeexplore.ieee.org" not in html_text:
	# 	return {}
	
	# 先寻找类似于<link rel="canonical" href="https://ieeexplore.ieee.org/document/10203683/" />的部分，把这个href的链接提取出来
	canonical_index = html_text.find('<link rel="canonical" href="https://ieeexplore.ieee.org/document/')
	if canonical_index == -1:
		return {}
	start_index = canonical_index + len('<link rel="canonical" href="')
	end_index = html_text.find('"', start_index)
	canonical_link = html_text[start_index:end_index]

	# 然后尝试提取作者信息：
	# "authors":[{"name":"Hanyue Lou","affiliation":["National Key Laboratory for Multimedia Information Processing, School of Computer Science, Peking University","National Engineering Research Center of Visual Technology, School of Computer Science, Peking University"],"firstName":"Hanyue","lastName":"Lou","id":"37089951238"},{"name":"Minggui Teng","affiliation":["National Key Laboratory for Multimedia Information Processing, School of Computer Science, Peking University","National Engineering Research Center of Visual Technology, School of Computer Science, Peking University"],"firstName":"Minggui","lastName":"Teng","id":"37089156069"},{"name":"Yixin Yang","affiliation":["National Key Laboratory for Multimedia Information Processing, School of Computer Science, Peking University","National Engineering Research Center of Visual Technology, School of Computer Science, Peking University"],"firstName":"Yixin","lastName":"Yang","id":"37089320347"},{"name":"Boxin Shi","affiliation":["National Key Laboratory for Multimedia Information Processing, School of Computer Science, Peking University","National Engineering Research Center of Visual Technology, School of Computer Science, Peking University"],"firstName":"Boxin","lastName":"Shi","id":"37401831700"}],"isbn":[
	authors_data = []
	authors_index = html_text.find('"authors":[')
	isbn_index = html_text.find('],"isbn":[')
	issn_index = html_text.find('],"issn":[')
	# get the smaller one that is not -1
	end_idx = -1
	if isbn_index != -1 and issn_index != -1:
		end_idx = min(isbn_index, issn_index)
	elif isbn_index != -1:
		end_idx = isbn_index
	elif issn_index != -1:
		end_idx = issn_index
	
	if authors_index != -1 and end_idx != -1 and end_idx > authors_index:
		author_json_str = html_text[authors_index + len('"authors":'):end_idx + 1]
	else:
		return {"canonical_link": canonical_link}
	
	try:
		authors_list = json.loads(author_json_str)
		for author in authors_list:
			name = author.get("name", "")
			affiliations = author.get("affiliation", [])
			aff_clean = []
			for aff in affiliations:
				af = aff.strip()
				# Remove non-ascii characters at end. Some affiliations have extra "." or "," at the end.
				if not isascii(af[-1]):
					af = af[:-1]
				# If the string ends with " and", remove it
				if af.endswith(" and"):
					af = af[:-4].strip()
				aff_clean.append(af)
			institute = "; ".join(aff_clean) if aff_clean else ""
			authors_data.append([name, institute])
	except json.JSONDecodeError:
		return {"canonical_link": canonical_link}
	
	return {
		"canonical_link": canonical_link,
		"authors": authors_data
	}

def process_one_paper(t):
	print(t)
	info = {"title": t}
	try:
		doi_link = get_doi_from_title_semantic(t)
		info["doi_link"] = doi_link
		html_text = doi_to_html_text(doi_link)
		author_info = get_authors_from_html(html_text)
		info.update(author_info)
	except Exception as e:
		info["error"] = str(e)
	return info

def process_paper_list(paper_titles, raw_log_path="raw/ss_ieee_author_log.txt", skip_done=True):
	# 每完成一个，在txt里append一行，对应结果的json str。
	if skip_done and os.path.exists(raw_log_path):
		done_titles = set()
		with open(raw_log_path, 'r', encoding='utf-8') as f:
			for line in f:
				try:
					entry = json.loads(line.strip())
					if "title" in entry:
						done_titles.add(entry["title"])
				except json.JSONDecodeError:
					continue
		paper_titles = [title for title in paper_titles if title not in done_titles]
		if not paper_titles:
			print("All papers have been processed already.")
			return
		else:
			print(f"Processing {len(paper_titles)} new papers...")

	for title in tqdm.tqdm(paper_titles):
		# Use ThreadPoolExecutor to enforce a timeout
		# We create a new executor per iteration to ensure we don't get blocked by a hung thread
		executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
		future = executor.submit(process_one_paper, title)
		
		try:
			all_info = future.result(timeout=20)
		except concurrent.futures.TimeoutError:
			all_info = {"title": title, "error": "Timeout: Processing exceeded 20 seconds"}
		except Exception as e:
			all_info = {"title": title, "error": str(e)}
		
		# Shutdown without waiting for the potentially hung thread
		executor.shutdown(wait=False)

		with open(raw_log_path, 'a', encoding='utf-8') as f:
			results = json.dumps(all_info, ensure_ascii=False)
			f.write(results + '\n')
	
	return results

if __name__ == "__main__":
	raw_paper_list = get_raw_paper_list("raw/paper_list_2026_01_02.csv")
	paper_titles = [title for _, title, _ in raw_paper_list]
	process_paper_list(paper_titles)

	# html = doi_to_html_text("https://doi.org/10.1109/TMC.2024.3521044")
	# with open("raw/test_ieee.html", "w", encoding="utf-8") as f:
	# 	f.write(html)
	# a = get_authors_from_html(html)
	# print(a)

	#title = "all-in-focus imaging from event focal stacks"
	
	