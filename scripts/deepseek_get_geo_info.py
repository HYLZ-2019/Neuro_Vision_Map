import json
from openai import OpenAI
import tqdm
from secrets import DEEPSEEK_API_KEY
from data.institutes_alias_to_name import get_inst_name
from data.institute_info import institute_info

client = OpenAI(
	api_key=DEEPSEEK_API_KEY,
	base_url="https://api.deepseek.com",
)

def get_geo_info(inst_name, related_strings):
	system_prompt = """
	用户将给你提供一个机构的名称，以及与它相关的一些字符串（可能包含地理信息）。请你据此推断这一机构的国家与经纬度，输出一个json对象。例如，对于Peking University，输出：
	```
	{'lat': 39.9954, 'lon': 116.3138, 'country': 'China'}
	```
	"""

	user_prompt = f"机构名称：'{inst_name}'，相关字符串：{related_strings}"

	messages = [{"role": "system", "content": system_prompt},
				{"role": "user", "content": user_prompt}]

	response = client.chat.completions.create(
		model="deepseek-chat",
		messages=messages,
		response_format={
			'type': 'json_object'
		}
	)

	return json.loads(response.choices[0].message.content)

def query_all():
	all_mapped_insts = set(get_inst_name.values())
	done_insts = set(institute_info.keys())
	insts_to_query = sorted(list(all_mapped_insts - done_insts))

	for inst in tqdm.tqdm(insts_to_query):
		related_strings = [alias for alias, std_name in get_inst_name.items() if std_name == inst]
		try:
			geo_info = get_geo_info(inst, related_strings)
			with open('raw/deepseek_geo_info_log.txt', 'a', encoding='utf-8') as f:
				# Print a line like 'Korea Advanced Institute of Science and Technology (KAIST)': {'lat': 36.3794, 'lon': 127.3626, 'country': 'South Korea'},
				f.write(f"'{inst}': {geo_info},\n")
		except:
			print(f"Error querying geo info for institute: {inst}")


if __name__ == "__main__":
	query_all()