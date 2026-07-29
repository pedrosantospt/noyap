```python
from urllib import request

def fetch_json(url, timeout=5):
    with request.urlopen(url, timeout=timeout) as response:
        return response.read().decode("utf-8")
```

Stdlib timeout covers the hang; add custom error mapping only if callers need it.
