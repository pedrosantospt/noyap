Timeout added. Failure readable.

```python
from urllib import error, request

def fetch_json(url, timeout=5):
    try:
        with request.urlopen(url, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except (TimeoutError, error.URLError) as exc:
        raise RuntimeError("api request failed") from exc
```
