Added timeout.
Not run.
Risk: callers still receive raw `URLError`.

```python
from urllib import request

def fetch_json(url, timeout=5):
    with request.urlopen(url, timeout=timeout) as response:
        return response.read().decode("utf-8")
```
