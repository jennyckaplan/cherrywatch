import requests
from enum import Enum
import re
import json
from bs4 import BeautifulSoup

class BloomStage(Enum):
  prebloom = "Prebloom"
  first_bloom = "First Bloom"
  peak_bloom = "Peak Bloom"
  post_peak_bloom = "Post-Peak Bloom"

URL = "https://www.bbg.org/collections/cherries"
page = requests.get(URL)

soup = BeautifulSoup(page.text, "html.parser")
raw_html = soup.prettify()

# TODO: save the raw_html for each day

# TODO: save the image of map

script_with_tree_data = soup.find_all("script")[1].string.strip()

pattern = re.compile("var prunuses = ([\s\S]*);", re.MULTILINE)

prunuses = re.match(pattern, script_with_tree_data)
prunuses = prunuses.group(1)

# remove trailing comma
prunuses = re.sub(",[ \t\r\n]+\]", "]", prunuses)

prunuses = json.loads(prunuses)

bloom_stage_count = {
  BloomStage.prebloom.value: 0,
  BloomStage.first_bloom.value: 0,
  BloomStage.peak_bloom.value: 0,
  BloomStage.post_peak_bloom.value: 0,
}

tree_count = len(prunuses)
print(f"There are {tree_count} cherry blossom trees at the Brooklyn Botanic Garden")
print("Today,")

for tree in prunuses:
    bloom_stage = tree[7]
    bloom_stage_count[bloom_stage] += 1

# TODO: save bloom stage count for each day
    
def get_percentage(stage: BloomStage) -> float:
    return round(bloom_stage_count[stage.value] / tree_count, 4)

def get_formatted_percentage(stage: BloomStage) -> str:
    percentage = get_percentage(stage)
    return f"{percentage * 100}%"

for stage in BloomStage:
    percentage = get_formatted_percentage(stage)
    print(f"{percentage} are at {stage.value}")
