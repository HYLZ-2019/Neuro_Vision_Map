# Neuromorphic Vision Papers and Where to Find Them

This project visualizes the locations of all institutes that have published neuromorphic vision papers, showing growing international participation and collaboration. Click the link below to view:

https://hylz-2019.github.io/Neuro_Vision_Map/map.html

An interactive bar chart showing the number of papers published by different conferences/journals over the years is also available:

https://hylz-2019.github.io/Neuro_Vision_Map/bar.html

All data is collected from public sources. Feel free to include the graphs in your PPTs and reports!

You might have noticed that some information is missing or incorrect. It would be great if you could help improve the project by contributing to this repository. I will first explain how the project works, and then give some Q&As on how to contribute.

## How this works

All source data is in `data/*.py`.

1. `data/paper_list.py`: 

	This is the original list of papers, including source (e.g. CVPR 2025), title and type (conference/journal/book). The data was initially sourced from [Recent papers on Event-based Vision](https://docs.google.com/spreadsheets/d/1_OBbSz10CkxXNDHQd-Mn_ui3OmymMFvm-lW316uvxy8/edit?gid=0#gid=0).

2. `data/paper_authors.py`: 

	This file contains the author lists of papers. Each author is represented as `[{name}, {affiliation}]`. When there are multiple affiliations, they should be concated with `;`, e.g. `["Author A", "University X; Company Y"]`. 
	
	The source of most author names is the arXiv API or the Semantic Scholar API. For papers available on arXiv, I used an LLM to extract the affiliations from the first page of the PDF. Hence, many authors have affiliation strings missing or messy.

3. `data/institutes_alias_to_name.py`:

	The affiliation strings in `data/paper_authors.py` are diverse. For example, a person's affiliation may be "Peking University", "State Key Lab of Multimedia Info. Processing, School of Computer Science, Peking University" or "Peking University, Beijing, China" in different papers. 

	Hence, we use this file to map original affiliation strings to a standard institute name, such as "Peking University". For example, an item `"State Key Lab of Multimedia Info. Processing, School of Computer Science, Peking University": "Peking University"` means that all "State Key..."s should be considered as "Peking University".

	The draft of the file was generated with LLMs, and manual corrections were made.

4. `data/institute_info.py`:

	This file contains the latitude, longitude and country of each institute. The keys in the file are standard institute names generated from the previous step, and the values were also drafted by an LLM agent equipped with map tools.

5. `data/research_groups.py`:

	This file contains information about research groups, with data sourced from [NeuroPAC](https://www.neuropac.info/resources-3/map/). An institute may correspond to multiple research groups. When clicking on an institute on the map, all research groups with `institute={institute_standard_name}` should be listed in the popup.

By running `python compile_map.py`, all data will be injected to the template, and a file `result_map.html` will be generated. It is a static HTML file and can be opened in any browser.

Powered by Github Actions, whenever something new is pushed to the `main` branch, `compile_map.py` will be run automatically, and the new `result_map.html` will be deployed to [https://hylz-2019.github.io/Neuro_Vision_Map/](https://hylz-2019.github.io/Neuro_Vision_Map/).

## How to contribute

If you would like to contribute, edit the `data/*.py` files and submit a pull request. A github action will automatically run a compilation check. If the check passes, I will review and merge your PR, and the new map will be deployed automatically.

**Q. I want to add a new paper to the database.**

	Add the paper to `data/paper_list.py`, and add the author list to `data/paper_authors.py`. Ensure that the author affiliations are standard institute names, or can be mapped to standard names by `data/institutes_alias_to_name.py`.

**Q. There are duplications of the same institute with different names.**

	Edit `data/institutes_alias_to_name.py` to map them to the same name.

**Q. The location of an institute is wrong.**
	
	To prevent dots from lapping over each other, I wrote a simple algorithm in the map to randomly shift each dot.

	If the location error is so large that it cannot be explained by the random shift algorithm, please edit `data/institute_info.py` to correct the latitude and longitude.

**Q. I want to add a research group.**

	Please edit `data/research_groups.py` to add the group.