import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request

def download(item):
    path = Path('data/raw') / item['name']
    urllib.request.urlretrieve(item['url'], path)
    return dict(key=item['key'], name=item['name'], path=str(path), source=item['source'],
                bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest())

if __name__ == '__main__':
    request_file = Path('data/download_requests.private.json')
    items = json.loads(request_file.read_text(encoding='utf-8-sig'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(download, items))
    Path('outputs/fase1/manifesto.json').write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
    request_file.unlink()
    for item in results:
        print(item['key'], item['bytes'], item['sha256'])
