import os
import glob

files_to_update = glob.glob('d:/Camera/LensCraft/*.html')
files_to_update.append('d:/Camera/LensCraft/js/main.js')

for filepath in files_to_update:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace cases
    content = content.replace('LensCraft Photography', 'Vinod Photography')
    content = content.replace('LensCraft', 'Vinod')
    content = content.replace('lenscraft.com', 'vinodphotography.com')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Renaming complete.")
