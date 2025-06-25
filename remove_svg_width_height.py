import os
import re

folder = 'static/cards'
for fname in os.listdir(folder):
    if fname.endswith('.svg'):
        path = os.path.join(folder, fname)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Hapus width dan height hanya pada tag <svg ...>
        content_new = re.sub(r'(<svg[^>]*?)\swidth="[^"]*"', r'\1', content)
        content_new = re.sub(r'(<svg[^>]*?)\sheight="[^"]*"', r'\1', content_new)
        if content != content_new:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content_new)
print('Selesai menghapus width/height di semua SVG.') 