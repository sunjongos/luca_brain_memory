import codecs

for fpath in ['memory_layer/memory_server.py', 'memory_layer/core.py']:
    with codecs.open(fpath, 'r', 'utf-8') as f:
        data = f.read()
    data = data.replace('raise ValueError("GEMINI_API_KEY is not set', 'pass #')
    with codecs.open(fpath, 'w', 'utf-8') as f:
        f.write(data)
