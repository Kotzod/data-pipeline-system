import xml.etree.ElementTree as ET
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FILE = BASE_DIR / "data.xml"

tree = ET.parse(FILE)
root = tree.getroot()
channel = root.find("channel")

items = channel.findall('item')

text = []

for item in items:
    title = item.findtext('name')
    date = item.findtext('pubDate')
    description = item.findtext('description')
    summary_line = f'{title} published on {date}: {description}'
    text.append(summary_line)
    print(summary_line)