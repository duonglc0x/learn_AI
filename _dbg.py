import json, sys
sys.stdout.reconfigure(encoding='utf-8')
nb = json.load(open(r'f:\AI\BT.ipynb', encoding='utf-8'))
ncells = len(nb['cells'])
print(f'Total cells: {ncells}')
for i, c in enumerate(nb['cells']):
    nlines = len(c['source'])
    print(f'Cell {i}: type={c["cell_type"]}, lines={nlines}')
    # Check first few chars
    src_preview = ''.join(c['source'][:3])[:100]
    print(f'  Preview: {repr(src_preview)}')
