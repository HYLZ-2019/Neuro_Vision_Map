# This get_authors method searches for the arxiv paper, gets the first page of the pdf, and extracts authors from there.

import requests
import json
import re
from secrets import API_KEY

import os
# Our official coze sdk for Python [cozepy](https://github.com/coze-dev/coze-py)
from cozepy import COZE_CN_BASE_URL
coze_api_base = COZE_CN_BASE_URL
from cozepy import Coze, TokenAuth, Stream, WorkflowEvent, WorkflowEventType  # noqa
from scripts.get_paper_list import get_new_paper_list

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=API_KEY), base_url=coze_api_base)

def handle_workflow_iterator(workflow_id, stream: Stream[WorkflowEvent]):
	for event in stream:
		if event.event == WorkflowEventType.MESSAGE:
			return event.message.content
		elif event.event == WorkflowEventType.ERROR:
			print("got error", event.error)
			raise Exception(event.error.message)
		elif event.event == WorkflowEventType.INTERRUPT:
			return handle_workflow_iterator(
				workflow_id,
				coze.workflows.runs.resume(
					workflow_id=workflow_id,
					event_id=event.interrupt.interrupt_data.event_id,
					resume_data="hey",
					interrupt_type=event.interrupt.interrupt_data.type,
				)
			)


def get_authors(paper_title):
	"""
	输入论文题目，返回作者列表。
	作者列表格式：[("作者名", "单位", "其他信息"), ...]
	"""
	workflow_id = '7540237429899411494'
	stream = coze.workflows.runs.stream(
		workflow_id=workflow_id,
		parameters={
			"CONVERSATION_NAME": "Default",
			"USER_INPUT": paper_title
		}
	)
	result = handle_workflow_iterator(workflow_id, stream)
	# 返回的东西是一个字符串，类似于：
	# [("Shuang Guo", "Dept. of Electrical Engineering and Computer Science, Technische Universität Berlin; Robotics Institute Germany, Berlin, Germany", "unknown"), ("Guillermo Gallego", "Dept. of Electrical Engineering and Computer Science, Technische Universität Berlin; Robotics Institute Germany, Berlin, Germany; Science of Intelligence (SCIoI) Excellence Cluster; Einstein Center Digital Future (ECDF), Berlin, Germany", "unknown")]
	return result

def get_and_log_lines(paper_list):
	author_log_file = "raw/got_authors.txt"
	# 每一行里是：{"paper_title": ..., "authors": [...]}	
	# 先读取author_log_file，把已经查到的paper_title从paper_list里去掉。
	# 每查询一个paper_title，往author_log_file里面append一行。
	if os.path.exists(author_log_file):
		with open(author_log_file, "r", encoding="utf-8") as f:
			logged_titles = set()
			for line in f:
				try:
					entry = json.loads(line.strip())
					logged_titles.add(entry["paper_title"])
				except:
					continue
		paper_list = [p for p in paper_list if p[1] not in logged_titles]
	with open(author_log_file, "a", encoding="utf-8") as f:
		for source, title, c_or_j in paper_list:
			try:
				authors_str = get_authors(title)
				entry = {
					"paper_title": title,
					"authors": authors_str
				}
				out_str = json.dumps(entry, ensure_ascii=False) + "\n"
				f.write(out_str)
				print(out_str)
			except Exception as e:
				print(f"Error getting authors for paper: {title}, error: {e}")


# 示例用法
if __name__ == "__main__":
	new_papers = get_new_paper_list()
	print(f"Found {len(new_papers)} new papers.")
	get_and_log_lines(new_papers)