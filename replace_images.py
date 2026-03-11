import os
import glob
import re
import random

html_files = glob.glob('d:/Camera/LensCraft/*.html')
new_images = [
    'images/vinod1.jpg',
    'images/vinod2.jpg',
    'images/vinod3.jpg',
    'images/vinod4.jpg',
    'images/vinod5.jpg'
]

# Regex to find image sources that are external (http/https)
img_src_regex = re.compile(r'src="https?://[^"]+"')
url_regex = re.compile(r'url\([\'"]?https?://[^\'")]+[\'"]?\)')

for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace src="..."
    def src_replacer(match):
        return f'src="{random.choice(new_images)}"'
    content = img_src_regex.sub(src_replacer, content)
    
    # Replace url("...") for background images
    def url_replacer(match):
        return f'url("{random.choice(new_images)}")'
    content = url_regex.sub(url_replacer, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Images replaced.")
